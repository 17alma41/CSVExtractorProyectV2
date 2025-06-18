"""
Benchmarking script para optimizar scraping:
Mide tiempos de extracción de emails y redes sociales en un conjunto de URLs de prueba
usando distintos valores de WORKER_OPTIONS y WAIT_TIMEOUT_OPTIONS.

Instrucciones:
 1. Ajusta TEST_URLS con URLs representativas.
 2. Desde la carpeta raíz del proyecto ejecuta:
     python scripts/benchmark_scraping.py
 3. Observa la matriz de tiempos y ajusta MAX_WORKERS / wait_timeout.
"""

import sys, os
# Asegura que Python encuentre el paquete extractor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from extractor.utils import setup_driver
from extractor.email_extractor import extract_emails_from_url
from extractor.social_extractor import extract_essential_social_links_from_url

# Lista de URLs de prueba
test_urls = [
    "https://example.com",
    # Añade más URLs representativas aquí...
]

# Parámetros a probar
worker_options = [1, 2, 4, 8]
wait_timeout_options = [5, 10, 15]

# Función de prueba para un solo URL y driver
def run_once(url, wait_timeout, driver):
    extract_emails_from_url(
        url,
        driver=driver,
        wait_timeout=wait_timeout,
        modo_verificacion='avanzado'
    )
    extract_essential_social_links_from_url(
        url,
        driver=driver,
        wait_timeout=wait_timeout
    )

results = []
for workers in worker_options:
    for wait_timeout in wait_timeout_options:
        start = time.perf_counter()
        drivers = []
        futures = []

        with ThreadPoolExecutor(max_workers=workers) as executor:
            for url in test_urls:
                # Crear un driver por tarea y almacenarlo para cierre
                drv = setup_driver(headless=True)
                drivers.append(drv)
                futures.append(
                    executor.submit(run_once, url, wait_timeout, drv)
                )
            # Esperar a todas las ejecuciones
            for f in futures:
                f.result()

        total = time.perf_counter() - start
        # Cerrar todos los drivers
        for drv in drivers:
            drv.quit()

        results.append({
            'workers': workers,
            'wait_timeout': wait_timeout,
            'total_time_s': total
        })

# Mostrar resultados en formato pivote
df = pd.DataFrame(results)
print(df.pivot(index='workers', columns='wait_timeout', values='total_time_s'))
