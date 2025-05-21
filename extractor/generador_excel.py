import pandas as pd
from pathlib import Path
from urllib.parse import urlparse

# Ruta base: suponiendo que este archivo está en extractor/
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FOLDER = BASE_DIR / "data" / "outputs"

def generar_excel(df_resultado, nombre_archivo):
    """
    Genera un archivo Excel con:
      - Hoja `data` con los datos y autofiltros.
      - Hoja `statistics` con métricas.
      - Hoja `sectors` (si existe `main_category`).
      - Hoja `copyright` con aviso legal.
    """
    # --- Cálculo de métricas adicionales ---
    if "website" in df_resultado.columns:
        domains = (
            df_resultado["website"]
            .dropna()
            .astype(str)
            .apply(lambda s: urlparse(s).netloc)
        )
        num_domains = domains.nunique()
    else:
        num_domains = 0

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
    # Deshabilitar conversión automática de cadenas a URLs
    with pd.ExcelWriter(
            excel_path,
            engine="xlsxwriter",
            engine_kwargs={"options": {"strings_to_urls": False}}
    ) as writer:

        # Hoja de datos
        df_resultado.to_excel(writer, sheet_name="data", index=False)
        worksheet = writer.sheets["data"]
        last_col = len(df_resultado.columns)
        if last_col > 0:
            last_letter = chr(ord('A') + last_col - 1)
            worksheet.autofilter(f"A1:{last_letter}1")

        # Hoja de estadísticas
        stats = {
            "Number of companies":       [len(df_resultado)],
            "Number of domains":         [num_domains],
            "Number of emails (valid)":  [df_resultado.get("email", pd.Series()).astype(bool).sum()],
            "Number of phone numbers":   [df_resultado.get("phone", pd.Series()).astype(bool).sum()],
            "Number of social networks": [num_socials],
        }
        df_stats = pd.DataFrame(stats)
        df_stats.to_excel(writer, sheet_name="statistics", index=False)

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
        copyright_text = (
            "Legal Notice
            © companiesdata.cloud All rights reserved.
            Registered with the Ministry of Culture and Historical Heritage GR-00416-2020.
            https://companiesdata.cloud/ and https://www.centraldecomunicacion.es/
        
            The data sources are the official websites of each company.
            We do not handle personal data, therefore LOPD and GDPR do not apply.
        
            The database is non-transferable and non-replicable.
            Copying, distribution, or publication, in whole or in part, without express consent is prohibited.
            Legal action will be taken for copyright infringements.
        
            For more information, please refer to our FAQ:
            https://companiesdata.cloud/faq and https://www.centraldecomunicacion.es/preguntas-frecuentes-bases-de-datos/
        
            Reproduction, distribution, public communication, and transformation, in whole or in part,
            of the contents of this database are prohibited without the express authorization of companiesdata.cloud and centraldecomunicacion.es
            The data has been collected from public sources and complies with current regulations."
        )
        df_copyright = pd.DataFrame(
            [[line] for line in copyright_text.split("\n")]
        )
        df_copyright.to_excel(
            writer,
            sheet_name="copyright",
            index=False,
            header=False
        )

    print(f"📊 Excel generado con estadísticas y datos: {excel_path}")
