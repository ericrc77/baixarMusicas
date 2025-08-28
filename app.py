import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
import threading
import webbrowser

from youtube_api import search_videos
from downloader import download_many
from utils import load_environment, get_download_dir, get_max_concurrency, truncate_title, load_config, save_config

class YouTubeDownloaderApp:
    """A classe principal para o aplicativo YouTube Music Downloader."""
    def __init__(self, master):
        """Inicializa o aplicativo."""
        self.master = master
        master.title("YouTube Music Downloader")
        master.geometry("900x750")
        master.iconphoto(False, tk.PhotoImage(file="icon.png"))

        # Apply a modern theme
        style = ttk.Style()
        style.theme_use("clam") # You can try other themes like \'alt\', \'default\', \'classic\'

        load_environment()
        self.download_dir = get_download_dir()
        self.max_concurrency = get_max_concurrency()
        self.config = load_config()

        # Create downloads directory if it doesn\\\\\\'t exist
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

        self.create_widgets()
        self.load_user_settings()
        self.log_message("Aplicativo iniciado. Insira um artista para buscar.")

        # Bind close event to save settings
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """Cria e posiciona os widgets na janela principal."""
        # Main Frame
        main_frame = ttk.Frame(self.master, padding="10 10 10 10")
        main_frame.pack(fill="both", expand=True)

        # Search Frame
        search_frame = ttk.LabelFrame(main_frame, text="Buscar Músicas", padding="10 10 10 10")
        search_frame.pack(padx=5, pady=5, fill="x")

        ttk.Label(search_frame, text="Artista:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.artist_entry = ttk.Entry(search_frame, width=40)
        self.artist_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.artist_entry.bind("<Return>", lambda event: self.perform_search())

        ttk.Label(search_frame, text="Resultados:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.limit_entry = ttk.Entry(search_frame, width=10)
        self.limit_entry.insert(0, "20")
        self.limit_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(search_frame, text="Concorrência:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.concurrency_entry = ttk.Entry(search_frame, width=10)
        self.concurrency_entry.insert(0, str(self.max_concurrency))
        self.concurrency_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(search_frame, text="Formato:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.format_var = tk.StringVar(value="mp3")
        ttk.Radiobutton(search_frame, text="MP3", variable=self.format_var, value="mp3").grid(row=3, column=1, sticky="w")
        ttk.Radiobutton(search_frame, text="MP4", variable=self.format_var, value="mp4").grid(row=3, column=1, padx=60, sticky="w")

        self.quality_var = tk.StringVar(value="720") # Default quality
        ttk.Radiobutton(search_frame, text="360p", variable=self.quality_var, value="360").grid(row=3, column=1, padx=120, sticky="w")
        ttk.Radiobutton(search_frame, text="720p", variable=self.quality_var, value="720").grid(row=3, column=1, padx=180, sticky="w")
        ttk.Radiobutton(search_frame, text="1080p", variable=self.quality_var, value="1080").grid(row=3, column=1, padx=240, sticky="w")

        ttk.Label(search_frame, text="Views Mínimas:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.min_views_entry = ttk.Entry(search_frame, width=10)
        self.min_views_entry.insert(0, "0")
        self.min_views_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        self.search_button = ttk.Button(search_frame, text="Buscar", command=self.perform_search)
        self.search_button.grid(row=0, column=2, rowspan=5, padx=10, pady=5, sticky="ns")

        search_frame.columnconfigure(1, weight=1)

        # Results Frame
        results_frame = ttk.LabelFrame(main_frame, text="Resultados da Busca", padding="10 10 10 10")
        results_frame.pack(padx=5, pady=5, fill="both", expand=True)

        self.results_tree = ttk.Treeview(results_frame, columns=("checkbox", "title", "channel", "duration", "views"), show="headings")
        self.results_tree.heading("checkbox", text="✅")
        self.results_tree.heading("title", text="Título")
        self.results_tree.heading("channel", text="Canal")
        self.results_tree.heading("duration", text="Duração")
        self.results_tree.heading("views", text="Views")
        self.results_tree.column("checkbox", width=30, anchor="center")
        self.results_tree.column("title", width=300)
        self.results_tree.column("channel", width=150)
        self.results_tree.column("duration", width=80, anchor="center")
        self.results_tree.column("views", width=100, anchor="center")
        self.results_tree.pack(fill="both", expand=True)

        self.results_tree.bind("<Button-1>", self.on_tree_click)
        self.master.bind("<Control-a>", lambda event: self.select_all_results())
        self.master.bind("<Control-A>", lambda event: self.select_all_results())
        # Select All/None buttons
        select_buttons_frame = ttk.Frame(results_frame)
        select_buttons_frame.pack(pady=5)
        ttk.Button(select_buttons_frame, text="Selecionar Todos", command=self.select_all_results).pack(side="left", padx=5)
        ttk.Button(select_buttons_frame, text="Limpar Seleção", command=self.clear_selection).pack(side="left", padx=5)

        # Downloads Frame
        downloads_frame = ttk.LabelFrame(main_frame, text="Downloads", padding="10 10 10 10")
        downloads_frame.pack(padx=5, pady=5, fill="x")

        self.download_button = ttk.Button(downloads_frame, text="Baixar Selecionados", command=self.perform_download)
        self.download_button.pack(side="left", padx=5)

        self.open_folder_button = ttk.Button(downloads_frame, text="Abrir Pasta de Downloads", command=self.open_download_folder)
        self.open_folder_button.pack(side="left", padx=5)

        self.about_button = ttk.Button(downloads_frame, text="Sobre", command=self.show_about_dialog)
        self.about_button.pack(side="left", padx=5)
        # Global Progress Bar
        ttk.Label(downloads_frame, text="Progresso Global:").pack(side="left", padx=5)
        self.progress_bar = ttk.Progressbar(downloads_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(side="left", padx=5, fill="x", expand=True)

        # Log Area
        log_frame = ttk.LabelFrame(main_frame, text="Log de Atividades", padding="10 10 10 10")
        log_frame.pack(padx=5, pady=5, fill="both", expand=True)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state="disabled", background="#333333", foreground="#FFFFFF", insertbackground="#FFFFFF")
        self.log_text.pack(fill="both", expand=True)

        # Copyright Notice
        copyright_notice = "Aviso: Baixar conteúdo do YouTube pode violar os Termos de Serviço e direitos autorais. Este aplicativo é para uso pessoal e educacional."
        ttk.Label(main_frame, text=copyright_notice, foreground="red", wraplength=880, justify="center").pack(pady=5)

    def log_message(self, message):
        """Exibe uma mensagem na área de log."""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def load_user_settings(self):
        """Carrega as configurações do usuário do arquivo config.json."""
        if "last_artist" in self.config:
            self.artist_entry.delete(0, tk.END)
            self.artist_entry.insert(0, self.config["last_artist"])
        if "last_format" in self.config:
            self.format_var.set(self.config["last_format"])
        if "last_quality" in self.config:
            self.quality_var.set(self.config["last_quality"])
        if "last_concurrency" in self.config:
            self.concurrency_entry.delete(0, tk.END)
            self.concurrency_entry.insert(0, self.config["last_concurrency"])
        if "last_min_views" in self.config:
            self.min_views_entry.delete(0, tk.END)
            self.min_views_entry.insert(0, self.config["last_min_views"])

    def save_user_settings(self):
        """Salva as configurações do usuário no arquivo config.json."""
        self.config["last_artist"] = self.artist_entry.get()
        self.config["last_format"] = self.format_var.get()
        self.config["last_quality"] = self.quality_var.get()
        self.config["last_concurrency"] = self.concurrency_entry.get()
        self.config["last_min_views"] = self.min_views_entry.get()
        save_config(self.config)

    def on_closing(self):
        """Salva as configurações e fecha o aplicativo."""
        self.save_user_settings()
        self.master.destroy()

    def show_about_dialog(self):
        """Exibe a caixa de diálogo \"Sobre\"."""
        about_text = (
            "YouTube Music Downloader\n\n"
            "Versão: 1.0\n"
            "Autor: Manus\n\n"
            "Aviso: Baixar conteúdo do YouTube pode violar os Termos de Serviço e direitos autorais. "
            "Este aplicativo é fornecido apenas para uso pessoal e educacional. "
            "O desenvolvedor não se responsabiliza por qualquer uso indevido."
        )
        messagebox.showinfo("Sobre", about_text)

    def perform_search(self):
        """Inicia a busca de vídeos com base nos critérios inseridos."""
        artist = self.artist_entry.get()
        if not artist:
            messagebox.showwarning("Entrada Inválida", "Por favor, insira o nome de um artista.")
            return

        try:
            limit = int(self.limit_entry.get())
            min_views = int(self.min_views_entry.get())
        except ValueError:
            messagebox.showwarning("Entrada Inválida", "O limite de resultados e as visualizações mínimas devem ser números.")
            return

        self.log_message(f"Buscando vídeos para \\\\\' {artist}\\\\\\'...")
        self.search_button.config(state="disabled")
        self.results_tree.delete(*self.results_tree.get_children())
        
        threading.Thread(target=self._search_thread, args=(artist, limit, min_views)).start()

    def _search_thread(self, artist, limit, min_views):
        """Executa a busca em uma thread separada para não bloquear a UI."""
        try:
            videos = search_videos(artist, limit, min_views)
            self.master.after(0, self._update_results_tree, videos)
            self.master.after(0, lambda: self.log_message(f"Busca concluída. Encontrados {len(videos)} vídeos."))
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Erro de Busca", f"Ocorreu um erro durante a busca: {e}"))
        finally:
            self.master.after(0, lambda: self.search_button.config(state="normal"))

    def _update_results_tree(self, videos):
        """Atualiza a árvore de resultados com os vídeos encontrados."""
        self.video_data = {}
        for i, video in enumerate(videos):
            item_id = self.results_tree.insert("", "end", iid=i, values=("", truncate_title(video["title"]), video["channelTitle"], video["duration"], video["views"]))
            self.results_tree.item(item_id, tags=("unchecked",))
            self.video_data[item_id] = video

    def on_tree_click(self, event):
        """Alterna a seleção de um item na árvore de resultados."""
        item_id = self.results_tree.identify_row(event.y)
        if item_id:
            current_tags = self.results_tree.item(item_id, "tags")
            if "checked" in current_tags:
                self.results_tree.item(item_id, tags=("unchecked",))
                self.results_tree.set(item_id, "checkbox", "")
            else:
                self.results_tree.item(item_id, tags=("checked",))
                self.results_tree.set(item_id, "checkbox", "✅")

    def select_all_results(self):
        """Seleciona todos os itens na árvore de resultados."""
        for item_id in self.results_tree.get_children():
            self.results_tree.item(item_id, tags=("checked",))
            self.results_tree.set(item_id, "checkbox", "✅")

    def clear_selection(self):
        """Limpa a seleção de todos os itens na árvore de resultados."""
        for item_id in self.results_tree.get_children():
            self.results_tree.item(item_id, tags=("unchecked",))
            self.results_tree.set(item_id, "checkbox", "")

    def perform_download(self):
        """Inicia o download dos vídeos selecionados."""
        selected_items = [item_id for item_id in self.results_tree.get_children() if "checked" in self.results_tree.item(item_id, "tags")]
        if not selected_items:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione pelo menos um vídeo para baixar.")
            return

        urls_to_download = [self.video_data[item_id]["url"] for item_id in selected_items]
        download_format = self.format_var.get()
        
        try:
            concurrency = int(self.concurrency_entry.get())
        except ValueError:
            messagebox.showwarning("Entrada Inválida", "A concorrência deve ser um número.")
            return

        self.log_message(f"Iniciando download de {len(urls_to_download)} vídeos em formato {download_format}...")
        self.download_button.config(state="disabled")
        self.progress_bar["value"] = 0
        self.progress_bar["maximum"] = len(urls_to_download)

        threading.Thread(target=self._download_thread, args=(urls_to_download, concurrency, download_format, self.quality_var.get())).start()

    def _download_thread(self, urls, concurrency, download_format, quality):
        """Executa o download em uma thread separada para não bloquear a UI."""
        try:
            download_many(
                urls,
                concurrency,
                download_format,
                self.download_dir,
                progress_cb=self._update_progress,
                log_cb=self.log_message,
                quality=quality
            )
            self.master.after(0, lambda: self.log_message("Todos os downloads concluídos!"))
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Erro de Download", f"Ocorreu um erro durante o download: {e}"))
        finally:
            self.master.after(0, lambda: self.download_button.config(state="normal"))

    def _update_progress(self, current, total):
        """Atualiza a barra de progresso global."""
        self.master.after(0, lambda: self.progress_bar.config(value=current))

    def open_download_folder(self):
        """Abre a pasta de downloads no gerenciador de arquivos do sistema."""
        try:
            path = os.path.abspath(self.download_dir)
            if os.path.exists(path):
                webbrowser.open(path)
                self.log_message(f"Abrindo pasta de downloads: {path}")
            else:
                self.log_message(f"Erro: Pasta de downloads não encontrada em {path}")
        except Exception as e:
            self.log_message(f"Erro ao tentar abrir a pasta de downloads: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()


