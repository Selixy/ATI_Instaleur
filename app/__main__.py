# app/__main__.py
from PySide6.QtWidgets import QApplication
from hook import setup_environment
import sys


def main():
    app = QApplication(sys.argv)
    setup_environment()

    # Charger les styles
    from ui import update_styles
    success = update_styles(app)
    if not success:
        print("Erorr QSS aply")

    # Créer la fenêtre principale
    from ui.main_window import create_main_window
    window = create_main_window()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()