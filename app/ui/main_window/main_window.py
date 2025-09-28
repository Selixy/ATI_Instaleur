from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from qframelesswindow import FramelessMainWindow
from .title_bar import CustomTitleBar
from utils.resource_manager import get_icon_path
from .workspace import Workspace

class MainWindow(FramelessMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATI_Instaleur")
        self._set_window_icon()
        self._setup_window_properties()  # Configuration de la fenêtre
        self._setup_central_widget()  # combine barre de titre + workspace

    def _set_window_icon(self):
        icon_path = get_icon_path("app.ico")
        if icon_path:
            self.setWindowIcon(QIcon(str(icon_path)))

    def _setup_window_properties(self):
        """Configure les propriétés de la fenêtre (taille, position, etc.)"""
        
        # Option 1: Taille fixe
        self.resize(800, 800)
        self._center_window()

    def _center_window(self):
        """Centre la fenêtre sur l'écran principal"""
        if QApplication.instance():
            screen = QApplication.primaryScreen()
            screen_geometry = screen.geometry()
            
            # Calculer la position pour centrer
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            
            self.move(x, y)

    def _setup_central_widget(self):
        """Crée un widget central avec la barre de titre et le workspace."""
        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Barre de titre personnalisée
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        # Workspace principal
        self.workspace = Workspace(self)
        main_layout.addWidget(self.workspace)

        self.setCentralWidget(central_widget)

def create_main_window() -> MainWindow:
    return MainWindow()