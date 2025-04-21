import pandas as pd


def generar_excel(df_resultado, nombre_archivo):
    excel_path = f"outputs/{nombre_archivo.replace('.csv', '')}.xlsx"
    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        # Hoja de datos
        df_resultado.to_excel(writer, sheet_name="datos", index=False)

        # Statistics
        statistics = {
            "Number of companies": [len(df_resultado)],
            "Number of emails (valid)": [df_resultado["email"].astype(bool).sum()],
            "Number of phone numbers": [df_resultado["phone"].astype(bool).sum()],
            "Landline phones": [df_resultado["phone"].str.extract(r'(\d+)')[0].dropna().apply(
                lambda x: str(x).startswith(("9", "8"))).sum()],
            "Mobile phones": [df_resultado["phone"].str.extract(r'(\d+)')[0].dropna().apply(
                lambda x: str(x).startswith(("6", "7"))).sum()],
        }
        df_statistics = pd.DataFrame(statistics)
        df_statistics.to_excel(writer, sheet_name="statistics", index=False)

        # Sectors (main_category)
        if "main_category" in df_resultado.columns:
            df_sectors = df_resultado["main_category"].value_counts().reset_index()
            df_sectors.columns = ["Sector", "Number of companies"]
            df_sectors.to_excel(writer, sheet_name="sectors", index=False)

        # Copyright
        copyright_text = """Legal Notice
        © centraldecomunicacion.es. All rights reserved.
        Registered with the Ministry of Culture and Historical Heritage GR-00416-2020.
        https://www.centraldecomunicacion.es/
        
        The data sources are the official websites of each company.
        We do not handle personal data, therefore LOPD and GDPR do not apply.
        
        The database is non-transferable and non-replicable.
        Copying, distribution, or publication, in whole or in part, without express consent is prohibited.
        Legal action will be taken for copyright infringements.
        
        For more information, please refer to our FAQ:
        https://www.centraldecomunicacion.es/preguntas-frecuentes-bases-de-datos/
        
        Reproduction, distribution, public communication, and transformation, in whole or in part,
        of the contents of this database are prohibited without the express authorization of centraldecomunicacion.es.
        The data has been collected from public sources and complies with current regulations."""
        df_copyright = pd.DataFrame([line.split("\n") for line in copyright_text.split("\n")])
        df_copyright.to_excel(writer, sheet_name="copyright", index=False, header=False)

    print(f"📊 Excel generado con estadísticas y datos: {excel_path}")
