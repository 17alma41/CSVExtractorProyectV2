"""
settings.py - Configuración centralizada de rutas y constantes del proyecto
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUTS_DIR = DATA_DIR / "inputs"
OUTPUTS_DIR = DATA_DIR / "outputs"
CLEAN_INPUTS_DIR = DATA_DIR / "clean_inputs"
LOGS_DIR = BASE_DIR / "logs"  
CONFIG_DIR = BASE_DIR / "config"
TXT_CONFIG_DIR = CONFIG_DIR / "txt_config"
EXCLUSIONES_FOLDER = TXT_CONFIG_DIR / "xclusiones_email"
XCLUSION_INPUTS_DIR = OUTPUTS_DIR  # Usar data/outputs como entrada para exclusión
XCLUSION_OUTPUTS_DIR = DATA_DIR / "exclusions_outputs"  # Usar data/exclusions_outputs como salida
DEMO_INPUTS_DIR = XCLUSION_OUTPUTS_DIR  # Usar exclusiones_outputs como entrada para demo
DEMO_OUTPUTS_DIR = DATA_DIR / "demo_outputs"  # Usar data/demo_outputs como salida

# Hojas y otros nombres comunes
HOJA_DATA = "data"
HOJA_STATS = "statistics"
IMAGE_SIZE = (1200, 630)
