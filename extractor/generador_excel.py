import pandas as pd
from pathlib import Path
from urllib.parse import urlparse

# Ruta base: suponiendo que este archivo está en extractor/
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FOLDER = BASE_DIR / "data" / "outputs"

def generar_excel(df_resultado, nombre_archivo):
    # --- Cálculo de métricas adicionales ---
    # 1) Número de dominios únicos en la columna 'website'
    if "website" in df_resultado.columns:
        domains = (
            df_resultado["website"]
            .dropna()
            .astype(str)
            .apply(lambda u: urlparse(u).netloc)
        )
        num_domains = domains.nunique()
    else:
        num_domains = 0

    # 2) Número total de enlaces a redes sociales (facebook, instagram, linkedin, x)
    social_cols = ["facebook", "instagram", "linkedin", "x"]
    num_socials = 0
    for col in social_cols:
        if col in df_resultado.columns:
            counts = (
                df_resultado[col]
                .dropna()
                .astype(str)
                .apply(lambda s: sum(1 for link in s.split(",") if link.strip()))
                .sum()
            )
            num_socials += counts

    # --- Escritura del Excel ---
    excel_path = OUTPUT_FOLDER / f"{nombre_archivo.replace('.csv', '')}.xlsx"
    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        df_resultado.to_excel(writer, sheet_name="data", index=False)
        worksheet = writer.sheets["data"]

        # Aplicar autofiltro solo si hay columnas
        last_col = len(df_resultado.columns)
        if last_col > 0:
            last_letter = chr(ord('A') + last_col - 1)
            worksheet.autofilter(f"A1:{last_letter}1")

        # Hoja de estadísticas
        statistics = {
            "Number of companies":       [len(df_resultado)],
            "Number of domains":         [num_domains],
            "Number of emails (valid)":  [df_resultado["email"].astype(bool).sum()],
            "Number of phone numbers":   [df_resultado["phone"].astype(bool).sum()],
            "Number of social networks": [num_socials],
        }
        df_statistics = pd.DataFrame(statistics)
        df_statistics.to_excel(writer, sheet_name="statistics", index=False)

        # Sectores (main_category)
        if "main_category" in df_resultado.columns:
            df_sectors = (
                df_resultado["main_category"]
                .value_counts()
                .reset_index()
                .rename(columns={"index": "Sector", "main_category": "Number of companies"})
            )
            df_sectors.to_excel(writer, sheet_name="sectors", index=False)

        # Copyright
        copyright_text = """Legal Notice
© companiesdata.cloud All rights reserved.
Registered with the Ministry of Culture and Historical Heritage GR-00416-2020.
https://companiesdata.cloud/

The data sources are the official websites of each company.
We do not handle personal data, therefore LOPD and GDPR do not apply.

The database is non-transferable and non-replicable.
Copying, distribution, or publication, in whole or in part, without express consent is prohibited.
Legal action will be taken for copyright infringements.

For more information, please refer to our FAQ:
https://companiesdata.cloud/faq

Reproduction, distribution, public communication, and transformation, in whole or in part,
of the contents of this database are prohibited without the express authorization of companiesdata.cloud
The data has been collected from public sources and complies with current regulations."""
        df_copyright = pd.DataFrame(
            [line.split("\n") for line in copyright_text.split("\n")]
        )
        df_copyright.to_excel(
            writer, sheet_name="copyright", index=False, header=False
        )

    print(f"📊 Excel generado con estadísticas y datos: {excel_path}")
