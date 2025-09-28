# selection_page/components/category_section.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, 
    QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from .application_card import ApplicationCard


class CategorySection(QWidget):
    """Section pour une catégorie d'applications."""

    app_selection_changed = Signal()  # Signal émis quand une application de cette section est cochée/décochée

    def __init__(self, category_name, applications):
        super().__init__()
        self.category_name = category_name
        self.applications = applications
        self.app_cards = []
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface de la section."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)
        layout.setSpacing(10)

        # En-tête de catégorie
        header_layout = QHBoxLayout()

        # Checkbox "Tout sélectionner"
        self.select_all_checkbox = QCheckBox()
        self.select_all_checkbox.stateChanged.connect(self.on_select_all)
        header_layout.addWidget(self.select_all_checkbox)

        # Nom de la catégorie
        category_label = QLabel(self.category_name)
        category_font = QFont()
        category_font.setBold(True)
        category_font.setPointSize(14)
        category_label.setFont(category_font)
        category_label.setStyleSheet("color: #0078d4;")
        header_layout.addWidget(category_label)

        # Compteur d'applications
        count_label = QLabel(f"({len(self.applications)} applications)")
        count_label.setStyleSheet("color: #aaa; font-size: 12px;")
        header_layout.addWidget(count_label)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Grille d'applications
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(10)

        # Ajouter les cartes d'applications
        columns = 2  # Nombre de colonnes
        for i, app in enumerate(self.applications):
            card = ApplicationCard(app)
            card.toggled.connect(self.on_app_toggled)
            self.app_cards.append(card)

            row = i // columns
            col = i % columns
            grid_layout.addWidget(card, row, col)

        layout.addWidget(grid_widget)

        # Ligne de séparation
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #444;")
        layout.addWidget(separator)

    def on_select_all(self, state):
        """Gestionnaire pour sélectionner/désélectionner toutes les applications."""
        if state == 1:  # PartiallyChecked -> on sélectionne tout
            is_checked = True
        else:
            is_checked = state == 2  # 2 = Checked, 0 = Unchecked

        # Sélectionner/désélectionner toutes les applications de cette catégorie
        for card in self.app_cards:
            card.set_selected(is_checked)

    def on_app_toggled(self, app_name, is_selected):
        """Gestionnaire quand une application est sélectionnée/désélectionnée."""
        # Mettre à jour l'état de la checkbox "Tout sélectionner"
        selected_count = sum(1 for card in self.app_cards if card.is_selected())
        total_count = len(self.app_cards)

        # Temporairement déconnecter le signal pour éviter la récursion
        self.select_all_checkbox.blockSignals(True)

        if selected_count == 0:
            self.select_all_checkbox.setCheckState(Qt.Unchecked)
        elif selected_count == total_count:
            self.select_all_checkbox.setCheckState(Qt.Checked)
        else:
            self.select_all_checkbox.setCheckState(Qt.PartiallyChecked)

        # Reconnecter le signal
        self.select_all_checkbox.blockSignals(False)

        # Émettre le signal pour notifier la page parent
        self.app_selection_changed.emit()

    def get_selected_apps(self):
        """Retourne la liste des applications sélectionnées avec leurs informations de version."""
        selected_apps = []
        for card in self.app_cards:
            if card.is_selected():
                app_info = {
                    'name': card.application.name,
                    'application': card.application,
                    'selected_version': card.get_selected_version(),
                    'methods': card.get_methods_for_installation()
                }
                selected_apps.append(app_info)
        return selected_apps