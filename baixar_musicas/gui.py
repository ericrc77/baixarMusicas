
def main():
	import sys
	from PyQt5.QtWidgets import QApplication
	app = QApplication(sys.argv)
	win = MainWindow()
	win.show()
	sys.exit(app.exec())


# Lazy import e tratamento de dependências
import sys
import os

def _import_pyqt6():
	try:
		from PyQt5.QtWidgets import (
			QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
			QComboBox, QProgressBar, QTextEdit, QSpinBox, QMessageBox, QDialog, QListWidget, QListWidgetItem, QMenuBar, QMenu, QAction
		)
		from PyQt5.QtCore import Qt
		return (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
				QComboBox, QProgressBar, QTextEdit, QSpinBox, QMessageBox, QDialog, QListWidget, QListWidgetItem, QMenuBar, QMenu, QAction, Qt)
	except ImportError as e:
		import ctypes
		msg = f"Erro ao importar PyQt5:\n{e}\n\nTente rodar:\n    pip install pyqt5\n\nA aplicação será encerrada."
		ctypes.windll.user32.MessageBoxW(0, msg, "Dependência não encontrada", 0)
		sys.exit(1)

def _show_missing_dep_dialog(pkg):
	import ctypes
	msg = f"O pacote '{pkg}' não está instalado.\n\nTente rodar:\n    pip install {pkg.lower()}\n\nA aplicação será encerrada."
	ctypes.windll.user32.MessageBoxW(0, msg, "Dependência não encontrada", 0)


# Importação dinâmica do módulo de API do YouTube
def _import_youtube_api():
	try:
		from .youtube_api import buscar_artista_youtube, buscar_musicas_populares
		return buscar_artista_youtube, buscar_musicas_populares
	except ImportError:
		_show_missing_dep_dialog('yt-dlp, requests, google-api-python-client, python-dotenv, ytmusicapi')
		sys.exit(1)

from .utils import carregar_api_key, salvar_api_key

# Carregar PyQt6 dinamicamente
(
	QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
	QComboBox, QProgressBar, QTextEdit, QSpinBox, QMessageBox, QDialog, QListWidget, QListWidgetItem, QMenuBar, QMenu, QAction, Qt
) = _import_pyqt6()

buscar_artista_youtube, buscar_musicas_populares = _import_youtube_api()

class MainWindow(QWidget):
	"""
	Janela principal da aplicação Baixar Músicas.
	"""
	def on_buscar_artista(self):
		# Verifica API Key antes de buscar
		try:
			api_key = carregar_api_key()
		except Exception as e:
			self.log(f'Erro ao carregar API Key: {e}')
			QMessageBox.critical(self, 'Erro', f'API Key não encontrada ou inválida. Configure em Configurações > API Key.')
			self.abrir_dialogo_api_key()
			return
		if not api_key:
			QMessageBox.warning(self, 'Aviso', 'API Key não configurada. Configure em Configurações > API Key.')
			self.abrir_dialogo_api_key()
			return
		artista = self.artista_input.text().strip()
		if not artista:
			QMessageBox.warning(self, 'Aviso', 'Digite o nome do artista.')
			return
		self.log('Buscando artista...')
		try:
			resultados = buscar_artista_youtube(artista)
		except ImportError as e:
			self.log(f'Dependência ausente: {e}')
			QMessageBox.critical(self, 'Erro', f'Dependência ausente: {e}\nTente rodar: pip install yt-dlp requests google-api-python-client python-dotenv ytmusicapi')
			return
		except Exception as e:
			self.log(f'Erro ao buscar artista: {e}')
			QMessageBox.critical(self, 'Erro', f'Erro ao buscar artista: {e}')
			return
		if not resultados:
			self.log('Nenhum canal musical encontrado.')
			QMessageBox.warning(self, 'Aviso', 'Nenhum canal musical encontrado.')
			return
		# Exibir lista de canais para escolha
		dialog = QDialog(self)
		dialog.setWindowTitle('Escolha o canal do artista')
		vbox = QVBoxLayout()
		label = QLabel('Selecione o canal musical correto:')
		vbox.addWidget(label)
		lista = QListWidget()
		canais_map = {}
		for idx, canal in enumerate(resultados):
			txt = f"{canal['nome']} | Inscritos: {canal['inscritos']} | Categoria: {canal['categoria']} | Fonte: {canal['fonte']}"
			if canal.get('oficial'):
				txt = '⭐ ' + txt
			item = QListWidgetItem(txt)
			lista.addItem(item)
			canais_map[idx] = canal
		vbox.addWidget(lista)
		link_label = QLabel()
		link_label.setOpenExternalLinks(True)
		vbox.addWidget(link_label, alignment=Qt.AlignmentFlag.AlignHCenter)
		def atualizar_info():
			idx = lista.currentRow()
			if idx < 0:
				link_label.clear()
				return
			canal = canais_map[idx]
			link_label.setText(f"<a href='{canal['url']}'>{canal['url']}</a>")
		lista.currentRowChanged.connect(atualizar_info)
		if resultados:
			lista.setCurrentRow(0)
		hbox = QHBoxLayout()
		btn_ok = QPushButton('Confirmar canal')
		btn_cancel = QPushButton('Cancelar')
		hbox.addWidget(btn_ok)
		hbox.addWidget(btn_cancel)
		vbox.addLayout(hbox)
		dialog.setLayout(vbox)
		confirmado = {'canal': None}
		def ok():
			idx = lista.currentRow()
			if idx < 0:
				return
			confirmado['canal'] = canais_map[idx]
			dialog.accept()
		def cancelar():
			confirmado['canal'] = None
			dialog.reject()
		btn_ok.clicked.connect(ok)
		btn_cancel.clicked.connect(cancelar)
		dialog.exec()
		if confirmado['canal']:
			self.artista_encontrado = confirmado['canal']
			self.log(f"Artista confirmado: {confirmado['canal']['nome']} ({confirmado['canal']['url']})")
			self.confirmar_btn.setEnabled(True)
		else:
			self.log('Artista não confirmado. Digite outro nome.')
			def init_ui(self):
				layout = QVBoxLayout()

				# Menu superior
				menubar = QMenuBar(self)
				menu_config = QMenu('Configurações', self)
				acao_api = QAction('API Key...', self)
				acao_api.triggered.connect(self.abrir_dialogo_api_key)
				menu_config.addAction(acao_api)
				menubar.addMenu(menu_config)
				layout.setMenuBar(menubar)

				# Campo de busca do artista
				artista_layout = QHBoxLayout()
				artista_label = QLabel('Artista:')
				self.artista_input = QLineEdit()
				self.artista_input.setPlaceholderText('Digite o nome do artista')
				artista_layout.addWidget(artista_label)
				artista_layout.addWidget(self.artista_input)
				layout.addLayout(artista_layout)

				# Opções de formato
				formato_layout = QHBoxLayout()
				formato_label = QLabel('Formato:')
				self.formato_combo = QComboBox()
				self.formato_combo.addItems(['Vídeo (.mp4)', 'Áudio (.mp3)'])
				formato_layout.addWidget(formato_label)
				formato_layout.addWidget(self.formato_combo)
				layout.addLayout(formato_layout)

				# Quantidade de músicas
				qtd_layout = QHBoxLayout()
				qtd_label = QLabel('Quantidade:')
				self.qtd_spin = QSpinBox()
				self.qtd_spin.setRange(1, 50)
				self.qtd_spin.setValue(20)
				qtd_layout.addWidget(qtd_label)
				qtd_layout.addWidget(self.qtd_spin)
				layout.addLayout(qtd_layout)

				# Botões principais
				btn_layout = QHBoxLayout()
				self.buscar_btn = QPushButton('Buscar Artista')
				self.buscar_btn.setObjectName('buscar_btn')
				self.confirmar_btn = QPushButton('Próximo passo')
				self.confirmar_btn.setObjectName('confirmar_btn')
				self.confirmar_btn.setEnabled(False)
				self.baixar_btn = QPushButton('Baixar Músicas')
				self.baixar_btn.setObjectName('baixar_btn')
				self.baixar_btn.setEnabled(False)
				self.cancelar_btn = QPushButton('Cancelar')
				self.cancelar_btn.setObjectName('cancelar_btn')
				self.cancelar_btn.setEnabled(False)
				btn_layout.addWidget(self.buscar_btn)
				btn_layout.addWidget(self.confirmar_btn)
				btn_layout.addWidget(self.baixar_btn)
				btn_layout.addWidget(self.cancelar_btn)
				layout.addLayout(btn_layout)

				# Barra de progresso
				self.progress_bar = QProgressBar()
				self.progress_bar.setValue(0)
				layout.addWidget(self.progress_bar)

				# Área de logs
				self.log_area = QTextEdit()
				self.log_area.setReadOnly(True)
				self.log_area.setMaximumHeight(120)
				layout.addWidget(QLabel('Logs:'))
				layout.addWidget(self.log_area)

				self.setLayout(layout)

				# Conectar sinais aos slots (funções)
				self.buscar_btn.clicked.connect(self.on_buscar_artista)
				self.confirmar_btn.clicked.connect(self.on_confirmar_artista)
				self.baixar_btn.clicked.connect(self.on_baixar_musicas)
				self.cancelar_btn.clicked.connect(self.on_cancelar)
		self._cancelar = False

		# Progresso individual e geral
		progresso_individual = [0.0] * total

		def progresso_callback(idx, percent, titulo):
			progresso_individual[idx] = percent
			# Atualiza barra de progresso geral (média dos individuais)
			media = sum(progresso_individual) / total if total else 0
			self.progress_bar.setValue(int(media * 100))

		def logger(msg):
			self.log(msg)

		def download_thread():
			baixar_varias_musicas(
				musicas,
				pasta_destino,
				formato=formato,
				logger=logger,
				progresso_callback=progresso_callback
			)
			self.cancelar_btn.setEnabled(False)
			self.log('Downloads finalizados.')

		t = threading.Thread(target=download_thread)
		t.start()

	def __init__(self):
		super().__init__()
		self.setWindowTitle('Baixar Músicas Populares de Artistas')
		self.setMinimumWidth(600)
		self.init_ui()

	def abrir_dialogo_api_key(self):
		dialog = QDialog(self)
		dialog.setWindowTitle('Configurar API Key do YouTube')
		vbox = QVBoxLayout()
		label = QLabel('Informe sua chave da API do YouTube:')
		vbox.addWidget(label)
		input_api = QLineEdit()
		input_api.setPlaceholderText('YOUTUBE_API_KEY')
		vbox.addWidget(input_api)
		info = QLabel('<a href="https://console.cloud.google.com/apis/credentials">Obter chave</a>')
		info.setOpenExternalLinks(True)
		vbox.addWidget(info)
		hbox = QHBoxLayout()
		btn_salvar = QPushButton('Salvar')
		btn_cancelar = QPushButton('Cancelar')
		hbox.addWidget(btn_salvar)
		hbox.addWidget(btn_cancelar)
		vbox.addLayout(hbox)
		dialog.setLayout(vbox)
		btn_cancelar.clicked.connect(dialog.reject)

		import sys
		import os

		# ...existing code...

	def init_ui(self):
		layout = QVBoxLayout()
		# ...existing code...

		# Menu superior
		menubar = QMenuBar(self)
		menu_config = QMenu('Configurações', self)
		acao_api = QAction('API Key...', self)
		acao_api.triggered.connect(self.abrir_dialogo_api_key)
		menu_config.addAction(acao_api)
		menubar.addMenu(menu_config)
		layout.setMenuBar(menubar)
		# ...existing code...

	def init_ui(self):
		layout = QVBoxLayout()

		# Campo de busca do artista
		artista_layout = QHBoxLayout()
		artista_label = QLabel('Artista:')
		self.artista_input = QLineEdit()
		self.artista_input.setPlaceholderText('Digite o nome do artista')
		artista_layout.addWidget(artista_label)
		artista_layout.addWidget(self.artista_input)
		layout.addLayout(artista_layout)

		# Opções de formato
		formato_layout = QHBoxLayout()
		formato_label = QLabel('Formato:')
		self.formato_combo = QComboBox()
		self.formato_combo.addItems(['Vídeo (.mp4)', 'Áudio (.mp3)'])
		formato_layout.addWidget(formato_label)
		formato_layout.addWidget(self.formato_combo)
		layout.addLayout(formato_layout)

		# Quantidade de músicas
		qtd_layout = QHBoxLayout()
		qtd_label = QLabel('Quantidade:')
		self.qtd_spin = QSpinBox()
		self.qtd_spin.setRange(1, 50)
		self.qtd_spin.setValue(20)
		qtd_layout.addWidget(qtd_label)
		qtd_layout.addWidget(self.qtd_spin)
		layout.addLayout(qtd_layout)

		# Botões principais
		btn_layout = QHBoxLayout()
		self.buscar_btn = QPushButton('Buscar Artista')
		self.buscar_btn.setObjectName('buscar_btn')
		self.confirmar_btn = QPushButton('Próximo passo')
		self.confirmar_btn.setObjectName('confirmar_btn')
		self.confirmar_btn.setEnabled(False)
		self.baixar_btn = QPushButton('Baixar Músicas')
		self.baixar_btn.setObjectName('baixar_btn')
		self.baixar_btn.setEnabled(False)
		self.cancelar_btn = QPushButton('Cancelar')
		self.cancelar_btn.setObjectName('cancelar_btn')
		self.cancelar_btn.setEnabled(False)
		btn_layout.addWidget(self.buscar_btn)
		btn_layout.addWidget(self.confirmar_btn)
		btn_layout.addWidget(self.baixar_btn)
		btn_layout.addWidget(self.cancelar_btn)
		layout.addLayout(btn_layout)

		# Barra de progresso
		self.progress_bar = QProgressBar()
		self.progress_bar.setValue(0)
		layout.addWidget(self.progress_bar)

	# Área de logs
	self.log_area = QTextEdit()
	self.log_area.setReadOnly(True)
	self.log_area.setMaximumHeight(120)
	layout.addWidget(QLabel('Logs:'))
	layout.addWidget(self.log_area)

	# Menu superior
	menubar = QMenuBar(self)
	menu_config = QMenu('Configurações', self)
	acao_api = QAction('API Key...', self)
	acao_api.triggered.connect(self.abrir_dialogo_api_key)
	menu_config.addAction(acao_api)
	menubar.addMenu(menu_config)
	layout.setMenuBar(menubar)
	self.setLayout(layout)

	# Conectar sinais aos slots (funções)
	self.buscar_btn.clicked.connect(self.on_buscar_artista)
	self.confirmar_btn.clicked.connect(self.on_confirmar_artista)
	self.baixar_btn.clicked.connect(self.on_baixar_musicas)
	self.cancelar_btn.clicked.connect(self.on_cancelar)

	def main():
		app = QApplication(sys.argv)
		win = MainWindow()
		win.show()
		sys.exit(app.exec())

