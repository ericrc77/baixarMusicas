
import os
from typing import Optional
from dotenv import load_dotenv, set_key

def baixar_imagens_bob_marley(pasta_destino: str) -> list[str]:
	"""
	Baixa imagens do Bob Marley (banner, ícone, capa) se não existirem.
	Args:
		pasta_destino (str): Caminho da pasta onde salvar as imagens.
	Returns:
		list[str]: Lista de nomes de imagens baixadas.
	"""
	import requests
	imagens = [
		{
			'nome': 'banner.jpg',
			'url': 'https://upload.wikimedia.org/wikipedia/commons/9/9e/Bob-Marley-in-Concert_zurich_05-30-80_%28cropped%29.jpg'
		},
		{
			'nome': 'icone.jpg',
			'url': 'https://upload.wikimedia.org/wikipedia/commons/5/5e/Bob_Marley_1979.jpg'
		},
		{
			'nome': 'capa.jpg',
			'url': 'https://upload.wikimedia.org/wikipedia/commons/2/2e/Bob_Marley_1977.jpg'
		}
	]
	os.makedirs(pasta_destino, exist_ok=True)
	baixadas = []
	for img in imagens:
		caminho = os.path.join(pasta_destino, img['nome'])
		if not os.path.exists(caminho):
			r = requests.get(img['url'], timeout=10)
			with open(caminho, 'wb') as f:
				f.write(r.content)
			baixadas.append(img['nome'])
	return baixadas

def carregar_api_key() -> Optional[str]:
	"""
	Carrega a chave da API do YouTube de forma resiliente.
	Ordem de busca:
		1. Variável de ambiente YOUTUBE_API_KEY
		2. .env na raiz do projeto
		3. .env ou .env.txt em ~/Desktop/Senhas
	Returns:
		str | None: A chave da API, se encontrada.
	"""
	# 1. Variável de ambiente
	api_key = os.environ.get('YOUTUBE_API_KEY')
	if api_key:
		return api_key

	# 2. .env na raiz do projeto
	env_local = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
	if os.path.exists(env_local):
		load_dotenv(env_local)
		api_key = os.environ.get('YOUTUBE_API_KEY')
		if api_key:
			return api_key

	# 3. .env ou .env.txt em ~/Desktop/Senhas
	desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
	env_dir = os.path.join(desktop, 'Senhas')
	env_path = os.path.join(env_dir, '.env')
	env_path_txt = os.path.join(env_dir, '.env.txt')
	for path in [env_path, env_path_txt]:
		if os.path.exists(path):
			load_dotenv(path)
			api_key = os.environ.get('YOUTUBE_API_KEY')
			if api_key:
				return api_key

	# Não encontrada
	return None

def salvar_api_key(api_key: str) -> bool:
	"""
	Salva a chave da API no arquivo .env na raiz do projeto.
	Args:
		api_key (str): Chave da API a ser salva.
	Returns:
		bool: True se salvou com sucesso, False caso contrário.
	"""
	env_local = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
	try:
		if not os.path.exists(env_local):
			with open(env_local, 'w', encoding='utf-8') as f:
				f.write('YOUTUBE_API_KEY=' + api_key + '\n')
		else:
			set_key(env_local, 'YOUTUBE_API_KEY', api_key)
		return True
	except Exception as e:
		return False

