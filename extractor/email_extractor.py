import re
import time
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from extractor.email_verifier import verificar_existencia_email, determinar_estado

def setup_driver():
    # 1️⃣ Definir ruta absoluta al driver
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    chromedriver_path = PROJECT_ROOT / "drivers" / "chromedriver.exe"
    if not chromedriver_path.exists():
        raise FileNotFoundError(f"❌ No se encontró ChromeDriver en: {chromedriver_path}")

    # 2️⃣ Configurar opciones "lightweight"
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-software-rasterizer")
    opts.add_argument("--blink-settings=imagesEnabled=false")
    opts.add_argument("user-agent=Mozilla/5.0")

    # 3️⃣ Iniciar servicio y driver
    service = Service(str(chromedriver_path))
    driver = webdriver.Chrome(service=service, options=opts)

    # 4️⃣ Ajustar timeouts
    driver.set_page_load_timeout(15)  # abortar páginas muy lentas
    return driver


def extract_emails_from_url(url, modo_verificacion='avanzado'):
    # 1️⃣ Validar URL
    if not url or not isinstance(url, str) or not url.lower().startswith(('http://', 'https://')):
        print(f"⚠️ URL inválida, saltando: {url}")
        return []

    driver = setup_driver()
    try:
        driver.get(url)
        time.sleep(3)  # espera mínima para renderizado

        html = driver.page_source
        # 2️⃣ Extraer emails con regex
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
