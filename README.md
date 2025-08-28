# YouTube Music Downloader

Este é um aplicativo desktop robusto e amigável, desenvolvido em Python com Tkinter (usando `ttk` para uma interface moderna), que permite pesquisar e baixar músicas e vídeos do YouTube. Ele foi projetado para uso pessoal e educacional, com foco em uma experiência de usuário aprimorada.

## Funcionalidades

- **Interface Moderna:** Utiliza `ttk` com temas modernos para uma experiência visual agradável.
- **Busca Avançada:**
  - Pesquisa de vídeos do YouTube por artista, com filtros inteligentes para priorizar canais oficiais/verificados.
  - Fallback automático para `yt-dlp` em caso de falha da API do YouTube, garantindo resultados.
  - Opção de ignorar vídeos com menos de um número configurável de visualizações.
- **Resultados Detalhados:** Exibição de resultados em uma tabela interativa (`ttk.Treeview`) com colunas para: checkbox de seleção, Título, Canal, Duração e Views.
- **Controle de Seleção:** Botões para selecionar todos ou limpar a seleção de vídeos.
- **Downloads Flexíveis:**
  - Download em formato MP3 ou MP4.
  - Opções de qualidade para MP4 (360p, 720p, 1080p).
  - Gerenciamento de downloads em fila, com barra de progresso global e logs detalhados.
  - Histórico de músicas baixadas salvo em `downloads/history.json`.
- **Gerenciamento de Arquivos:** Botão para abrir a pasta de downloads com um clique.
- **Configurações Persistentes:** Salva as últimas configurações do usuário (artista, formato, qualidade, concorrência, views mínimas) em `config.json`.
- **Atalhos de Teclado:** Atalhos para buscar (`Enter`) e selecionar todos os vídeos (`Ctrl+A`).
- **Informações do Aplicativo:** Botão "Sobre" com detalhes da versão, autor e aviso legal.
- **Logs Claros:** Área de log com estilo de console (fundo escuro, texto claro) para feedback em tempo real.

## Estrutura do Projeto

```
novoProjeto/
  app.py             # Interface gráfica principal e lógica de interação do usuário
  youtube_api.py     # Lógica de interação com a YouTube Data API e fallback yt-dlp
  downloader.py      # Lógica de download de áudio/vídeo e gerenciamento de histórico
  utils.py           # Funções utilitárias (carregar .env, gerenciar config.json, etc.)
  requirements.txt   # Dependências do Python
  README.md          # Este arquivo
  .env.example       # Exemplo de arquivo de configuração de variáveis de ambiente
  config.json        # Arquivo para salvar as configurações do usuário
  icon.png           # Ícone do aplicativo
  downloads/         # Pasta para salvar os arquivos baixados
    history.json     # Histórico de downloads
```

## Instalação e Configuração

### 1. Pré-requisitos

Certifique-se de ter o Python 3.x e o `yt-dlp` instalados em seu sistema. Para instalar `yt-dlp`, siga as instruções em [yt-dlp/README.md](https://github.com/yt-dlp/yt-dlp/blob/master/README.md#installation).

### 2. Clonar o Repositório (ou criar a estrutura de arquivos)

Se você recebeu o projeto como um arquivo zip, descompacte-o. Caso contrário, crie a estrutura de pastas e arquivos conforme a seção "Estrutura do Projeto" acima.

### 3. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (`novoProjeto/`) baseado no `.env.example`:

```bash
cp .env.example .env
```

Abra o arquivo `.env` e substitua `SUA_CHAVE_DA_API_AQUI` pela sua chave da YouTube Data API v3 (opcional, mas recomendado para melhor desempenho e menos falhas).

```ini
YOUTUBE_API_KEY=SUA_CHAVE_DA_API_AQUI
DOWNLOAD_DIR=downloads
MAX_CONCURRENCY=3
```

- `YOUTUBE_API_KEY`: Sua chave da API do YouTube. Veja como obtê-la na próxima seção. Se não for fornecida, o aplicativo usará apenas `yt-dlp` para buscas.
- `DOWNLOAD_DIR`: Diretório onde os arquivos serão salvos (padrão: `downloads`).
- `MAX_CONCURRENCY`: Número máximo de downloads simultâneos (padrão: `3`).

### 4. Como Obter a Chave da YouTube Data API (Opcional)

1. Vá para o [Google Cloud Console](https://console.cloud.google.com/).
2. Crie um novo projeto ou selecione um existente.
3. No menu de navegação, vá para **APIs e Serviços > Biblioteca**.
4. Procure por "YouTube Data API v3" e habilite-a.
5. Vá para **APIs e Serviços > Credenciais**.
6. Clique em "Criar Credenciais" e selecione "Chave de API".
7. Copie a chave gerada e cole-a no seu arquivo `.env`.

### 5. Instalar Dependências

Navegue até a pasta `novoProjeto` no terminal e instale as dependências usando pip:

```bash
pip install -r requirements.txt
```

## Como Rodar o Aplicativo

Após instalar as dependências e configurar sua chave de API (opcional), você pode executar o aplicativo a partir da pasta `novoProjeto`:

```bash
python app.py
```

## Avisos Importantes

**Uso Pessoal e Ética:** Este aplicativo é fornecido apenas para fins educacionais e de uso pessoal. O download de conteúdo do YouTube pode violar os Termos de Serviço do YouTube e os direitos autorais dos criadores de conteúdo. Certifique-se de ter os direitos ou permissões necessárias para baixar e usar qualquer material. O desenvolvedor deste aplicativo não se responsabiliza por qualquer uso indevido.

**DRM e Login:** Este aplicativo não contorna tecnologias de Gerenciamento de Direitos Digitais (DRM) nem realiza login automatizado em contas do YouTube.

## Screenshots

(Serão adicionadas aqui após a validação final do aplicativo.)


