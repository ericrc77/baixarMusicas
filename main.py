
"""
Ponto de entrada do app Baixar Músicas.
Inicializa a interface e captura exceções, mostrando log e QMessageBox.
"""

import sys
from baixar_musicas.logger import get_logger

logger = get_logger('main')

if __name__ == "__main__":
    try:
        from baixar_musicas.gui import main
        main()
    except Exception as e:
        logger.error(f"Erro ao iniciar o app: {e}", exc_info=True)
        try:
            from PyQt5.QtWidgets import QMessageBox, QApplication
            app = QApplication.instance() or QApplication(sys.argv)
            QMessageBox.critical(None, 'Erro crítico', f'Erro ao iniciar o app:\n{e}')
        except Exception:
            print("Erro ao iniciar o app:", e)
        input("Pressione Enter para sair...")
