# 📬 WebContacts Extractor - Extracción de datos automatizada

**WebContacts Extractor** es una herramienta modular y escalable para **extraer correos electrónicos y redes sociales** desde sitios web listados en archivos `.csv`. Incluye funciones para verificación avanzada de emails, edición de columnas, limpieza por lotes, generación de archivos demo enmascarados y exclusión de correos no deseados según listas personalizables.

---

## 🚀 Funcionalidades clave

- 🔍 **Extracción automatizada de emails** con Selenium.
- 🌐 **Scraping de redes sociales**: Facebook, Instagram, LinkedIn, X/Twitter.
- 📧 **Verificación avanzada** de emails: formato, dominio, MX, SPF, DKIM, SMTP.
- ✂️ **Exclusión de emails** con nombres/apellidos o palabras clave desde archivos `.txt`.
- 🛠️ **Editor de columnas** para ordenar, renombrar o eliminar columnas.
- 📊 **Generación de Excel (.xlsx)** con datos organizados.
- 🔒 **Modo demo** con enmascaramiento de datos sensibles.
- ⚡ **Paralelización** con `ThreadPoolExecutor` para mayor rendimiento.
- 🧹 **Limpieza masiva de CSVs** vacíos o con información irrelevante.
- 📁 Estructura lista para producción y mantenimiento escalable.

---

## 🗂 Estructura del proyecto

```
CSVExtractorProyect/
├── scripts/
│   ├── main.py                        # Script principal
│   ├── main_xclusionEmail.py         # Variante con exclusión de emails
│   └── demo_masker.py                # Generador enmascarado para modo demo
├── extractor/
│   ├── email_extractor.py            # Scraper de emails
│   ├── social_extractor.py           # Scraper de redes sociales
│   ├── email_verifier.py             # Verificación avanzada
│   ├── column_editor.py              # Gestión de columnas
│   ├── generador_excel.py            # Generación de Excel
│   ├── limpiar_csv_lote.py           # Limpieza por lotes
│   └── utils.py                      # Utilidades compartidas
├── txt_config/                       # Archivos de configuración
│   ├── columnas_a_eliminar.txt
│   ├── orden_columnas.txt
│   └── renombrar_columnas.txt
├── xclusiones_email/                # Palabras a excluir en emails
│   ├── apellidos.txt
│   ├── nombres.txt
│   ├── spam.txt
│   ├── spamEN.txt
│   ├── spamIT.txt
│   └── spamPT.txt
├── drivers/
│   └── chromedriver.exe              # Driver de Selenium
├── inputs/                           # CSVs originales
├── clean_inputs/                     # CSVs limpios
├── outputs/                          # Resultados completos
├── demo_inputs/                      # Datos reales para demo
├── demo_outputs/                     # Datos enmascarados para demo
├── xclusiones_outputs/              # Resultados con exclusiones aplicadas
├── requirements.txt
└── README.md
```

---

## ⚙️ Requisitos

1. Python **3.8 o superior**
2. Instalar las dependencias:
```bash
  pip install -r requirements.txt
```
3. Tener **Google Chrome instalado**
4. Descargar el **ChromeDriver** desde:
   👉 [https://sites.google.com/chromium.org/driver/](https://sites.google.com/chromium.org/driver/)
5. Colocar `chromedriver.exe` en la carpeta `drivers/` o incluirlo en el `PATH`.

---
## ▶️ Instrucciones de uso

1. Agrega los archivos ``.csv`` a la carpeta ``data/inputs``
2. Ejecuta el script principal:
```bash
  python scripts/main.py
```
3. Obtendrás archivos `.xlxs` en `outputs/`.
---
## 🔒 Generar archivos demo enmascarados

1. Coloca tus `.csv` o `.xlsx` reales en `demo_inputs/`
2. Ejecuta:
```bash
  python scripts/demo_masker.py
```
3. Obtendrás archivos en `demo_outputs/` con datos como:

```
contacto@empresa.com → c****@empresa.com
612 34 56 78         → 612 34 56 **
instagram.com/user   → instagram.com/****
```

---

## ✂️ Exclusión de emails no deseados

Puedes excluir emails que contengan palabras como `"info"`, `"admin"`, nombres comunes, spam o apellidos no deseados:

- Edita los archivos en `xclusiones_email/`
- Ejecuta `scripts/main_xclusionEmail.py` para aplicar esta lógica



