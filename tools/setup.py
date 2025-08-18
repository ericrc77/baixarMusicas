"""
Script de setup para instalar dependências, criar .env exemplo e checar ffmpeg.
"""
import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_EXAMPLE = BASE_DIR / '.env.example'
ENV_FILE = BASE_DIR / '.env'
REQUIREMENTS = BASE_DIR / 'requirements.txt'

print('Instalando dependências...')
os.system(f'pip install -r "{REQUIREMENTS}"')

if not ENV_FILE.exists() and ENV_EXAMPLE.exists():
    print('Copiando .env.example para .env')
    with open(ENV_EXAMPLE, 'r') as src, open(ENV_FILE, 'w') as dst:
        dst.write(src.read())

print('Checando ffmpeg...')
try:
    subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print('ffmpeg: OK')
except Exception:
    print('ffmpeg não encontrado no PATH. Instale e adicione ao PATH.')

print('Setup concluído.')
