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
        copyright_text = """Aviso Legal
        © centraldecomunicacion.es. Todos los derechos reservados.
        Registrada ante la consejería de cultura y patrimonio histórico GR-00416-2020.
        https://www.centraldecomunicacion.es/

        Las fuentes de los datos son las páginas web oficiales de cada empresa.
        No manejamos datos personales, por lo que no aplican LOPD ni RGPD.

        La base de datos es intransferible y no replicable.
        Se prohíbe la copia, distribución o publicación total o parcial sin consentimiento expreso.
        Se tomarán medidas legales por infracciones de derechos de autor.

        Para más información, consulte nuestras preguntas frecuentes:
        https://www.centraldecomunicacion.es/preguntas-frecuentes-bases-de-datos/

        Queda prohibida la reproducción, distribución, comunicación pública y transformación, total o parcial,
        de los contenidos de esta base de datos, sin la autorización expresa de centraldecomunicacion.es.
        Los datos han sido recopilados de fuentes públicas y cumplen con la normativa vigente."""
        df_copyright = pd.DataFrame([line.split("\n") for line in copyright_text.split("\n")])
        df_copyright.to_excel(writer, sheet_name="copyright", index=False, header=False)

    print(f"📊 Excel generado con estadísticas y datos: {excel_path}")
