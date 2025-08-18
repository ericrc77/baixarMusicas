# Baixar Músicas

Aplicativo para buscar artistas no YouTube, listar as músicas mais populares e baixar áudio (.mp3 320kbps) ou vídeo (.mp4 720p) com interface moderna e robusta.

## Requisitos
- Python 3.8+
- ffmpeg instalado e no PATH
- Chave da API do YouTube (YouTube Data API v3)

## Instalação
```sh
pip install -r requirements.txt
```

## Configuração
1. Copie `.env.example` para `.env` e preencha sua chave:
   ```
   cp .env.example .env
   # Edite .env e coloque sua YOUTUBE_API_KEY
   ```
2. Certifique-se de que o ffmpeg está instalado e acessível no PATH.

## Como rodar
```sh
python main.py
```

## Scripts úteis
- `python tools/check_env.py` — Checa dependências, ffmpeg e variáveis do .env
- `python -m app --selftest` — Autoteste de execução
- `make setup` — Instala dependências, cria .env exemplo
- `make run` — Executa o app
- `make test` — Roda os testes

## Funcionalidades
- Busca de artista (prioriza canal oficial)
- Lista top 20 músicas com miniaturas
- Download de áudio (.mp3 320kbps) e vídeo (.mp4 720p)
- Barra de progresso, logs detalhados, botão cancelar
- Evita duplicatas, sanitiza nomes de arquivos/pastas
- Compatível com Windows, Linux e macOS

## Limitações
- Sujeito a limites de quota da API do YouTube
- Requer conexão com a internet para busca e download

## Melhorias implementadas
- Modularização completa
- Logging padronizado (arquivo + console)
- Checagem de ambiente e dependências
- Robustez no tratamento de erros
- Testes automatizados

---

Para dúvidas ou problemas, consulte o log em `logs/app.log` ou abra uma issue.
