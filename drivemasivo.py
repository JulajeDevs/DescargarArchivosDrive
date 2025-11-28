import os
import pandas as pd
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import re

# --- CONFIGURACIÓN ---

# Construimos la ruta absoluta para evitar errores
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'service-account.json')

# ID de la carpeta principal (Referencia)
PARENT_FOLDER_ID = '1fGGv0uGqpkdVy8xs7g0hoPvnUvIyXo2M'

# Archivos de entrada y salida
INPUT_FILE = os.path.join(BASE_DIR, 'datos.xlsx')
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'Descargados')
LOG_FILE = os.path.join(BASE_DIR, 'log_proceso.txt')

# Scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate_drive():
    """Autentica y devuelve el servicio de la API de Drive."""
    creds = None
    try:
        if not os.path.exists(CREDENTIALS_FILE):
            print(f"ERROR CRÍTICO: No se encuentra el archivo de credenciales en: {CREDENTIALS_FILE}")
            return None

        creds = service_account.Credentials.from_service_account_file(
                CREDENTIALS_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Error de autenticación: {e}")
        return None

def get_folder_name(service, folder_id):
    """Obtiene el nombre de una carpeta dado su ID."""
    try:
        file = service.files().get(fileId=folder_id, fields='name').execute()
        return file.get('name', 'Desconocido')
    except Exception:
        return "Sin_Carpeta"

def sanitize_name(name):
    """Limpia el nombre de la carpeta para que sea válido en Windows."""
    # Reemplaza caracteres inválidos con guion bajo
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()

def search_file(service, search_term):
    """
    Busca un archivo por nombre (RadicadoEnvio) y retorna ID, Nombre y ID del Padre.
    """
    safe_search_term = search_term.replace("'", "\\'")
    query = f"name contains '{safe_search_term}' and trashed = false"
    
    try:
        # Solicitamos también los 'parents' para saber en qué carpeta está
        results = service.files().list(
            q=query,
            fields="files(id, name, parents)",
            pageSize=1
        ).execute()
        
        files = results.get('files', [])
        return files[0] if files else None
    except Exception as e:
        logging.error(f"Error buscando '{search_term}': {e}")
        return None

def download_file(service, file_id, original_file_name, destination_folder, new_name_prefix):
    """Descarga el archivo en la carpeta específica."""
    
    # Determinar extensión original
    _, extension = os.path.splitext(original_file_name)
    if not extension:
        extension = "" 

    # Nombre final: NumeroDeCaso.extension
    final_filename = f"{new_name_prefix}{extension}"
    file_path = os.path.join(destination_folder, final_filename)

    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(file_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        return final_filename
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise e

def main():
    # 1. Configurar Logging
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                        format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    # 2. Crear carpeta base de descargas
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    # 3. Leer Excel
    print(f"Leyendo archivo de datos: {INPUT_FILE}")
    try:
        if INPUT_FILE.endswith('.csv'):
            df = pd.read_csv(INPUT_FILE)
        else:
            df = pd.read_excel(INPUT_FILE, engine='openpyxl')
    except Exception as e:
        print(f"Error leyendo archivo: {e}")
        return

    if 'Caso' not in df.columns or 'RadicadoEnvio' not in df.columns:
        print("Error: Columnas 'Caso' y 'RadicadoEnvio' son requeridas.")
        return

    # 4. Autenticar
    service = authenticate_drive()
    if not service:
        return

    print("\n--- Iniciando Proceso Organizado ---")
    total_casos = len(df)
    procesados = 0
    exitos = 0

    for index, row in df.iterrows():
        case_number = str(row['Caso']).strip().replace('.0', '')
        radicado_envio = str(row['RadicadoEnvio']).strip()
        
        if not radicado_envio or radicado_envio.lower() == 'nan' or not case_number:
            continue

        print(f"[{procesados + 1}/{total_casos}] Buscando: {radicado_envio} (Caso {case_number})...")
        
        try:
            # 1. BUSCAR
            found_file = search_file(service, radicado_envio)
            
            if found_file:
                file_id = found_file['id']
                original_name = found_file['name']
                
                # 2. IDENTIFICAR CARPETA DE ORIGEN (IPS)
                parents = found_file.get('parents', [])
                if parents:
                    # Obtenemos el nombre de la carpeta padre (ej: "traumaoriente")
                    parent_folder_name = get_folder_name(service, parents[0])
                else:
                    parent_folder_name = "Sin_Carpeta_Padre"
                
                # Limpiamos el nombre para que sirva como carpeta en Windows
                safe_folder_name = sanitize_name(parent_folder_name)
                
                # 3. CREAR SUB-CARPETA LOCAL
                # Ruta será: Descargados/traumaoriente/
                specific_download_path = os.path.join(DOWNLOAD_DIR, safe_folder_name)
                
                if not os.path.exists(specific_download_path):
                    os.makedirs(specific_download_path)
                    print(f"   [+] Nueva carpeta creada: {safe_folder_name}")

                # 4. DESCARGAR en la sub-carpeta
                saved_name = download_file(service, file_id, original_name, specific_download_path, case_number)
                
                msg = f"EXITO: Guardado en '{safe_folder_name}/{saved_name}'"
                print(f"   L> {msg}")
                logging.info(f"Caso {case_number} ({radicado_envio}) -> {safe_folder_name}/{saved_name}")
                exitos += 1
            else:
                print(f"   L> No encontrado.")
                logging.warning(f"No encontrado: {radicado_envio} (Caso {case_number})")
                
        except Exception as e:
            print(f"   L> Error: {e}")
            logging.error(f"Error caso {case_number}: {e}")
        
        procesados += 1

    print("\n--- Finalizado ---")
    print(f"Archivos descargados exitosamente: {exitos}")

if __name__ == '__main__':
    main()