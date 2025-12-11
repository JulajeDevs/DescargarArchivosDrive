import os
from datetime import datetime

# Ruta proporcionada
ruta = r"C:\Users\kevin.yepes\Desktop\Web Scraping\plugins\SirasGeneroSolution\Descargados\WEBSCRAPING\SIRAS\CMVS"

# Nombre del archivo de salida
archivo_salida = "procesados.txt"

# Abrir archivo para escribir
with open(archivo_salida, 'w', encoding='utf-8') as f:
    # Verificar si la ruta existe
    if os.path.exists(ruta):
        # Escribir encabezado en archivo
        f.write(f"📁 CONTENIDO DE LA CARPETA: {ruta}\n")
        f.write("="*70 + "\n\n")
        
        # Lista para almacenar archivos
        lista_archivos = []
        
        # Recorrer todos los archivos en la ruta
        for archivo in os.listdir(ruta):
            # Crear la ruta completa
            ruta_completa = os.path.join(ruta, archivo)
            
            # Verificar si es un archivo (no directorio)
            if os.path.isfile(ruta_completa):
                # Obtener información del archivo
                tamaño = os.path.getsize(ruta_completa)
                tamaño_kb = tamaño / 1024
                tamaño_mb = tamaño_kb / 1024
                
                # Obtener fecha de modificación
                fecha_mod = os.path.getmtime(ruta_completa)
                fecha_str = datetime.fromtimestamp(fecha_mod).strftime('%Y-%m-%d %H:%M:%S')
                
                # Obtener extensión del archivo
                nombre, extension = os.path.splitext(archivo)
                
                # Crear diccionario con información
                info_archivo = {
                    'nombre': archivo,
                    'ruta': ruta_completa,
                    'tamaño_bytes': tamaño,
                    'tamaño_kb': tamaño_kb,
                    'tamaño_mb': tamaño_mb,
                    'fecha_modificacion': fecha_str,
                    'extension': extension.upper() if extension else 'SIN EXTENSIÓN'
                }
                
                lista_archivos.append(info_archivo)
        
        # Escribir resumen
        f.write(f"📊 RESUMEN DE ARCHIVOS ENCONTRADOS:\n")
        f.write(f"Total de archivos: {len(lista_archivos)}\n")
        
        # Calcular tamaño total
        if lista_archivos:
            tamaño_total_bytes = sum(arch['tamaño_bytes'] for arch in lista_archivos)
            tamaño_total_mb = tamaño_total_bytes / (1024 * 1024)
            f.write(f"Tamaño total: {tamaño_total_mb:.2f} MB\n")
        
        f.write("\n" + "="*70 + "\n\n")
        
        # Escribir lista detallada de archivos
        f.write("📋 LISTA DETALLADA DE ARCHIVOS:\n")
        f.write("="*70 + "\n\n")
        
        for i, arch in enumerate(lista_archivos, 1):
            f.write(f"ARCHIVO {i}:\n")
            f.write(f"  Nombre: {arch['nombre']}\n")
            f.write(f"  Extensión: {arch['extension']}\n")
            f.write(f"  Tamaño: {arch['tamaño_bytes']:,} bytes ({arch['tamaño_kb']:.2f} KB / {arch['tamaño_mb']:.3f} MB)\n")
            f.write(f"  Fecha modificación: {arch['fecha_modificacion']}\n")
            f.write(f"  Ruta completa: {arch['ruta']}\n")
            f.write("-" * 60 + "\n\n")
        
        # Escribir lista simple (solo nombres)
        f.write("\n" + "="*70 + "\n")
        f.write("📄 LISTA SIMPLE DE ARCHIVOS (SOLO NOMBRES):\n")
        f.write("="*70 + "\n\n")
        
        for i, arch in enumerate(lista_archivos, 1):
            f.write(f"{i:3}. {arch['nombre']}\n")
        
        # Escribir resumen por extensiones
        f.write("\n" + "="*70 + "\n")
        f.write("📊 RESUMEN POR EXTENSIONES:\n")
        f.write("="*70 + "\n\n")
        
        extensiones = {}
        for arch in lista_archivos:
            ext = arch['extension']
            if ext in extensiones:
                extensiones[ext] += 1
            else:
                extensiones[ext] = 1
        
        for ext, cantidad in sorted(extensiones.items()):
            f.write(f"{ext}: {cantidad} archivo{'s' if cantidad != 1 else ''}\n")
        
        # Información de generación
        f.write("\n" + "="*70 + "\n")
        f.write(f"📝 INFORMACIÓN DEL REPORTE:\n")
        f.write("="*70 + "\n")
        f.write(f"Reporte generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Ruta analizada: {ruta}\n")
        f.write(f"Archivo generado: {os.path.abspath(archivo_salida)}\n")
        
        # Mostrar mensaje en consola
        print(f"✅ Reporte generado exitosamente!")
        print(f"📁 Archivos encontrados: {len(lista_archivos)}")
        print(f"💾 Reporte guardado en: {os.path.abspath(archivo_salida)}")
        
        # Mostrar vista previa en consola
        if lista_archivos:
            print("\n📋 Vista previa de archivos encontrados:")
            print("-" * 50)
            for i, arch in enumerate(lista_archivos[:10], 1):  # Mostrar solo primeros 10
                print(f"{i:3}. {arch['nombre']} ({arch['tamaño_kb']:.1f} KB)")
            
            if len(lista_archivos) > 10:
                print(f"... y {len(lista_archivos) - 10} archivos más")
        
    else:
        # Si la ruta no existe
        f.write(f"❌ ERROR: LA RUTA NO EXISTE\n")
        f.write("="*50 + "\n\n")
        f.write(f"Ruta especificada: {ruta}\n")
        f.write(f"Fecha del error: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\nPosibles soluciones:\n")
        f.write("1. Verificar que la ruta esté escrita correctamente\n")
        f.write("2. Comprobar que la carpeta exista\n")
        f.write("3. Verificar permisos de acceso\n")
        
        # Mostrar error en consola
        print(f"❌ Error: La ruta no existe")
        print(f"Ruta: {ruta}")
        print(f"El error se ha guardado en {archivo_salida}")

print("\n" + "="*50)
print("¡Proceso completado!")