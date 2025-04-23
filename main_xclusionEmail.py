import os
import pandas as pd

# 📂 Configuración
CLEAN_INPUT_FOLDER = "./xclusiones"
OUTPUT_FOLDER      = "./xclusiones_outputs"
EXCLUSIONES_FOLDER = "./txt_config/xclusiones_email"
HOJA_DATOS         = "datos"
HOJA_STATS         = "statistics"

def cargar_exclusiones(carpeta):
    exclusiones = set()
    for fn in os.listdir(carpeta):
        if fn.endswith(".txt"):
            with open(os.path.join(carpeta, fn), encoding="utf-8") as f:
                exclusiones.update(line.strip().lower() for line in f if line.strip())
    return exclusiones

def filtrar_y_contar(df: pd.DataFrame, exclusiones: set):
    """
    Filtra direcciones excluidas dentro de cada celda de 'email' y devuelve:
      - df_filtrado       : DataFrame con emails limpiados
      - total_eliminadas  : número total de direcciones borradas
      - total_restantes   : número total de direcciones que quedan
    """
    # Lista original de listas de emails por fila
    orig_listas = df["email"].fillna("").apply(
        lambda cell: [e.strip() for e in str(cell).replace(';', ',').split(',') if e.strip()]
    )
    orig_counts = orig_listas.apply(len)

    # Lista filtrada
    filt_listas = orig_listas.apply(
        lambda lst: [e for e in lst if not any(tok in e.lower() for tok in exclusiones)]
    )
    filt_counts = filt_listas.apply(len)

    # Reconstruir columna 'email'
    df_filtrado = df.copy()
    df_filtrado["email"] = filt_listas.apply(
        lambda lst: ", ".join(lst) if lst else pd.NA
    )

    total_eliminadas = (orig_counts - filt_counts).sum()
    total_restantes  = filt_counts.sum()
    return df_filtrado, total_eliminadas, total_restantes

def procesar_archivo(path_entrada: str, exclusiones: set):
    hojas = pd.read_excel(path_entrada, sheet_name=None)
    resultado = {}

    # 1) Procesar 'datos'
    if HOJA_DATOS not in hojas:
        raise RuntimeError(f"No existe la hoja '{HOJA_DATOS}' en {path_entrada}")
    df_datos = hojas[HOJA_DATOS]
    df_limpia, tot_elim, tot_rest = filtrar_y_contar(df_datos, exclusiones)
    resultado[HOJA_DATOS] = df_limpia
    print(f"✂️ '{HOJA_DATOS}': {tot_elim} direcciones eliminadas, {tot_rest} restantes")

    # 2) Copiar intactas las demás (menos statistics)
    for name, df in hojas.items():
        if name not in (HOJA_DATOS, HOJA_STATS):
            resultado[name] = df.copy()

    # 3) Actualizar 'statistics'
    if HOJA_STATS in hojas:
        df_stats = hojas[HOJA_STATS].copy()
        # Detectar columna de emails
        col_emails = next(
            (c for c in df_stats.columns
             if "number" in c.lower() and "email" in c.lower()),
            None
        )
        if col_emails:
            df_stats.loc[0, col_emails] = tot_rest
            print(f"📊 '{HOJA_STATS}' actualizado: '{col_emails}' = {tot_rest}")
        resultado[HOJA_STATS] = df_stats
    else:
        print(f"⚠️ No existe la hoja '{HOJA_STATS}'")

    return resultado

def guardar_hojas(hojas_dict: dict, path_salida: str):
    """
    Guarda las hojas en el orden:
      1. datos
      2. statistics
      3. todas las demás en el orden que aparezcan
    """
    os.makedirs(os.path.dirname(path_salida), exist_ok=True)
    with pd.ExcelWriter(path_salida, engine="openpyxl") as writer:
        # Primero 'datos' y 'statistics'
        for nombre in (HOJA_DATOS, HOJA_STATS):
            if nombre in hojas_dict:
                hojas_dict[nombre].to_excel(writer, sheet_name=nombre, index=False)
        # Después el resto
        for nombre, df in hojas_dict.items():
            if nombre not in (HOJA_DATOS, HOJA_STATS):
                df.to_excel(writer, sheet_name=nombre, index=False)

def main():
    exclusiones = cargar_exclusiones(EXCLUSIONES_FOLDER)
    print(f"📋 Cargadas {len(exclusiones)} palabras de exclusión\n")

    for fn in os.listdir(CLEAN_INPUT_FOLDER):
        if not fn.lower().endswith(".xlsx"):
            continue
        entrada = os.path.join(CLEAN_INPUT_FOLDER, fn)
        salida  = os.path.join(OUTPUT_FOLDER, fn.replace(".xlsx", ".xlsx"))

        print(f"🔄 Procesando: {fn}")
        hojas_out = procesar_archivo(entrada, exclusiones)
        guardar_hojas(hojas_out, salida)
        print(f"✅ Guardado → {salida}\n")

if __name__ == "__main__":
    main()
