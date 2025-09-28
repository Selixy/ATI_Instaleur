"""
Gestionnaire principal du workspace qui gère la navigation entre les pages.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Qt
from .selection_page import SelectionPage
from .installation_page import InstallationPage


class Workspace(QWidget):
    """
    Widget principal du workspace qui gère la navigation entre 
    la page de sélection et la page d'installation.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Workspace")
        self.setAttribute(Qt.WA_StyledBackground)
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Configure l'interface du workspace."""
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Widget empilé pour la navigation entre les pages
        self.stacked_widget = QStackedWidget()
        
        # Page de sélection des applications
        self.selection_page = SelectionPage()
        self.stacked_widget.addWidget(self.selection_page)
        
        # Page d'installation
        self.installation_page = InstallationPage()
        self.stacked_widget.addWidget(self.installation_page)
        
        # Démarrer sur la page de sélection
        self.stacked_widget.setCurrentWidget(self.selection_page)
        
        layout.addWidget(self.stacked_widget)
        

    
    def setup_connections(self):
        """Configure les connexions entre les signaux et slots."""
        # Connexion : sélection -> installation
        self.selection_page.installation_requested.connect(self.start_installation)
        
        # Connexion : installation -> sélection (retour)
        self.installation_page.back_to_selection.connect(self.show_selection_page)
        
        # Connexion : installation terminée
        self.installation_page.installation_finished.connect(self.on_installation_completed)
    
    def start_installation(self, selected_apps):
        """
        Démarre l'installation avec les applications sélectionnées.
        
        Args:
            selected_apps (list): Liste des noms d'applications à installer
        """
        print(f"[DEBUG] Démarrage installation de: {selected_apps}")
        
        # Passer à la page d'installation
        self.stacked_widget.setCurrentWidget(self.installation_page)
        
        # Démarrer le processus d'installation
        self.installation_page.start_installation(selected_apps)
    
    def show_selection_page(self):
        """Retourne à la page de sélection des applications."""
        print("[DEBUG] Retour à la page de sélection")

        # S'assurer que la page d'installation est dans un état propre
        self.installation_page.reset_ui_state()

        # Rafraîchir les statuts d'installation après un retour (installation possible)
        self.selection_page.refresh_installation_statuses()

        # Retourner à la page de sélection
        self.stacked_widget.setCurrentWidget(self.selection_page)
    
    def on_installation_completed(self):
        """Gestionnaire appelé quand l'installation est terminée."""
        print("[DEBUG] Installation terminée")
        
        pass
    
    def get_current_page(self):
        """Retourne la page actuellement affichée."""
        current_widget = self.stacked_widget.currentWidget()
        
        if current_widget == self.selection_page:
            return "selection"
        elif current_widget == self.installation_page:
            return "installation"
        else:
            return "unknown"
    
    def get_selected_applications(self):
        """Retourne les applications actuellement sélectionnées."""
        if self.get_current_page() == "selection":
            return self.selection_page.get_selected_applications()
        return []