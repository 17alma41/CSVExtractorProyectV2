"""
main.py - Punto de entrada principal del proyecto WebContactsExtractor
Permite ejecutar extracción, filtrado o generación de demo mediante flags CLI.
"""
import sys
sys.path.append(str(__file__).replace('main.py',''))
from src.extractor.web_scraper import run_extraction
from src.cleaner.exclusion_filter import run_filter
from src.demo.demo_generator import run_demo
import argparse
from pathlib import Path


def run_all(overwrite=False, test_mode=False, max_workers=None, wait_timeout=10, resume=False):
    """
    Ejecuta el flujo completo: limpieza → scraping → exclusión → demo.
    """
    from src.extractor.column_editor import procesar_csvs_en_carpeta
    import shutil
    import os
    from src.settings import INPUTS_DIR, CLEAN_INPUTS_DIR, OUTPUTS_DIR, XCLUSION_OUTPUTS_DIR, DEMO_OUTPUTS_DIR
    print("[1/4] Limpiando y normalizando archivos de entrada...")
    procesar_csvs_en_carpeta(
        carpeta_outputs=str(CLEAN_INPUTS_DIR),
        nuevo_orden=None,
        renombrar_columnas=None,
        overwrite=overwrite,
        test_mode=test_mode
    )
    print("[2/4] Ejecutando scraping web...")
    run_extraction(overwrite=overwrite, test_mode=test_mode, max_workers=max_workers, wait_timeout=wait_timeout, resume=resume)
    # NO eliminar archivos de inputs automáticamente
    # NO copiar outputs a exclusions_inputs ni exclusions_outputs a demo_inputs
    print("[3/4] Aplicando exclusiones y generando estadísticas...")
    run_filter(overwrite=overwrite, test_mode=test_mode, resume=resume)
    print("[4/4] Generando archivos demo enmascarados...")
    run_demo(overwrite=overwrite, test_mode=test_mode, resume=resume)
    print("✅ Flujo completo finalizado.")


def clean_logs():
    import os
    import glob
    from pathlib import Path
    logs_dir = Path(__file__).resolve().parent.parent / 'logs'
    if logs_dir.exists():
        confirm = input(f"¿Seguro que quieres eliminar todos los archivos de {logs_dir}? (s/N): ").strip().lower()
        if confirm != 's':
            print("❌ Operación cancelada.")
            return
        for file in logs_dir.glob('*'):
            try:
                file.unlink()
            except Exception as e:
                print(f"No se pudo eliminar {file}: {e}")
        print(f"🧹 Carpeta de logs limpiada: {logs_dir}")
    else:
        print(f"No existe la carpeta de logs: {logs_dir}")


def main():
    parser = argparse.ArgumentParser(description="WebContactsExtractor CLI")
    parser.add_argument('--extract', action='store_true', help='Ejecuta la extracción de datos web')
    parser.add_argument('--filter', action='store_true', help='Filtra emails según exclusiones')
    parser.add_argument('--demo', action='store_true', help='Genera versión demo enmascarada de los datos')
    parser.add_argument('--all', action='store_true', help='Ejecuta el flujo completo de procesamiento')
    parser.add_argument('--overwrite', action='store_true', help='Sobrescribe archivos ya existentes en cada etapa')
    parser.add_argument('--test', action='store_true', help='Procesa solo 20 filas por archivo (modo prueba)')
    parser.add_argument('--wait-timeout', type=int, default=10, help='Timeout de espera por página (segundos)')
    parser.add_argument('--resume', action='store_true', help='Reanuda archivos/URLs incompletos o fallidos')
    parser.add_argument('--clean-logs', action='store_true', help='Elimina todos los archivos de la carpeta logs/')
    args = parser.parse_args()

    # Ajuste automático de hilos
    import psutil, multiprocessing
    def get_optimal_workers():
        cpu_count = multiprocessing.cpu_count()
        ram_gb = psutil.virtual_memory().total / (1024**3)
        return max(1, min(cpu_count, int(ram_gb // 2)))
    max_workers = get_optimal_workers()

    if args.clean_logs:
        clean_logs()
        return
    if args.all:
        run_all(overwrite=args.overwrite, test_mode=args.test, max_workers=max_workers, wait_timeout=args.wait_timeout, resume=args.resume)
    elif args.extract:
        run_extraction(overwrite=args.overwrite, test_mode=args.test, max_workers=max_workers, wait_timeout=args.wait_timeout, resume=args.resume)
    elif args.filter:
        run_filter(overwrite=args.overwrite, test_mode=args.test, resume=args.resume)
    elif args.demo:
        run_demo(overwrite=args.overwrite, test_mode=args.test, resume=args.resume)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
