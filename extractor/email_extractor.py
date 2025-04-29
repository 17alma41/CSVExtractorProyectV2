import re
from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from extractor.utils import setup_driver
from extractor.email_verifier import verificar_existencia_email, determinar_estado


def extract_emails_from_url(
    url: str,
    modo_verificacion: str = 'avanzado',
    driver=None,
    wait_timeout: int = 10,
):
    """
    Extrae emails de la URL dada usando Selenium driver compartido.
    - url: dirección HTTP/HTTPS.
    - modo_verificacion: 'avanzado' o 'ultra-avanzado'.
    - driver: instancia de Selenium; si no se pasa, se crea y cierra internamente.
    - wait_timeout: segundos a esperar por carga de <body>.

    Retorna lista de emails válidos.
    """
    if not url or not isinstance(url, str) or not url.lower().startswith(('http://', 'https://')):
        print(f"⚠️ URL inválida, saltando: {url}")
        return []

    driver_created = False
    if driver is None:
        driver = setup_driver()
        driver_created = True

    try:
        driver.get(url)
        # Espera explícita a que el <body> esté presente (carga completa)
        WebDriverWait(driver, wait_timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        html = driver.page_source

        # Extraer con regex
        raw_emails = set(re.findall(
            r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            html
        ))

        valid_emails = []
        for e in raw_emails:
            resultados = verificar_existencia_email(e, modo=modo_verificacion)
            estado = determinar_estado(resultados, modo=modo_verificacion)
            if estado == 'Válido':
                valid_emails.append(e)

        print(f"🔍 {url} → Emails extraídos: {valid_emails}")
        return valid_emails

    except Exception as e:
        print(f"❌ Error en {url}: {e}")
        return []

    finally:
        # Si el driver fue creado aquí, cerrarlo; si se reusa externamente, no tocarlo
        if driver_created:
            driver.quit()
