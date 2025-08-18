import sys
import os
from typing import List
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel, QFileDialog, QProgressBar, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QThreadPool
from src.downloader import DownloadTask, DownloadSignals, sanitize_filename
from src.config_manager import ConfigManager
import logging


from src.config_manager import ConfigManager
LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'app.log')
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

class DownloadWidget(QWidget):
    def __init__(self, index: int, filename: str):
        super().__init__()
        self.layout = QHBoxLayout()
        self.label = QLabel(filename)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.pause_btn = QPushButton("⏸")
        self.pause_btn.setToolTip("Pausar download")
        self.resume_btn = QPushButton("▶")
        self.resume_btn.setToolTip("Retomar download")
        self.resume_btn.setVisible(False)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progress)
        self.layout.addWidget(self.pause_btn)
        self.layout.addWidget(self.resume_btn)
        self.setLayout(self.layout)

        self._pause_callback = None
        self._resume_callback = None
        self.pause_btn.clicked.connect(self._on_pause)
        self.resume_btn.clicked.connect(self._on_resume)

    def set_pause_resume_callbacks(self, pause_cb, resume_cb):
        self._pause_callback = pause_cb
        self._resume_callback = resume_cb

    def _on_pause(self):
        if self._pause_callback:
            self._pause_callback()
        self.set_paused(True)

    def _on_resume(self):
        if self._resume_callback:
            self._resume_callback()
        self.set_paused(False)

    def set_paused(self, paused: bool):
        self.pause_btn.setVisible(not paused)
        self.resume_btn.setVisible(paused)

    def set_progress(self, percent: int):
        self.progress.setValue(percent)


from src.search.youtube_search import buscar_artista_youtube, buscar_musicas_populares
from src.models.artist import Artist
from src.models.music import Music


from PyQt6.QtGui import QPalette, QColor, QFont

from PyQt6.QtGui import QPixmap, QIcon
class MainWindow(QWidget):


    def toggle_theme(self):
        if self.is_dark_theme:
            self.apply_light_theme()
            self.theme_toggle_btn.setText("☀️")
        else:
            self.apply_dark_theme()
            self.theme_toggle_btn.setText("🌙")
        self.is_dark_theme = not self.is_dark_theme

    def apply_dark_theme(self):
        self.setStyleSheet('''
            QWidget { background-color: #181818; color: #f1f1f1; font-family: Arial, sans-serif; font-size: 14px; }
            QLabel { color: #f1f1f1; font-weight: 500; }
            QLineEdit, QTextEdit, QListWidget, QProgressBar {
                background: #232323; color: #fff; border-radius: 8px; font-size: 14px; border: 1px solid #333;
            }
            QPushButton { background: #222; color: #fff; border-radius: 8px; padding: 6px 18px; font-weight: bold; }
            QPushButton:hover { background: #333; }
            QProgressBar { text-align: center; font-weight: bold; }
        ''')

    def apply_light_theme(self):
        self.setStyleSheet('''
            QWidget { background-color: #f5f5f5; color: #222; font-family: Arial, sans-serif; font-size: 14px; }
            QLabel { color: #222; font-weight: 500; }
            QLineEdit, QTextEdit, QListWidget, QProgressBar {
                background: #fff; color: #222; border-radius: 8px; font-size: 14px; border: 1px solid #bbb;
            }
            QPushButton { background: #e0e0e0; color: #222; border-radius: 8px; padding: 6px 18px; font-weight: bold; }
            QPushButton:hover { background: #d5d5d5; }
            QProgressBar { text-align: center; font-weight: bold; }
        ''')

    def toggle_theme(self):
        if self.is_dark_theme:
            self.apply_light_theme()
            self.theme_toggle_btn.setText("☀️")
        else:
            self.apply_dark_theme()
            self.theme_toggle_btn.setText("🌙")
        self.is_dark_theme = not self.is_dark_theme

    def apply_dark_theme(self):
        self.setStyleSheet('''
            QWidget { background-color: #181818; color: #f1f1f1; font-family: Arial, sans-serif; font-size: 14px; }
            QLabel { color: #f1f1f1; font-weight: 500; }
            QLineEdit, QTextEdit, QListWidget, QProgressBar {
                background: #232323; color: #fff; border-radius: 8px; font-size: 14px; border: 1px solid #333;
            }
            QPushButton { background: #222; color: #fff; border-radius: 8px; padding: 6px 18px; font-weight: bold; }
            QPushButton:hover { background: #333; }
            QProgressBar { text-align: center; font-weight: bold; }
        ''')

    def apply_light_theme(self):
        self.setStyleSheet('''
            QWidget { background-color: #f5f5f5; color: #222; font-family: Arial, sans-serif; font-size: 14px; }
            QLabel { color: #222; font-weight: 500; }
            QLineEdit, QTextEdit, QListWidget, QProgressBar {
                background: #fff; color: #222; border-radius: 8px; font-size: 14px; border: 1px solid #bbb;
            }
            QPushButton { background: #e0e0e0; color: #222; border-radius: 8px; padding: 6px 18px; font-weight: bold; }
            QPushButton:hover { background: #d5d5d5; }
            QProgressBar { text-align: center; font-weight: bold; }
        ''')
    def __init__(self, config):
        super().__init__()
        self.setWindowTitle("Baixar Músicas - Moderno")
        self.resize(800, 650)
        self.setMinimumSize(600, 500)
        self.config = config
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(self.config.get('max_concurrent_downloads', 3))
        self.download_dir = self.config.get('download_dir', 'downloads')
        self.selected_artist = None
        self.musics = []
        try:
            self.init_ui()
        except Exception as e:
            import traceback
            self.show_critical_error(f"Erro ao iniciar a interface:\n{e}\n{traceback.format_exc()}")

    def show_critical_error(self, msg):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Erro Crítico", msg)
        self.close()


    def init_ui(self):
        from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox, QSizePolicy, QSpacerItem
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.setContentsMargins(24, 18, 24, 18)

        # Top bar com tema
        top_bar = QHBoxLayout()
        self.is_dark_theme = True
        self.theme_toggle_btn = QPushButton("🌙")
        self.theme_toggle_btn.setFixedWidth(36)
        self.theme_toggle_btn.setToolTip("Alternar tema claro/escuro")
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        top_bar.addWidget(self.theme_toggle_btn)
        top_bar.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addLayout(top_bar)
        self.apply_dark_theme()

        # Busca de artista
        busca_group = QGroupBox("Buscar Artista")
        busca_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #444; border-radius: 8px; margin-top: 8px; padding: 8px 8px 8px 8px; }")
        busca_layout = QHBoxLayout()
        self.artist_input = QLineEdit()
        self.artist_input.setPlaceholderText("Digite o nome do artista...")
        self.artist_input.setMinimumWidth(200)
        self.artist_input.setStyleSheet("background: #232323; color: #fff; border-radius: 8px; padding: 8px; font-size: 15px;")
        busca_layout.addWidget(self.artist_input)
        self.artist_search_btn = QPushButton("Buscar")
        self.artist_search_btn.setStyleSheet("background-color: #1db954; color: #fff; border-radius: 8px; padding: 8px 22px; font-weight: bold; font-size: 15px;")
        self.artist_search_btn.clicked.connect(self.on_search_artist)
        busca_layout.addWidget(self.artist_search_btn)
        busca_group.setLayout(busca_layout)
        layout.addWidget(busca_group)

        # Lista de artistas encontrados
        artistas_group = QGroupBox("Artistas encontrados")
        artistas_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #444; border-radius: 8px; margin-top: 8px; padding: 8px 8px 8px 8px; }")
        artistas_layout = QVBoxLayout()
        self.artist_list = QListWidget()
        self.artist_list.setStyleSheet("background: #232323; color: #fff; font-size: 15px; border-radius: 8px;")
        self.artist_list.itemClicked.connect(self.on_artist_selected)
        artistas_layout.addWidget(self.artist_list)
        artistas_group.setLayout(artistas_layout)
        layout.addWidget(artistas_group)

        # Lista de músicas populares
        musicas_group = QGroupBox("Músicas populares encontradas (marque para baixar)")
        musicas_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #444; border-radius: 8px; margin-top: 8px; padding: 8px 8px 8px 8px; }")
        musicas_layout = QVBoxLayout()
        self.music_list = QListWidget()
        self.music_list.setStyleSheet("background: #232323; color: #fff; font-size: 15px; border-radius: 8px;")
        self.music_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        musicas_layout.addWidget(self.music_list)
        musicas_group.setLayout(musicas_layout)
        layout.addWidget(musicas_group)

        # Progresso dos downloads
        progresso_group = QGroupBox("Progresso dos downloads")
        progresso_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #444; border-radius: 8px; margin-top: 8px; padding: 8px 8px 8px 8px; }")
        progresso_layout = QVBoxLayout()
        self.progress_list = QListWidget()
        self.progress_list.setStyleSheet("background: #232323; color: #fff; font-size: 13px; border-radius: 8px;")
        progresso_layout.addWidget(self.progress_list)
        progresso_group.setLayout(progresso_layout)
        layout.addWidget(progresso_group)

        # Botões de download e seleção de pasta
        btns_layout = QHBoxLayout()
        self.download_audio_btn = QPushButton("Baixar Áudio (.mp3)")
        self.download_audio_btn.setStyleSheet("background-color: #1db954; color: #fff; border-radius: 8px; padding: 8px 22px; font-weight: bold; font-size: 15px;")
        self.download_audio_btn.clicked.connect(lambda: self.safe_action(lambda: self.start_artist_downloads('mp3')))
        self.download_video_btn = QPushButton("Baixar Vídeo (.mp4)")
        self.download_video_btn.setStyleSheet("background-color: #0057b8; color: #fff; border-radius: 8px; padding: 8px 22px; font-weight: bold; font-size: 15px;")
        self.download_video_btn.clicked.connect(lambda: self.safe_action(lambda: self.start_artist_downloads('mp4')))
        btns_layout.addWidget(self.download_audio_btn)
        btns_layout.addWidget(self.download_video_btn)
    # Todas as referências antigas a layout.addWidget/addLayout removidas. Apenas widgets do layout moderno são usados.

        # Log do sistema
        log_group = QGroupBox("Logs do sistema")
        log_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #444; border-radius: 8px; margin-top: 8px; padding: 8px 8px 8px 8px; }")
        log_layout = QVBoxLayout()
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("background: #181818; color: #f1f1f1; font-size: 13px; border-radius: 8px; font-family: 'Consolas', 'monospace';")
        log_layout.addWidget(self.log_area)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)


    def safe_action(self, func):
        try:
            func()
        except Exception as e:
            import traceback
            self.log(f"Erro: {e}\n{traceback.format_exc()}")
        # ...continua o restante do método normalmente...

        # Busca de artista
    # Todos os blocos antigos de layout removidos. Apenas widgets do layout moderno com QGroupBox são usados.

    # Removido: chamada duplicada de setLayout/layout antiga

    def start_single_download(self):
        from src.download.yt_dlp_downloader import DownloadItem, baixar_musicas
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText("Informe a URL da música.")
            return
        self.status_label.setText("Preparando download...")
        dest_dir = self.download_dir
        item = DownloadItem("", url, dest_dir, 'mp3')
        def progresso_callback(idx, d):
            if d['status'] == 'downloading':
                percent = d.get('progress', 0)
                if 'total_bytes' in d and 'downloaded_bytes' in d:
                    percent = int(d['downloaded_bytes'] * 100 / d['total_bytes'])
                self.progress_bar.setValue(percent)
                self.status_label.setText(f"Baixando... {percent}%")
            elif d['status'] == 'finished':
                self.progress_bar.setValue(100)
                self.status_label.setText("Download concluído!")
        def log_callback(msg):
            if "Concluído" in msg:
                self.downloaded_list.addItem(self.url_input.text())
        # Download em thread
        from PyQt6.QtCore import QRunnable
        class DownloadRunnable(QRunnable):
            def run(self):
                baixar_musicas([item], lambda i, d: progresso_callback(0, d), log_callback)
        self.progress_bar.setValue(0)
        self.status_label.setText("Baixando...")
        self.threadpool.start(DownloadRunnable())

    def on_search_artist(self):
        try:
            from PyQt6.QtGui import QPixmap, QIcon
            import urllib.request
            nome = self.artist_input.text().strip()
            if not nome:
                self.log("Digite o nome de um artista.")
                return
            self.artist_list.clear()
            self.music_list.clear()
            self.progress_list.clear()
            self.log(f"Buscando artista '{nome}'...")
            artistas = buscar_artista_youtube(nome)
            if not artistas:
                self.log("Nenhum artista encontrado.")
                return
            for a in artistas:
                item = QListWidgetItem(f"{a.name}  |  {a.subscribers} inscritos")
                item.setData(Qt.ItemDataRole.UserRole, a)
                # Baixa e exibe thumbnail
                if hasattr(a, 'thumbnail'):
                    try:
                        data = urllib.request.urlopen(a.thumbnail).read()
                        pixmap = QPixmap()
                        pixmap.loadFromData(data)
                        icon = QIcon(pixmap)
                        item.setIcon(icon)
                    except Exception:
                        pass
                self.artist_list.addItem(item)
            self.log(f"{len(artistas)} artista(s) encontrado(s). Selecione um.")
        except Exception as e:
            import traceback
            self.log(f"Erro na busca: {e}\n{traceback.format_exc()}")

    def on_artist_selected(self, item):
        try:
            artist = item.data(Qt.ItemDataRole.UserRole)
            self.selected_artist = artist
            self.music_list.clear()
            self.progress_list.clear()
            self.log(f"Buscando músicas populares de {artist.name}...")
            qnt = 20
            try:
                qnt = int(self.qnt_input.text())
            except Exception:
                pass
            self.musics = buscar_musicas_populares(artist.channel_id, quantidade=qnt)
            for m in self.musics:
                music_item = QListWidgetItem(m.title)
                music_item.setData(Qt.ItemDataRole.UserRole, m)
                music_item.setCheckState(Qt.CheckState.Checked)
                self.music_list.addItem(music_item)
            self.log(f"{len(self.musics)} músicas populares encontradas.")
        except Exception as e:
            import traceback
            self.log(f"Erro ao buscar músicas: {e}\n{traceback.format_exc()}")

    def choose_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Escolher pasta de download", self.download_dir)
        if dir_path:
            self.download_dir = dir_path
            self.dir_label.setText(f"Pasta: {self.download_dir}")
            self.config.set('download_dir', dir_path)


    def start_artist_downloads(self, formato: str):
        try:
            from src.download.yt_dlp_downloader import DownloadItem, baixar_musicas
            selected = [self.music_list.item(i).data(Qt.ItemDataRole.UserRole)
                        for i in range(self.music_list.count())
                        if self.music_list.item(i).checkState() == Qt.CheckState.Checked]
            if not selected:
                self.log("Nenhuma música selecionada.")
                return
            self.log(f"Iniciando download de {len(selected)} músicas em formato {formato}...")
            artista = self.selected_artist.name if self.selected_artist else "Artista"
            dest_dir = os.path.join(self.download_dir, artista)
            os.makedirs(dest_dir, exist_ok=True)
            # Checa duplicidade
            items = []
            for m in selected:
                filename = f"{m.title}.{formato}"
                filepath = os.path.join(dest_dir, filename)
                if os.path.exists(filepath):
                    self.log(f"Já existe: {filename}, pulando download.")
                    continue
                items.append(DownloadItem(m.title, m.url, dest_dir, formato))
            self.progress_widgets = []
            self.progress_list.clear()
            import threading
            self._download_runnables = []
            for idx, item in enumerate(items):
                w = DownloadWidget(idx, item.title)
                list_item = QListWidgetItem()
                self.progress_list.addItem(list_item)
                self.progress_list.setItemWidget(list_item, w)
                self.progress_widgets.append(w)
                pause_event = threading.Event()
                pause_event.clear()
                # DownloadRunnable com suporte a pausa
                class DownloadRunnable(QRunnable):
                    def __init__(self, item, idx, pause_event):
                        super().__init__()
                        self.item = item
                        self.idx = idx
                        self.pause_event = pause_event
                    def set_paused(self, paused):
                        if paused:
                            self.pause_event.set()
                        else:
                            self.pause_event.clear()
                    def run(self):
                        def progresso_hook(i, d):
                            while self.pause_event.is_set():
                                import time; time.sleep(0.2)
                            progresso_callback(self.idx, d)
                        baixar_musicas([self.item], progresso_hook, log_callback)
                runnable = DownloadRunnable(item, idx, pause_event)
                self._download_runnables.append(runnable)
                w.set_pause_resume_callbacks(
                    lambda e=pause_event, r=runnable: (e.set(), r.set_paused(True)),
                    lambda e=pause_event, r=runnable: (e.clear(), r.set_paused(False))
                )
                self.threadpool.start(runnable)

            def progresso_callback(idx, d):
                if d['status'] == 'downloading':
                    percent = d.get('progress', 0)
                    if 'total_bytes' in d and 'downloaded_bytes' in d:
                        percent = int(d['downloaded_bytes'] * 100 / d['total_bytes'])
                    self.progress_widgets[idx].set_progress(percent)
                elif d['status'] == 'finished':
                    self.progress_widgets[idx].set_progress(100)

            def log_callback(msg):
                self.log(msg)

            from PyQt6.QtCore import QRunnable
            class DownloadRunnable(QRunnable):
                def __init__(self, item, idx):
                    super().__init__()
                    self.item = item
                    self.idx = idx
                def run(self):
                    baixar_musicas([self.item], lambda i, d: progresso_callback(self.idx, d), log_callback)

            for idx, item in enumerate(items):
                runnable = DownloadRunnable(item, idx)
                self.threadpool.start(runnable)
        except Exception as e:
            import traceback
            self.log(f"Erro ao iniciar downloads: {e}\n{traceback.format_exc()}")

    def log(self, msg: str):
        self.log_area.append(msg)
        logging.info(msg)

    # Remover bloco duplicado e garantir escopo correto de dir_path

    def start_downloads(self):
        links = [l.strip() for l in self.links_input.toPlainText().splitlines() if l.strip()]
        if not links:
            self.log("Nenhum link informado.")
            return
        self.progress_list.clear()
        self.widgets = []
        for idx, link in enumerate(links):
            filename = sanitize_filename(link.split('/')[-1])
            dest = os.path.join(self.download_dir, filename)
            widget = DownloadWidget(idx, filename)
            item = QListWidgetItem()
            self.progress_list.addItem(item)
            self.progress_list.setItemWidget(item, widget)
            self.widgets.append(widget)
            signals = DownloadSignals()
            signals.progress.connect(widget.set_progress)
            signals.finished.connect(lambda i, s: self.log(f"{links[i]}: {s}"))
            signals.error.connect(lambda i, e: self.log(f"{links[i]}: {e}"))
            task = DownloadTask(link, dest, idx, signals)
            self.threadpool.start(task)
            self.log(f"Iniciando download: {link}")

    def log(self, msg: str):
        self.log_area.append(msg)
        logging.info(msg)

def run_app():
    app = QApplication(sys.argv)
    config = ConfigManager()
    window = MainWindow(config)
    window.resize(700, 500)
    window.show()
    sys.exit(app.exec())
