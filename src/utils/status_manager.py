"""
status_manager.py - Manejo de estado y errores persistente para reanudación de etapas y scraping.
"""
import json
import os
from datetime import datetime
from pathlib import Path

STATUS_PATH = Path(__file__).resolve().parent.parent.parent / 'logs' / 'status.json'
ERROR_LOG_PATH = Path(__file__).resolve().parent.parent.parent / 'logs' / 'error_log.txt'


def load_status():
    if STATUS_PATH.exists():
        with open(STATUS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_status(status):
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS_PATH, 'w', encoding='utf-8') as f:
        json.dump(status, f, indent=2, ensure_ascii=False)

def update_status(filename, stage, value, extra=None):
    status = load_status()
    if filename not in status:
        status[filename] = {
            "cleaned": False,
            "scraped": False,
            "scraping_index": 0,
            "excluded": False,
            "demo_generated": False
        }
    status[filename][stage] = value
    if extra:
        status[filename].update(extra)
    save_status(status)

def get_next_scraping_index(filename):
    status = load_status()
    if filename in status:
        return status[filename].get("scraping_index", 0)
    return 0

def is_stage_done(filename, stage):
    status = load_status()
    return status.get(filename, {}).get(stage, False)

def log_error(filename, stage, url, error):
    ERROR_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ERROR_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().isoformat()}] Archivo: {filename} | Etapa: {stage} | URL: {url} | Error: {error}\n")
