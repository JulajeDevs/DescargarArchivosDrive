import os
import pandas as pd
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
import io
import re
from datetime import datetime

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'service-account.json')
PARENT_FOLDER_ID = '1fGGv0uGqpkdVy8xs7g0hoPvnUvIyXo2M'  # Carpeta SIRAS

INPUT_FILE = os.path.join(BASE_DIR, 'datos.xlsx')
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'Descargados')
LOG_FILE = os.path.join(BASE_DIR, f'log_proceso_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Cache en memoria para acelerar procesos
FOLDER_CACHE = {}
SEARCH_CACHE = {}

def authenticate_drive():
    """Autentica y devuelve el servicio de Drive."""
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    return build('drive', 'v3', credentials=creds)

def search_file_cached(service, filename):
    """Búsqueda optimizada con cache para no repetir queries."""
    if filename in SEARCH_CACHE:
        return SEARCH_CACHE[filename]

    escaped_name = filename.replace("'", "\\'")

    query = f"name = '{escaped_name}' and trashed = false"

    try:
        results = service.files().list(
            q=query,
            fields="files(id, name, mimeType, parents)",
            pageSize=5
        ).execute()

        files = results.get('files', [])

        if not files:
            query = f"name contains '{escaped_name}' and trashed = false"
            results = service.files().list(
                q=query,
                fields="files(id, name, mimeType, parents)",
                pageSize=5
            ).execute()
            files = results.get('files', [])

        files = [f for f in files if f['mimeType'] != 'application/vnd.google-apps.folder']
        SEARCH_CACHE[filename] = files[0] if files else None
        return SEARCH_CACHE[filename]

    except:
        SEARCH_CACHE[filename] = None
        return None

def get_folder_path(service, file_info):
    """Devuelve la ruta de carpetas usando cache."""
    parents = file_info.get("parents", [])
    if not parents:
        return ["Raiz"]

    folder_id = parents[0]

    if folder_id in FOLDER_CACHE:
        return FOLDER_CACHE[folder_id]

    path = []
    current_id = folder_id

    while current_id:
        try:
            folder = service.files().get(
                fileId=current_id, fields='name, parents'
            ).execute()

            name = folder.get("name")
            path.insert(0, name)

            pr = folder.get("parents", [])
            current_id = pr[0] if pr else None

        except:
            break

    FOLDER_CACHE[folder_id] = path
    return path

def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()[:200]

def download_file(service, file_id, original_filename, destination_folder, new_name_prefix):
    """Descarga rápida sin prints ni pausas."""
    _, ext = os.path.splitext(original_filename)
    if not ext:
        ext = ".pdf"

    final_file = f"{new_name_prefix}{ext}"
    path = os.path.join(destination_folder, final_file)

    try:
        if os.path.exists(path):
            final_file = f"{new_name_prefix}_{datetime.now().strftime('%H%M%S')}{ext}"
            path = os.path.join(destination_folder, final_file)

        request = service.files().get_media(fileId=file_id)

        with io.FileIO(path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

        return final_file, True

    except:
        return None, False

def main():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        encoding="utf-8"
    )

    print("🔐 Autenticando con Google Drive...")
    service = authenticate_drive()
    print("✅ Listo\n")

    print(f"📄 Leyendo archivo de datos...")
    df = pd.read_excel(INPUT_FILE)

    total = len(df)
    print(f"📌 Registros a procesar: {total}\n")

    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    resultados = []
    encontrados = descargados = no_encontrados = errores = 0

    for i, row in df.iterrows():
        caso = str(row["Caso"]).replace(".0", "")
        radicado = str(row["RadicadoEnvio"]).strip()

        print(f"[{i+1}/{total}] 🔍 {radicado}")

        try:
            info = search_file_cached(service, radicado)

            if not info:
                no_encontrados += 1
                print("   ❌ NO ENCONTRADO")
                continue

            encontrados += 1
            file_name = info["name"]
            file_id = info["id"]

            folder_path = get_folder_path(service, info)
            safe = [sanitize_filename(x) for x in folder_path]
            local = os.path.join(DOWNLOAD_DIR, *safe)

            os.makedirs(local, exist_ok=True)

            saved_file, success = download_file(
                service, file_id, file_name, local, caso
            )

            if success:
                descargados += 1
                print("   💾 Descargado")
            else:
                errores += 1
                print("   ⚠️ Error de descarga")

        except Exception as e:
            errores += 1
            print(f"⚠️ Error: {e}")

    print("\n📊 PROCESO FINALIZADO")
    print(f"📌 Total: {total}")
    print(f"🔎 Encontrados: {encontrados}")
    print(f"💾 Descargados: {descargados}")
    print(f"❌ No encontrados: {no_encontrados}")
    print(f"⚠️ Errores: {errores}")

if __name__ == "__main__":
    main()
