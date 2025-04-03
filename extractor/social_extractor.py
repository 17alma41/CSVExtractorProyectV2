# Para usarlo: Descomentar de redes en main.py

import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0")
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
        page_source = driver.page_source

        patterns = {
            "facebook": r'https?://(?:www\.)?facebook\.com/[^"\'>\s]+',
            "instagram": r'https?://(?:www\.)?instagram\.com/[^"\'>\s]+',
            "linkedin": r'https?://(?:www\.)?linkedin\.com/[^"\'>\s]+',
            "twitter": r'https?://(?:www\.)?(twitter|x)\.com/[^"\'>\s]+'
        }

        found = {}
        for name, pattern in patterns.items():
            matches = re.findall(pattern, page_source)
            if matches:
                found[name] = list(set(matches))

        return found

    except Exception as e:
        print(f"❌ Error al extraer redes sociales esenciales de {url}: {e}")
        return {}
    finally:
        driver.quit()
