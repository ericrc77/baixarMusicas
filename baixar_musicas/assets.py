"""
Gerenciamento de imagens e ícones do app.
Baixa imagens automaticamente se não existirem, com fallback local.
"""
import os
from pathlib import Path
from urllib.request import urlretrieve
from .config import IMAGES_DIR, get_logger

IMAGES = {
    'banner': {
        'filename': 'banner.jpg',
        'url': 'https://i.imgur.com/0Z8FQyM.jpg',  # Exemplo Bob Marley
    },
    'capa': {
        'filename': 'capa.jpg',
        'url': 'https://i.imgur.com/0Z8FQyM.jpg',
    },
    'icone': {
        'filename': 'icone.jpg',
        'url': 'https://i.imgur.com/0Z8FQyM.jpg',
    },
}

logger = get_logger('assets')

def ensure_images():
    for key, info in IMAGES.items():
        path = IMAGES_DIR / info['filename']
        if not path.exists():
            try:
                urlretrieve(info['url'], path)
                logger.info(f"Imagem '{info['filename']}' baixada com sucesso.")
            except Exception as e:
                logger.error(f"Falha ao baixar {info['filename']}: {e}")
                # Fallback: cria arquivo vazio para não quebrar UI
                with open(path, 'wb') as f:
                    f.write(b'')
                logger.warning(f"Imagem '{info['filename']}' criada vazia (fallback).")

ensure_images()
