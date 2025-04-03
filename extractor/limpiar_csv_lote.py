import pandas as pd
import glob
import os
import sys
import codecs

# Configura la salida estándar para que acepte caracteres UTF-8
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach(), "replace")

# 📂 Definir la carpeta base con una ruta absoluta
carpeta_base = r"C:\Users\Usuario\PycharmProjects\CSVExtractorProyect\inputs"

# 🔍 Buscar todos los archivos .csv en la carpeta inputs
archivos_encontrados = glob.glob(os.path.join(carpeta_base, "*.csv"))

# 📌 Columnas a eliminar
columnas_a_eliminar = [
    "is_spending_on_ads",
    "can_claim",
    "owner_name",
    "owner_profile_link",
    "is_temporarily_closed",
    "query"
]

# Verificar si hay archivos en la carpeta
if not archivos_encontrados:
    print(f"❌ No se encontraron archivos CSV en la carpeta: {carpeta_base}")
else:
    # 📂 Definir carpeta de salida con ruta absoluta
    carpeta_salida = r"C:\Users\Usuario\PycharmProjects\CSVExtractorProyect\clean_inputs"
    os.makedirs(carpeta_salida, exist_ok=True)

    for archivo in archivos_encontrados:
        try:
            df = pd.read_csv(archivo, encoding="utf-8", sep=",")  # Asegurar formato correcto

            # 📌 Mostrar columnas reales en el CSV
            print(f"Columnas en {os.path.basename(archivo)}: {df.columns.tolist()}")

            # 🗑️ Verificar y eliminar columnas si existen
            columnas_encontradas = [col for col in columnas_a_eliminar if col in df.columns]
            print(f"Columnas a eliminar en {os.path.basename(archivo)}: {columnas_encontradas}")

            if columnas_encontradas:
                df.drop(columns=columnas_encontradas, inplace=True)
            else:
                print(f"No se encontraron columnas para eliminar en {os.path.basename(archivo)}")

            # 💾 Guardar el archivo limpio en clean_inputs
            archivo_salida = os.path.join(carpeta_salida, os.path.basename(archivo))
            df.to_csv(archivo_salida, index=False, encoding="utf-8")

            print(f"Archivo limpiado y guardado: {archivo_salida}")

        except Exception as e:
            print(f"Error al procesar {os.path.basename(archivo)}: {e}")
