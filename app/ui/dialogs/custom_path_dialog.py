"""Boîte de dialogue pour configurer le chemin d'installation personnalisé."""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QCheckBox, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

from core.installer.install_paths import get_install_path_manager
from utils.resource_manager import get_icon_path
from core.YamlLoader import YamlLoader


class CustomInstallPathDialog(QDialog):
    """Boîte de dialogue pour configurer les chemins d'installation personnalisés."""

    # Signal émis quand la configuration change
    path_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.path_manager = get_install_path_manager()
        self.yaml_loader = YamlLoader()
        self.setup_ui()
        self.load_current_settings()

    def setup_ui(self):
        """Configure l'interface utilisateur."""
        self.setWindowTitle("Chemins d'installation")
        self.setModal(True)
        self.resize(600, 400)

        # Définir l'icône de la fenêtre
        icon_path = get_icon_path("home.png")
        if icon_path:
            self.setWindowIcon(QIcon(str(icon_path)))

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Titre
        title_label = QLabel("Configuration des chemins d'installation personnalisés")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Section chemin global
        global_group = QGroupBox("Chemin d'installation global")
        global_layout = QVBoxLayout(global_group)

        # Checkbox pour activer/désactiver
        self.enable_custom_path_checkbox = QCheckBox("Utiliser un chemin d'installation personnalisé")
        self.enable_custom_path_checkbox.toggled.connect(self.on_checkbox_toggled)
        global_layout.addWidget(self.enable_custom_path_checkbox)

        # Sélection du chemin
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Chemin de base :"))

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Ex: C:\\Logiciels\\")
        path_layout.addWidget(self.path_edit)

        self.browse_button = QPushButton("Parcourir...")
        self.browse_button.clicked.connect(self.browse_path)
        path_layout.addWidget(self.browse_button)

        global_layout.addLayout(path_layout)
        layout.addWidget(global_group)

        # Section information
        info_group = QGroupBox("Informations")
        info_layout = QVBoxLayout(info_group)

        # Obtenir dynamiquement la liste des logiciels qui ne respectent pas le chemin personnalisé
        excluded_apps = self._get_excluded_apps()
        excluded_text = ", ".join(excluded_apps) if excluded_apps else "Aucun"

        info_text = QLabel(
            f"• Si désactivé : chaque logiciel s'installe dans son dossier par défaut\n"
            f"• Si activé : tous les logiciels s'installent dans le dossier choisi\n\n"
            f"  Exceptions (utilisent toujours leur dossier par défaut) :\n"
            f"  {excluded_text}"
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)

        layout.addWidget(info_group)

        # Boutons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Annuler")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        self.apply_button = QPushButton("Appliquer")
        self.apply_button.clicked.connect(self.apply_settings)
        self.apply_button.setDefault(True)
        button_layout.addWidget(self.apply_button)

        layout.addLayout(button_layout)

    def _get_excluded_apps(self):
        """Récupère dynamiquement la liste des applications qui n'utilisent pas le chemin personnalisé."""
        excluded_apps = []
        try:
            all_apps = self.yaml_loader.get_all_applications()
            for app in all_apps:
                if not app.get('custom_install_path', True):  # False ou absent = n'utilise pas le chemin personnalisé
                    excluded_apps.append(app.get('name', 'Unknown'))
        except Exception:
            # En cas d'erreur, retourner la liste par défaut
            excluded_apps = ['Unity', 'Maya', 'MotionBuilder']

        return excluded_apps

    def load_current_settings(self):
        """Charge les paramètres actuels."""
        # Vérifier s'il y a un chemin global configuré
        if hasattr(self.path_manager, 'global_custom_path') and self.path_manager.global_custom_path:
            self.enable_custom_path_checkbox.setChecked(True)
            self.path_edit.setText(self.path_manager.global_custom_path)
        else:
            self.enable_custom_path_checkbox.setChecked(False)
            self.path_edit.setText("")

        # Mettre à jour l'état initial
        self.on_checkbox_toggled(self.enable_custom_path_checkbox.isChecked())

    def on_checkbox_toggled(self, checked):
        """Gère le changement d'état de la checkbox."""
        self.path_edit.setEnabled(checked)
        self.browse_button.setEnabled(checked)

    def browse_path(self):
        """Ouvre la boîte de dialogue pour sélectionner un dossier."""
        current_path = self.path_edit.text()
        if not current_path:
            current_path = os.path.expanduser("~")

        path = QFileDialog.getExistingDirectory(
            self,
            "Sélectionner le dossier d'installation de base",
            current_path
        )

        if path:
            self.path_edit.setText(path)

    def apply_settings(self):
        """Applique les paramètres et ferme la boîte de dialogue."""
        try:
            if self.enable_custom_path_checkbox.isChecked():
                path = self.path_edit.text().strip()
                if not path:
                    QMessageBox.warning(
                        self,
                        "Chemin requis",
                        "Veuillez sélectionner un chemin d'installation ou décocher l'option."
                    )
                    return

                # Vérifier que le chemin est valide
                if not os.path.isabs(path):
                    QMessageBox.warning(
                        self,
                        "Chemin invalide",
                        "Le chemin doit être un chemin absolu (ex: C:\\Logiciels)"
                    )
                    return

                # Essayer de créer le dossier s'il n'existe pas
                try:
                    os.makedirs(path, exist_ok=True)
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Erreur de chemin",
                        f"Impossible de créer ou d'accéder au dossier :\n{path}\n\nErreur : {e}"
                    )
                    return

                # Configurer le chemin global
                self.path_manager.set_global_custom_path(path)
                message = f"Chemin d'installation configuré : {path}"

            else:
                # Désactiver le chemin personnalisé
                self.path_manager.set_global_custom_path("")
                message = "Chemin d'installation personnalisé désactivé"

            # Émettre le signal de changement
            self.path_changed.emit()

            # Confirmation
            QMessageBox.information(
                self,
                "Configuration appliquée",
                f"{message}\n\nLes prochaines installations utiliseront cette configuration."
            )

            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'application des paramètres :\n{e}"
            )