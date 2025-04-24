# 📬 WebContacts Extractor – Automated Data Extraction

**WebContacts Extractor** is a modular and scalable tool designed to **extract email addresses and social media profiles** from websites listed in `.csv` files. It includes advanced email verification, column editing, batch cleaning, masked demo generation, and email filtering based on customizable keyword lists.

---

## 🚀 Key Features

- 🔍 **Automated email extraction** using Selenium.
- 🌐 **Social media scraping**: Facebook, Instagram, LinkedIn, X/Twitter.
- 📧 **Advanced email verification**: format, domain, MX, SPF, DKIM, SMTP.
- ✂️ **Email exclusion** based on names, surnames or keywords via `.txt` files.
- 🛠️ **Column editor** for ordering, renaming or removing columns.
- 📊 **Excel (.xlsx) generation** with organized data.
- 🔒 **Demo mode** with sensitive data masking.
- ⚡ **Parallel processing** using `ThreadPoolExecutor` for higher performance.
- 🧹 **Batch CSV cleaning** for empty or irrelevant rows.
- 📁 Production-ready and scalable project structure.

---

## 🗂 Project Structure

```
CSVExtractorProyect/
├── scripts/
│   ├── main.py                        # Main script
│   ├── main_xclusionEmail.py         # Variant with email exclusion
│   └── demo_masker.py                # Demo data masker generator
├── extractor/
│   ├── email_extractor.py            # Email scraper
│   ├── social_extractor.py           # Social media scraper
│   ├── email_verifier.py             # Advanced verification
│   ├── column_editor.py              # Column handling
│   ├── generador_excel.py            # Excel generation
│   ├── limpiar_csv_lote.py           # Batch CSV cleaner
│   └── utils.py                      # Shared utilities
├── txt_config/                       # Configuration files
│   ├── columnas_a_eliminar.txt
│   ├── orden_columnas.txt
│   └── renombrar_columnas.txt
├── xclusiones_email/                # Email keyword exclusion lists
│   ├── apellidos.txt
│   ├── nombres.txt
│   ├── spam.txt
│   ├── spamEN.txt
│   ├── spamIT.txt
│   └── spamPT.txt
├── drivers/
│   └── chromedriver.exe              # Selenium driver
├── inputs/                           # Original input CSVs
├── clean_inputs/                     # Cleaned CSVs
├── outputs/                          # Final results
├── demo_inputs/                      # Real data for demo masking
├── demo_outputs/                     # Masked demo results
├── xclusiones_outputs/              # Results with email exclusions
├── requirements.txt
└── README-EN.md
```

---

## ⚙️ Requirements

1. Python **3.8 or higher**
2. Install dependencies:
```bash
  pip install -r requirements.txt
```
3. Make sure **Google Chrome is installed**
4. Download **ChromeDriver** from:
   👉 [https://sites.google.com/chromium.org/driver/](https://sites.google.com/chromium.org/driver/)
5. Place `chromedriver.exe` in the `drivers/` folder or add it to your `PATH`.

---
## ▶️ How to Use

1. Add your `.csv` files to the `data/inputs` folder
2. Run the main script:
```bash
  python scripts/main.py
```
3. Output `.xlsx` files will be generated in `outputs/`.

---

## 🔒 Generate Masked Demo Files

1. Add real `.csv` or `.xlsx` files to `demo_inputs/`
2. Run:
```bash
  python scripts/demo_masker.py
```
3. Masked results will appear in `demo_outputs/` with examples like:

```
contacto@empresa.com → c****@empresa.com
612 34 56 78         → 612 34 56 **
instagram.com/user   → instagram.com/****
```

---

## ✂️ Exclude Unwanted Emails

You can exclude email addresses containing keywords such as `"info"`, `"admin"`, common names, spam, or surnames:

- Edit the `.txt` lists in the `xclusiones_email/` folder
- Run `scripts/main_xclusionEmail.py` to apply the exclusions
