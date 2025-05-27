# CSVExtractorProyect V2

**CSVExtractorProyect V2** is a professional and automated solution for extracting, filtering, and masking contact data (emails, social networks, phones, etc.) from CSV files and websites. The system is designed to be robust, modular, and easy to use, allowing you to resume processes and handle errors intelligently.

---

## 🚀 What does this project do?
- **Cleans and normalizes** input CSV files.
- **Extracts** emails and social networks from websites using advanced scraping and automatic parallelism.
- **Filters** unwanted emails based on configurable exclusion lists.
- **Generates demo files** with masked/anonymous data for sharing without exposing real data.
- **Records the state** of each file and stage, allowing you to resume interrupted processes.
- **Manages errors** and logs in a centralized and professional way.

---

## 📁 Project Structure

```
CSVExtractorProyectV2/
├── src/
│   ├── main.py                # CLI entry point
│   ├── settings.py            # Path and constants configuration
│   ├── extractor/             # Extraction and cleaning
│   ├── cleaner/               # Exclusion filtering
│   ├── demo/                  # Demo file generation
│   ├── utils/                 # Utilities and state/log management
├── config/                    # Column and exclusion configuration
├── data/
│   ├── inputs/                # Original CSVs
│   ├── clean_inputs/          # Normalized CSVs
│   ├── outputs/               # Scraping results
│   ├── exclusions_outputs/    # Results after exclusion
│   └── demo_outputs/          # Masked demo files
├── logs/                      # Execution logs and state
│   ├── procesamiento.log
│   ├── status.json
│   └── error_log.txt
├── requirements.txt           # Python dependencies
└── README_EN.md               # This documentation
```

---

## ⚙️ Installation

1. **Clone the repository** and enter the project folder.
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
   > **Note:** Make sure you also have `matplotlib` and `Pillow` (these are included in the requirements file).
3. Make sure you have the Selenium driver (e.g., `chromedriver.exe`) in the `/drivers` folder.

---
## ▶️ Usage Instructions

1. Add your `.csv` files to the `data/inputs` folder
2. Run the main script:
  ```bash
    python src/main.py --all
  ```
4. The full flow will follow: `extraction -> filtering -> demos`
5. Each result will be stored in its corresponding folder: `data/clean_inputs -> data/outputs -> data/exclusions_outputs -> data/demo_outputs`

---

## 🖥️ Quick Usage

### Fully automated flow

```powershell
python src/main.py --all
```

### Main options
- `--all`           Runs the full flow: cleaning → scraping → exclusion → demo
- `--extract`       Only web extraction
- `--filter`        Only exclusion filtering
- `--demo`          Only demo generation
- `--overwrite`     Forces reprocessing of already processed files
- `--test`          Processes only 20 rows per file (test mode)
- `--wait-timeout`  Page wait timeout (seconds)
- `--resume`        Resumes incomplete or failed files/URLs
- `--clean-logs`    Cleans all files in the logs folder (requires confirmation)

### Advanced usage example
```powershell
python src/main.py --all --overwrite --test --wait-timeout 15
```

---

## 📝 Extracting information with FicherosDatos

This script scans country folders within a network path, locates Excel files, extracts specific metrics from the "statistics" sheet of each file, associates up to three available JPG images, and generates a summary Excel file with all that information.

- Run it to apply this code and get the data in an Excel file:
```bash
  python src/scripts/ficheros_datos.py
```
- You will get the results in `data/outputs` for review.

---

## 🧠 Advanced Features

- **Smart resuming:** If the process is interrupted, you can resume exactly where it left off with `--resume`.
- **State control:** The progress of each file and stage is saved in `/logs/status.json`.
- **Error logs:** All errors are recorded in `/logs/error_log.txt` with details.
- **Automatic parallelism:** The system adjusts the number of threads according to your hardware.
- **Flexible configuration:** You can customize columns, exclusions, and order in `/config/txt_config/`.

---

## 📝 Customization and configuration
- Edit the files in `/config/txt_config/` to:
  - Remove unnecessary columns
  - Rename columns
  - Define column order
  - Configure email exclusion lists

---

## 🛠️ Main module structure

- **src/main.py**: Main CLI and flow orchestrator.
- **src/extractor/**: Web extraction, cleaning, and Excel generation.
- **src/cleaner/**: Email filtering by exclusion.
- **src/demo/**: Masking/anonymous for demo files.
- **src/utils/status_manager.py**: State and log management for resuming and error control.

---

## ❓ FAQ

- **Can I resume if the process is interrupted?**
  Yes, run the same command with `--resume` and the system will continue where it left off.
- **How do I clean the logs and state to start from scratch?**
  Run: `python src/main.py --clean-logs`
- **Can I customize the scraping?**
  Yes, adjust the parameters via CLI or edit the configuration in `/config/txt_config/`.

---

## 📄 License
This project is private and its use is restricted to the terms agreed by the owner.

---

