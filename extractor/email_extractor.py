import re
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def setup_driver():
    options = Options()
    options.add_argument("--headless")  # Quitalo si querés ver Chrome abrirse
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0")

    # Ruta local al chromedriver.exe dentro del proyecto
    chromedriver_path = os.path.abspath("chromedriver.exe")
    service = Service(chromedriver_path)

    try:
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f"❌ Error inicializando ChromeDriver: {e}")
        return None

def extract_emails_from_url(url):
    driver = setup_driver()
    if not driver:
        return []

    try:
        driver.set_page_load_timeout(15)
        driver.get(url)
        time.sleep(5)  # Esperar a que cargue

        page_text = driver.page_source
        emails = set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", page_text))

        print(f"🔍 {url} → {emails}")
        return list(emails)

    except Exception as e:
        print(f"❌ Error en {url}: {e}")
        return []

    finally:
        driver.quit()
