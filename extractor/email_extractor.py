import re
import time
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from extractor.email_verifier import verificar_existencia_email, determinar_estado

def setup_driver():
    # 1. Defino ruta absoluta al driver
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    chromedriver_path = PROJECT_ROOT / "drivers" / "chromedriver.exe"
    if not chromedriver_path.exists():
        raise FileNotFoundError(f"❌ No se encontró ChromeDriver en: {chromedriver_path}")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0")

    service = Service(str(chromedriver_path))
    return webdriver.Chrome(service=service, options=options)

def extract_emails_from_url(url, modo_verificacion='avanzado'):
    # 2. Rechazo URLs vacías o no HTTP
    if not url or not isinstance(url, str) or not url.startswith("http"):
        print(f"⚠️ URL inválida, saltando: {url}")
        return []

    driver = setup_driver()
    try:
        driver.set_page_load_timeout(15)
        driver.get(url)
        time.sleep(3)  # espero a que renderice

        html = driver.page_source
        # 3. Extraigo todos los emails que coincidan con el patrón
        raw_emails = set(re.findall(
            r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            html
        ))

        valid_emails = []
        for e in raw_emails:
            resultado = verificar_existencia_email(e, modo=modo_verificacion)
            estado = determinar_estado(resultado, modo=modo_verificacion)
            if estado == "Válido":
                valid_emails.append(e)

        print(f"🔍 {url} → Emails extraídos: {valid_emails}")
        return valid_emails

    except Exception as e:
        print(f"❌ Error en {url}: {e}")
        return []

    finally:
        driver.quit()
