# selection_page/selection_page.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QPushButton
)
from PySide6.QtCore import Qt, Signal
from core.config_loader import get_config_loader
from .components import CategorySection


class SelectionPage(QWidget):
    """Page principale de sélection des applications."""

    installation_requested = Signal(list)

    def __init__(self):
        super().__init__()
        self.config_loader = get_config_loader()
        self.category_sections = []
        self.setup_ui()
        self.load_applications()

    def setup_ui(self):
        """Configure l'interface de la page."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Description
        desc_label = QLabel("Sélection des Applications")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setProperty("class", "DescriptionLabel")
        layout.addWidget(desc_label)

        # Zone de défilement pour les applications
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setObjectName("ScrollArea")

        # Widget de contenu de la zone de défilement
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("ScrollContent")  # Ajout pour le style CSS
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(20)

        scroll_area.setWidget(self.scroll_content)
        layout.addWidget(scroll_area)

        # Boutons d'action
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Bouton "Tout sélectionner"
        self.select_all_button = QPushButton("Tout sélectionner")
        self.select_all_button.setObjectName("SelectAllButton")
        self.select_all_button.clicked.connect(self.select_all_apps)
        button_layout.addWidget(self.select_all_button)

        # Bouton "Tout désélectionner"
        self.deselect_all_button = QPushButton("Tout désélectionner")
        self.deselect_all_button.setObjectName("DeselectAllButton")
        self.deselect_all_button.clicked.connect(self.deselect_all_apps)
        button_layout.addWidget(self.deselect_all_button)

        # Bouton "Installer les applications sélectionnées"
        self.install_button = QPushButton("Installer les applications sélectionnées")
        self.install_button.setObjectName("InstallButton")
        self.install_button.clicked.connect(self.start_installation)
        self.install_button.setEnabled(False)
        button_layout.addWidget(self.install_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def load_applications(self):
        """Charge et affiche les applications par catégorie."""
        # Obtenir les applications groupées par catégorie
        apps_by_category = self.config_loader.get_applications_grouped_by_category()

        # Créer une section pour chaque catégorie
        for category_name, applications in apps_by_category.items():
            if applications:  # Ignorer les catégories vides
                section = CategorySection(category_name, applications)

                # Connecter les signaux pour mettre à jour le bouton d'installation
                for card in section.app_cards:
                    card.toggled.connect(self.update_install_button)

                # Connecter le signal de changement de sélection de la section
                section.app_selection_changed.connect(self.update_install_button)

                self.category_sections.append(section)
                self.scroll_layout.addWidget(section)

        # Ajouter un spacer à la fin
        self.scroll_layout.addStretch()

    def update_install_button(self):
        """Met à jour l'état du bouton d'installation."""
        selected_apps = self.get_selected_applications()
        self.install_button.setEnabled(len(selected_apps) > 0)

        # Mettre à jour le texte du bouton
        if len(selected_apps) == 0:
            self.install_button.setText("Installer les applications sélectionnées")
        else:
            self.install_button.setText(f"Installer {len(selected_apps)} application(s)")

    def select_all_apps(self):
        """Sélectionne toutes les applications."""
        for section in self.category_sections:
            section.select_all_checkbox.setChecked(True)

    def deselect_all_apps(self):
        """Désélectionne toutes les applications."""
        for section in self.category_sections:
            section.select_all_checkbox.setChecked(False)

    def get_selected_applications(self):
        """Retourne la liste de toutes les applications sélectionnées."""
        selected_apps = []
        for section in self.category_sections:
            selected_apps.extend(section.get_selected_apps())
        return selected_apps

    def start_installation(self):
        """Démarre l'installation des applications sélectionnées."""
        selected_apps = self.get_selected_applications()
        if selected_apps:
            self.installation_requested.emit(selected_apps)