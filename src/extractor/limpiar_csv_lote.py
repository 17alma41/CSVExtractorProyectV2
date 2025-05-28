import pandas as pd
import glob
import os
import sys
import codecs
from pathlib import Path

def main():
    # Configura la salida estándar para que acepte caracteres UTF-8
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach(), "replace")

    # 📂 Definir la carpeta base y de salida usando rutas relativas al proyecto
    BASE_DIR = Path(__file__).resolve().parent.parent
    sys.path.append(str(BASE_DIR))
    from src.settings import INPUTS_DIR, CLEAN_INPUTS_DIR
    carpeta_base = INPUTS_DIR
    carpeta_salida = CLEAN_INPUTS_DIR
    os.makedirs(carpeta_salida, exist_ok=True)

    print(f"[DEBUG] BASE_DIR: {BASE_DIR}")
    print(f"[DEBUG] carpeta_base: {carpeta_base}")
    print(f"[DEBUG] carpeta_salida: {carpeta_salida}")

    # 📌 Columnas a eliminar
    columnas_a_eliminar = [
        "is_spending_on_ads",
        "can_claim",
        "owner_name",
        "owner_profile_link",
        "is_temporarily_closed",
        "query"
    ]

    # 🔍 Buscar todos los archivos .csv en la carpeta inputs
    glob_pattern = str(carpeta_base / "*.csv")
    print(f"[DEBUG] glob pattern: {glob_pattern}")
    print(f"[DEBUG] Archivos en carpeta_base (os.listdir): {os.listdir(carpeta_base)}")
    archivos_encontrados = glob.glob(glob_pattern)
    print(f"[DEBUG] Archivos encontrados: {archivos_encontrados}")

    # Verificar si hay archivos en la carpeta
    if not archivos_encontrados:
        print(f"❌ No se encontraron archivos CSV en la carpeta: {carpeta_base}")
    else:
        for archivo in archivos_encontrados:
            try:
                df = pd.read_csv(archivo, encoding="utf-8", sep=",")

                print(f"Columnas en {os.path.basename(archivo)}: {df.columns.tolist()}")
                columnas_encontradas = [col for col in columnas_a_eliminar if col in df.columns]
                print(f"Columnas a eliminar: {columnas_encontradas}")

                if columnas_encontradas:
                    df.drop(columns=columnas_encontradas, inplace=True)

                archivo_salida = carpeta_salida / os.path.basename(archivo)
                df.to_csv(archivo_salida, index=False, encoding="utf-8")

                print(f"✅ Archivo limpio guardado: {archivo_salida}")

            except Exception as e:
                print(f"❌ Error al procesar {os.path.basename(archivo)}: {e}")

if __name__ == "__main__":
    main()
