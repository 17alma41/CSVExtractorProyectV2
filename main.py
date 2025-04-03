import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from extractor.email_extractor import extract_emails_from_url
from extractor.social_extractor import extract_essential_social_links_from_url

INPUT_FOLDER = "inputs"
OUTPUT_FOLDER = "outputs"
DEMO_MODE = True  # Poner en true para aplicar la opción DEMO o ponerlo en false para ejecutarlo entero
MAX_WORKERS = 5 # Puedes subirlo según tu CPU/ChromeDriver

def procesar_sitio(row):
    website = row["website"]
    print(f"🔍 Procesando {website}")
    emails = extract_emails_from_url(website)
    # redes = extract_essential_social_links_from_url(website)

    return {
        **row,
        "emails": ", ".join(emails),
        # "facebook": ", ".join(redes.get("facebook", [])),
        # "instagram": ", ".join(redes.get("instagram", [])),
        # "linkedin": ", ".join(redes.get("linkedin", [])),
        # "twitter": ", ".join(redes.get("twitter", []))
    }

def procesar_archivo(nombre_archivo, demo_mode=False):
    path_entrada = os.path.join(INPUT_FOLDER, nombre_archivo)
    df = pd.read_csv(path_entrada)

    if "website" not in df.columns:
        print(f"❌ El archivo {nombre_archivo} no contiene columna 'website'")
        return

    if demo_mode:
        df = df.head(20)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        resultados = list(executor.map(procesar_sitio, [row for _, row in df.iterrows()]))

    df_resultado = pd.DataFrame(resultados)
    output_path = os.path.join(OUTPUT_FOLDER, f"emails_{nombre_archivo}")
    df_resultado.to_csv(output_path, index=False)
    print(f"✅ Datos guardados en {output_path}")

if __name__ == "__main__":
    for archivo in os.listdir(INPUT_FOLDER):
        if archivo.endswith(".csv"):
            procesar_archivo(archivo, demo_mode=DEMO_MODE)
