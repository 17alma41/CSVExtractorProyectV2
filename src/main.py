import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import argparse
from extractor.web_scraper import run_extraction
from cleaner.exclusion_filter import run_filter
from demo.demo_generator import run_demo
from extractor.limpiar_csv_lote import main as clean_main


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline CSVExtractorProyectV2: limpieza, scraping, exclusión, enmascarado, demo."
    )
    parser.add_argument('--clean', action='store_true', help='Ejecutar solo limpieza de archivos en ./data/inputs → ./data/clean_inputs')
    parser.add_argument('--scrap', action='store_true', help='Ejecutar solo scraping sobre ./data/clean_inputs → ./data/outputs')
    parser.add_argument('--exclude', action='store_true', help='Ejecutar solo exclusión de emails/generación imágenes → ./data/exclusions_outputs')
    parser.add_argument('--mask', action='store_true', help='Ejecutar solo enmascarado/demos → ./data/demo_outputs')
    parser.add_argument('--all', action='store_true', help='Ejecutar TODO el flujo completo')
    parser.add_argument('--test', action='store_true', help='Modo test: solo 20 filas por archivo')
    parser.add_argument('--overwrite', action='store_true', help='Sobrescribir archivos ya procesados')
    parser.add_argument('--resume', action='store_true', help='Reanudar etapas incompletas')
    args = parser.parse_args()

    # Si no se pasa ningún flag, mostrar ayuda
    if not any([args.clean, args.scrap, args.exclude, args.mask, args.all]):
        parser.print_help()
        return

    if args.all or args.clean:
        print("\n==== LIMPIEZA ====")
        # El script limpiar_csv_lote.py no tiene función, así que ejecutamos su main
        clean_main()  # Esto procesará ./data/inputs → ./data/clean_inputs

    if args.all or args.scrap:
        print("\n==== SCRAPING ====")
        run_extraction(
            overwrite=args.overwrite or args.all,
            test_mode=args.test,
            resume=args.resume
        )

    if args.all or args.exclude:
        print("\n==== EXCLUSIÓN DE EMAILS/IMÁGENES ====")
        run_filter(
            overwrite=args.overwrite or args.all,
            test_mode=args.test,
            resume=args.resume
        )

    if args.all or args.mask:
        print("\n==== ENMASCARADO/DEMOS ====")
        run_demo(
            overwrite=args.overwrite or args.all,
            test_mode=args.test,
            resume=args.resume
        )

if __name__ == "__main__":
    main()
