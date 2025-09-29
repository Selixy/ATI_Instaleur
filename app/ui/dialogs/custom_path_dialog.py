"""
Boîte de dialogue pour configurer le chemin d'installation personnalisé.
Module: ui.dialogs.custom_path_dialog
"""

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


        # Section chemin global - recréation complète
        self._create_path_section(layout)

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

        # Connecter les changements pour mise à jour en temps réel

        # Mise à jour initiale de l'état
        self._update_controls_state()

    def _create_path_section(self, layout):
        """Crée la section de configuration du chemin personnalisé."""
        # Groupe principal
        self.global_group = QGroupBox("Chemin d'installation global")
        global_layout = QVBoxLayout(self.global_group)

        # Checkbox d'activation
        self.enable_custom_path_checkbox = QCheckBox("Utiliser un chemin d'installation personnalisé")
        global_layout.addWidget(self.enable_custom_path_checkbox)

        # Ligne de chemin
        path_container = QWidget()
        path_layout = QHBoxLayout(path_container)
        path_layout.setContentsMargins(0, 0, 0, 0)

        # Label
        path_label = QLabel("Chemin de base :")
        path_layout.addWidget(path_label)

        # Champ de texte
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Ex: C:\\Logiciels\\")
        path_layout.addWidget(self.path_edit)

        # Bouton parcourir
        self.browse_button = QPushButton("Parcourir...")
        path_layout.addWidget(self.browse_button)

        global_layout.addWidget(path_container)
        layout.addWidget(self.global_group)

        # Connecter les signaux après création
        self._connect_signals()

    def _connect_signals(self):
        """Connecte tous les signaux."""
        self.enable_custom_path_checkbox.stateChanged.connect(self._on_checkbox_changed)
        self.browse_button.clicked.connect(self._on_browse_clicked)

    def _on_checkbox_changed(self, state):
        """Gère le changement d'état de la checkbox."""
        self._update_controls_state()

    def _on_browse_clicked(self):
        """Gère le clic sur le bouton parcourir."""
        QMessageBox.information(self, "Test", "Bouton Parcourir cliqué!")
        self._browse_for_directory()

    def _update_controls_state(self):
        """Met à jour l'état des contrôles selon la checkbox."""
        enabled = self.enable_custom_path_checkbox.isChecked()
        self.path_edit.setEnabled(enabled)
        self.browse_button.setEnabled(enabled)

    def _browse_for_directory(self):
        """Ouvre le sélecteur de dossier."""
        current_path = self.path_edit.text().strip()
        if not current_path or not os.path.exists(current_path):
            current_path = os.path.expanduser("~")

        selected_path = QFileDialog.getExistingDirectory(
            self,
            "Sélectionner le dossier d'installation",
            current_path
        )

        if selected_path:
            self.path_edit.setText(selected_path)

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

        # Mettre à jour l'état après le chargement
        self._update_controls_state()

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
                        f"Impossible de créer ou d'accéder au dossier :\\n{path}\\n\\nErreur : {e}"
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
                f"{message}\\n\\nLes prochaines installations utiliseront cette configuration."
            )

            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'application des paramètres :\\n{e}"
            )