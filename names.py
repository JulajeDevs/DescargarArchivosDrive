import os

# Ruta proporcionada
ruta = r"C:\Users\kevin.yepes\Desktop\Web Scraping\plugins\SirasGeneroSolution\Descargados\WEBSCRAPING\SIRAS\CMVS"

# Verificar si la ruta existe
if os.path.exists(ruta):
    print(f"📁 Contenido de: {ruta}\n" + "="*60)
    
    # Recorrer todos los archivos en la ruta
    for archivo in os.listdir(ruta):
        # Crear la ruta completa
        ruta_completa = os.path.join(ruta, archivo)
        
        # Verificar si es un archivo (no directorio)
        if os.path.isfile(ruta_completa):
            # Obtener tamaño del archivo
            tamaño = os.path.getsize(ruta_completa)
            tamaño_kb = tamaño / 1024
            
            # Obtener fecha de modificación
            fecha_mod = os.path.getmtime(ruta_completa)
            from datetime import datetime
            fecha_str = datetime.fromtimestamp(fecha_mod).strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"📄 {archivo}")
            print(f"   Tamaño: {tamaño_kb:.2f} KB")
            print(f"   Modificado: {fecha_str}")
            print("-" * 40)
    
    # Versión alternativa: lista simple
    print("\n" + "="*60)
    print("📋 LISTA SIMPLE DE ARCHIVOS:")
    print("="*60)
    
    # Obtener solo archivos (excluyendo directorios)
    archivos = [f for f in os.listdir(ruta) if os.path.isfile(os.path.join(ruta, f))]
    
    for i, archivo in enumerate(archivos, 1):
        print(f"{i:3}. {archivo}")
    
    print(f"\nTotal de archivos encontrados: {len(archivos)}")
    
else:
    print(f"❌ La ruta no existe: {ruta}")
    print("Por favor, verifica la ruta e inténtalo de nuevo.")