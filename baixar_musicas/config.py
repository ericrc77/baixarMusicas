"""
Módulo de configuração centralizada do app.
Lê variáveis do .env, define paths e constantes globais.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do .env
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)

# Diretórios principais
ASSETS_DIR = BASE_DIR / 'assets'
IMAGES_DIR = ASSETS_DIR / 'images'
DOWNLOADS_DIR = BASE_DIR / 'downloads'
LOGS_DIR = BASE_DIR / 'logs'

# Arquivos
LOG_FILE = LOGS_DIR / 'app.log'

# Variáveis de ambiente
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')

# Outras constantes
APP_NAME = 'Baixar Músicas'
VERSION = '1.0.0'

# Cria diretórios se não existirem
def ensure_dirs():
    for d in [ASSETS_DIR, IMAGES_DIR, DOWNLOADS_DIR, LOGS_DIR]:
        os.makedirs(d, exist_ok=True)

ensure_dirs()
