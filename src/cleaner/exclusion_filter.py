"""
exclusion_filter.py - Módulo para filtrar emails según listas de exclusión.
"""

import os
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as OpenpyxlImage
from pandas.plotting import table
from src.settings import XCLUSION_INPUTS_DIR, XCLUSION_OUTPUTS_DIR, EXCLUSIONES_FOLDER, HOJA_DATA, HOJA_STATS, IMAGE_SIZE
from src.utils.status_manager import load_status, update_status, is_stage_done, log_error

def cargar_exclusiones(carpeta=EXCLUSIONES_FOLDER):
    exclusiones = set()
    for fn in os.listdir(carpeta):
        if fn.endswith(".txt"):
            with open(os.path.join(carpeta, fn), encoding="utf-8") as f:
                exclusiones.update(line.strip().lower() for line in f if line.strip())
    return exclusiones

def filtrar_y_contar(df: pd.DataFrame, exclusiones: set):
    orig_listas = df["email"].fillna("").apply(
        lambda cell: [e.strip() for e in str(cell).replace(';', ',').split(',') if e.strip()]
    )
    orig_counts = orig_listas.apply(len)
    filt_listas = orig_listas.apply(
        lambda lst: [e for e in lst if not any(tok in e.lower() for tok in exclusiones)]
    )
    filt_counts = filt_listas.apply(len)
    df_filtrado = df.copy()
    df_filtrado["email"] = filt_listas.apply(lambda lst: ", ".join(lst) if lst else pd.NA)
    total_eliminadas = (orig_counts - filt_counts).sum()
    total_restantes = filt_counts.explode().dropna().nunique()
    return df_filtrado, total_eliminadas, total_restantes

def generar_estadisticas(df_data, df_sectors):
    stats = {
        "Number of companies": len(df_data),
        "Number of emails (unique)": df_data["email"].dropna().apply(
            lambda x: [e.strip() for e in str(x).split(",") if e.strip()]
        ).explode().nunique(),
        "Number of phone numbers": df_data["phone"].dropna().count(),
        "Mobile phones": df_data["phone"].dropna().count(),
        "Number of domains": df_data["website"].dropna().nunique() if "website" in df_data else 0,
        "Number of social networks": df_data[["facebook", "instagram", "linkedin", "x"]].notna().sum().sum() if all(
            col in df_data.columns for col in ["facebook", "instagram", "linkedin", "x"]) else 0
    }
    return pd.DataFrame([stats])

def insertar_imagen_en_excel(path_excel, path_imagen, hoja=HOJA_STATS, cell='A10'):
    wb = load_workbook(path_excel)
    ws = wb[hoja]
    img = OpenpyxlImage(path_imagen)
    ws.add_image(img, cell)
    wb.save(path_excel)

def guardar_tabla_como_imagen(df, path_imagen, title=None, columns=None):
    max_chars = 40
    max_columns = 5
    max_rows = 20
    if columns:
        df = df[columns]
    if df.shape[1] > max_columns:
        df = df.iloc[:, :max_columns]
    df = df.head(max_rows)
    df = df.copy().astype(str).apply(
        lambda col: col.map(lambda x: x[:max_chars] + "…" if len(x) > max_chars else x)
    )
    fig, ax = plt.subplots(figsize=(IMAGE_SIZE[0] / 100, IMAGE_SIZE[1] / 100))
    ax.axis("off")
    is_sectors = any("sector" in c.lower() for c in df.columns) and any(
        tok in c.lower() for tok in ("number", "count") for c in df.columns
    )
    col_widths = []
    for idx, col in enumerate(df.columns):
        col_lower = col.lower()
        if is_sectors:
            if idx == 0:
                col_widths.append(0.6)
            else:
                col_widths.append(0.4)
        elif "review" in col_lower:
            col_widths.append(0.05)
        elif "rating" in col_lower:
            col_widths.append(0.08)
        elif any(keyword in col_lower for keyword in ["name", "categories", "main_category"]):
            max_len = df[col].map(len).max()
            if max_len < 15:
                col_widths.append(0.18)
            elif max_len < 30:
                col_widths.append(0.24)
            else:
                col_widths.append(0.30)
        else:
            col_widths.append(0.12)
    tbl = table(ax, df, loc="center", colWidths=col_widths)
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1.2, 1.2)
    for key, cell in tbl.get_celld().items():
        cell.set_edgecolor('#cccccc')
        cell.set_linewidth(0.5)
        if key[0] == 0:
            cell.set_facecolor('#e6f2ff')
            cell.set_text_props(weight='bold')
        else:
            cell.set_facecolor('#ffffff')
    if title:
        ax.set_title(title, fontweight="bold", fontsize=13, pad=15)
    plt.tight_layout()
    fig.savefig(path_imagen, dpi=100)
    plt.close(fig)

def procesar_archivo(path_entrada: str, exclusiones: set):
    hojas = pd.read_excel(path_entrada, sheet_name=None)
    if HOJA_DATA not in hojas:
        raise RuntimeError(f"No existe la hoja '{HOJA_DATA}' en {path_entrada}")
    df_data = hojas[HOJA_DATA]
    df_limpia, tot_elim, tot_rest = filtrar_y_contar(df_data, exclusiones)
    hojas_out = {}
    hojas_out[HOJA_DATA] = df_limpia
    for name, df in hojas.items():
        if name not in (HOJA_DATA, HOJA_STATS):
            hojas_out[name] = df.copy()
    df_stats = generar_estadisticas(df_limpia, hojas.get("sectors", pd.DataFrame(columns=["Sector"])))
    hojas_out[HOJA_STATS] = df_stats
    return hojas_out, df_stats

def guardar_hojas(hojas_dict: dict, path_salida: str):
    os.makedirs(os.path.dirname(path_salida), exist_ok=True)
    with pd.ExcelWriter(path_salida, engine="openpyxl") as writer:
        for nombre in (HOJA_DATA, HOJA_STATS):
            if nombre in hojas_dict:
                hojas_dict[nombre].to_excel(writer, sheet_name=nombre, index=False)
        for nombre, df in hojas_dict.items():
            if nombre not in (HOJA_DATA, HOJA_STATS):
                df.to_excel(writer, sheet_name=nombre, index=False)

def run_filter(overwrite=False, test_mode=False, resume=False):
    """
    Ejecuta el filtrado de emails según exclusiones.
    """
    exclusiones = cargar_exclusiones()
    print(f"📋 Cargadas {len(exclusiones)} palabras de exclusión\n")
    for fn in os.listdir(XCLUSION_INPUTS_DIR):
        try:
            if not overwrite and is_stage_done(fn, 'excluded'):
                print(f"[SKIP] {fn} ya excluido.")
                continue
            if not fn.lower().endswith(".xlsx"):
                continue
            entrada = XCLUSION_INPUTS_DIR / fn
            salida = XCLUSION_OUTPUTS_DIR / fn
            print(f"🔄 Procesando: {fn}")
            hojas_out, estadisticas = procesar_archivo(entrada, exclusiones)
            df_data = hojas_out[HOJA_DATA]
            if "reviews" in df_data.columns:
                df_data["reviews"] = pd.to_numeric(df_data["reviews"], errors="coerce")
                df_data = df_data.sort_values("reviews", ascending=False)
                hojas_out[HOJA_DATA] = df_data
            guardar_hojas(hojas_out, salida)
            graph_path = XCLUSION_OUTPUTS_DIR / fn.replace(".xlsx", "_stats.jpg")
            estadisticas.T.plot(kind="bar", legend=False, figsize=(12, 6), title="Statistics Overview", color="#3498db")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig(graph_path, dpi=100)
            plt.close()
            insertar_imagen_en_excel(salida, graph_path)
            guardar_tabla_como_imagen(
                df_data.head(20),
                XCLUSION_OUTPUTS_DIR / fn.replace(".xlsx", "_data.jpg"),
                title="Data"
            )
            df_sectors = hojas_out.get("sectors")
            if df_sectors is not None:
                sector_cols = [col for col in df_sectors.columns if "sector" in col.lower()]
                company_cols = [col for col in df_sectors.columns if any(tok in col.lower() for tok in ("number", "count"))]
                if not sector_cols and len(df_sectors.columns) == 2:
                    sector_cols = [df_sectors.columns[0]]
                    company_cols = [df_sectors.columns[1]]
                if sector_cols and company_cols:
                    df_sector_imagen = df_sectors[[sector_cols[0], company_cols[0]]].copy()
                    df_sector_imagen.columns = ["Sector", "Number of companies"]
                    df_sector_imagen = df_sector_imagen.sort_values("Number of companies", ascending=False)
                    guardar_tabla_como_imagen(
                        df_sector_imagen,
                        XCLUSION_OUTPUTS_DIR / fn.replace(".xlsx", "_sectors.jpg"),
                        title="Sectors"
                    )
                else:
                    print("⚠️ No se encontraron columnas adecuadas en la hoja 'sectors'")
            else:
                print("⚠️ Hoja 'sectors' no encontrada")
            print(f"✅ Guardado → {salida}\n")
            update_status(fn, 'excluded', True)
        except Exception as e:
            log_error(fn, 'exclusion', '', str(e))
