"""
Script de verificação de ambiente para o app Baixar Músicas.
Verifica ffmpeg, .env, dependências e variáveis obrigatórias.
"""
import os
import sys
import subprocess
from pathlib import Path

REQUIRED_ENV_VARS = ['YOUTUBE_API_KEY']
REQUIRED_LIBS = [
    'PyQt5', 'yt_dlp', 'googleapiclient.discovery', 'google.auth',
    'google_auth_oauthlib', 'google_auth_httplib2', 'requests',
    'bs4', 'tqdm', 'PIL', 'dotenv', 'ffmpeg'
]

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'


def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print('ffmpeg: OK')
    except Exception:
        print('ffmpeg não encontrado no PATH. Instale e adicione ao PATH.')


def check_env():
    if not ENV_PATH.exists():
        print(f'.env não encontrado em {ENV_PATH}. Copie de .env.example e preencha.')
    else:
        print('.env: OK')
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=ENV_PATH)
        for var in REQUIRED_ENV_VARS:
            if not os.getenv(var):
                print(f'Variável obrigatória {var} ausente no .env')
            else:
                print(f'{var}: OK')


def check_libs():
    for lib in REQUIRED_LIBS:
        try:
            __import__(lib.split('.')[0])
            print(f'{lib}: OK')
        except ImportError:
            print(f'{lib}: NÃO INSTALADO')


def main():
    print('--- Checagem de Ambiente ---')
    check_ffmpeg()
    check_env()
    check_libs()
    print('--- Fim da checagem ---')

if __name__ == '__main__':
    main()
