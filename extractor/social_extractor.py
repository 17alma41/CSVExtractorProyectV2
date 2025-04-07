import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.chrome.service import Service
import os

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0")

    # Ruta al directorio raíz del proyecto (donde está este archivo)
    PROYECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Ruta absoluta al chromedriver.exe en la raíz del proyecto
    chromedriver_path = os.path.join(PROYECT_ROOT, "chromedriver.exe")
    service = Service(chromedriver_path)

    try:
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f"❌ Error inicializando ChromeDriver: {e}")
        return None

def extract_essential_social_links_from_url(url):
    print(f"\n🌐 Procesando URL: {url}")
    driver = setup_driver()
    if not driver:
        print("🚫 No se pudo iniciar el driver. Abortando operación.")
        return {}

    try:
        print("⏳ Cargando página...")
        driver.set_page_load_timeout(15)
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        print("✅ Página cargada y desplazada hacia el final.")

        links = driver.find_elements("tag name", "a")
        print(f"🔍 {len(links)} enlaces encontrados. Filtrando redes sociales...")

        urls = [link.get_attribute("href") for link in links if link.get_attribute("href")]

        patterns = {
            "facebook": "facebook.com/",
            "instagram": "instagram.com/",
            "linkedin": "linkedin.com/",
            "x": "x.com/"
        }

        found = {}
        for name, domain in patterns.items():
            found_links = [u for u in urls if domain in u and len(u) < 100]
            if found_links:
                found[name] = list(set(found_links))

        if found:
            print(f"🔗 Redes encontradas en {url}: {', '.join(found.keys())}")
        else:
            print(f"ℹ️ No se encontraron redes sociales en {url}")

        return found

    except TimeoutException:
        print(f"⏱️ Timeout al cargar {url}")
        return {}
    except Exception as e:
        print(f"❌ Error al extraer redes sociales de {url}: {e}")
        return {}
    finally:
        print("🧹 Cerrando navegador...")
        driver.quit()
