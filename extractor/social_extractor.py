import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36")
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except WebDriverException as e:
        print(f"❌ Error inicializando ChromeDriver: {e}")
        return None

def extract_essential_social_links_from_url(url):
    driver = setup_driver()
    if not driver:
        return {}

    try:
        driver.set_page_load_timeout(15)
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Esperar a que cargue

        links = driver.find_elements("tag name", "a")
        urls = [link.get_attribute("href") for link in links if link.get_attribute("href")]

        patterns = {
            "facebook": "facebook.com/",
            "instagram": "instagram.com/",
            "linkedin": "linkedin.com/",
            "twitter": "twitter.com/"
        }

        found = {}
        for name, domain in patterns.items():
            found_links = [u for u in urls if domain in u]
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
        driver.quit()
