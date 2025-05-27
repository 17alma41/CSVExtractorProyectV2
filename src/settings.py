"""
settings.py - Configuración centralizada de rutas y constantes del proyecto
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUTS_DIR = DATA_DIR / "inputs"
OUTPUTS_DIR = DATA_DIR / "outputs"
LOGS_DIR = DATA_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"
TXT_CONFIG_DIR = CONFIG_DIR / "txt_config"
CLEAN_INPUTS_DIR = DATA_DIR / "clean_inputs"
XCLUSION_INPUTS_DIR = DATA_DIR / "xclusion" / "xclusiones"
XCLUSION_OUTPUTS_DIR = DATA_DIR / "xclusion" / "xclusiones_outputs"
DEMO_INPUTS_DIR = DATA_DIR / "demo" / "demo_inputs"
DEMO_OUTPUTS_DIR = DATA_DIR / "demo" / "demo_outputs"

# Hojas y otros nombres comunes
HOJA_DATA = "data"
HOJA_STATS = "statistics"
IMAGE_SIZE = (1200, 630)
