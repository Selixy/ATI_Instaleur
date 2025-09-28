# installation_page/installation_page.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QTextEdit, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from ui.threads.installer_thread import InstallerThread
from datetime import datetime


class InstallationPage(QWidget):
    """Page d'installation utilisant InstallerThread pour une installation réelle."""

    installation_finished = Signal()
    back_to_selection = Signal()

    def __init__(self):
        super().__init__()
        self.installer_thread = None
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface avec les couleurs exactes."""
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Titre "Installation de n applications" (en gris clair)
        self.subtitle_label = QLabel("0 application(s) à installer")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setProperty("class", "TitleLabel")
        layout.addWidget(self.subtitle_label)

        # Carte "Application en cours" (ex: Python 3)
        current_app_card = QFrame()
        current_app_card.setObjectName("Card")
        current_app_layout = QVBoxLayout(current_app_card)

        self.current_app_label = QLabel("Aucune application")
        self.current_app_label.setProperty("class", "AppLabel")
        current_app_layout.addWidget(self.current_app_label)

        self.current_step_label = QLabel("Finalisation")
        self.current_step_label.setProperty("class", "StepLabel")
        current_app_layout.addWidget(self.current_step_label)

        layout.addWidget(current_app_card)

        # Carte "Progression" (barres + %)
        progress_card = QFrame()
        progress_card.setObjectName("Card")
        progress_layout = QVBoxLayout(progress_card)

        # Progression globale (texte en gris clair)
        global_layout = QHBoxLayout()
        global_label = QLabel("Progression globale:")
        global_label.setProperty("class", "ProgressLabel")
        global_layout.addWidget(global_label)

        self.global_progress_bar = QProgressBar()
        self.global_progress_bar.setRange(0, 100)
        self.global_progress_bar.setFixedHeight(4)
        global_layout.addWidget(self.global_progress_bar)

        self.global_percent_label = QLabel("0%")
        self.global_percent_label.setProperty("class", "PercentLabel")
        self.global_percent_label.setFixedWidth(30)
        global_layout.addWidget(self.global_percent_label)

        progress_layout.addLayout(global_layout)

        # Espacement
        progress_layout.addSpacing(10)

        # Progression actuelle (texte en gris clair)
        current_layout = QHBoxLayout()
        current_label = QLabel("Progression actuelle:")
        current_label.setProperty("class", "ProgressLabel")
        current_layout.addWidget(current_label)

        self.current_progress_bar = QProgressBar()
        self.current_progress_bar.setRange(0, 100)
        self.current_progress_bar.setFixedHeight(4)
        current_layout.addWidget(self.current_progress_bar)

        self.current_percent_label = QLabel("0%")
        self.current_percent_label.setProperty("class", "PercentLabel")
        self.current_percent_label.setFixedWidth(30)
        current_layout.addWidget(self.current_percent_label)

        progress_layout.addLayout(current_layout)

        layout.addWidget(progress_card)

        # Carte "Journal d'installation" - MODIFIÉE pour être responsive
        log_card = QFrame()
        log_card.setObjectName("Card")
        log_layout = QVBoxLayout(log_card)
        log_layout.setContentsMargins(12, 12, 12, 12)  # Marges constantes
        log_layout.setSpacing(8)  # Espacement constant entre titre et texte

        # Titre du journal aligné en haut
        log_title = QLabel("Journal d'installation")
        log_title.setProperty("class", "TitleLabel")
        log_title.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        log_layout.addWidget(log_title, 0)  # stretch = 0 pour ne pas s'étendre

        # TextEdit responsive qui prend l'espace restant
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        # Suppression de setFixedHeight pour permettre la responsivité
        self.log_text.setMinimumHeight(80)  # Hauteur minimale
        log_layout.addWidget(self.log_text, 1)  # stretch = 1 pour prendre l'espace disponible

        # Ajout avec stretch pour que la carte prenne l'espace disponible
        layout.addWidget(log_card, 1)  # stretch = 1 pour responsivité

        # Bouton "Terminer" (bleu)
        self.finish_button = QPushButton("Terminer")
        self.finish_button.setStyleSheet("background-color: #0078d4; color: white;")
        self.finish_button.setVisible(False)
        self.finish_button.clicked.connect(self.on_finish_clicked)

        # Bouton "Annuler"
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.setStyleSheet("background-color: #555555; color: white;")
        self.cancel_button.clicked.connect(self.cancel_installation)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.finish_button)
        button_layout.addStretch()

        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        layout.addWidget(button_widget, 0)  # stretch = 0 pour garder la taille fixe

    def start_installation(self, apps_to_install):
        """Démarre l'installation réelle avec InstallerThread."""
        self.log_text.clear()
        self.global_progress_bar.setValue(0)
        self.current_progress_bar.setValue(0)
        self.global_percent_label.setText("0%")
        self.current_percent_label.setText("0%")
        self.subtitle_label.setText(f"Installation de {len(apps_to_install)} applications")

        # Afficher le nom de la première application au lieu de "Préparation..."
        if apps_to_install:
            self.current_app_label.setText(apps_to_install[0])
            self.current_step_label.setText("Préparation du téléchargement...")
        else:
            self.current_app_label.setText("Aucune application")
            self.current_step_label.setText("Rien à installer")

        # Création et démarrage du thread d'installation
        self.installer_thread = InstallerThread(apps_to_install)

        # Connexion des signaux
        self.installer_thread.update_global_progress.connect(self.update_global_progress)
        self.installer_thread.update_current_progress.connect(self.update_current_progress)
        self.installer_thread.update_log.connect(self.update_log)
        self.installer_thread.update_current_app.connect(self.update_current_app)
        self.installer_thread.update_current_step.connect(self.update_current_step)
        self.installer_thread.finished.connect(self.on_installation_finished)
        self.installer_thread.cancelled.connect(self.on_installation_cancelled)

        # Démarrer le thread
        self.installer_thread.start()

    def update_global_progress(self, progress):
        """Met à jour la barre de progression globale."""
        self.global_progress_bar.setValue(progress)
        self.global_percent_label.setText(f"{progress}%")

    def update_current_progress(self, progress):
        """Met à jour la barre de progression de l'application courante."""
        self.current_progress_bar.setValue(progress)
        self.current_percent_label.setText(f"{progress}%")

    def update_log(self, message):
        """Ajoute un message au journal avec timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def update_current_app(self, app_name):
        """Met à jour le nom de l'application en cours d'installation."""
        self.current_app_label.setText(app_name)

    def update_current_step(self, step_info):
        """Met à jour les infos de téléchargement (MB/s, progression)."""
        self.current_step_label.setText(step_info)

    def cancel_installation(self):
        """Annule l'installation en cours."""
        if self.installer_thread and self.installer_thread.isRunning():
            # Désactiver le bouton annuler pour éviter les clics multiples
            self.cancel_button.setEnabled(False)
            self.cancel_button.setText("Annulation...")

            # Mettre à jour l'interface immédiatement
            self.current_step_label.setText("Annulation en cours...")
            self.update_log("Demande d'annulation envoyée...")

            # Arrêter le thread d'installation
            self.installer_thread.stop_installation()
        else:
            # Si aucune installation n'est en cours, retourner directement à la sélection
            self.back_to_selection.emit()

    def on_installation_finished(self):
        """Gestionnaire appelé quand l'installation est terminée."""
        self.finish_button.setVisible(True)
        self.cancel_button.setVisible(False)

    def on_installation_cancelled(self):
        """Gestionnaire appelé quand l'installation est annulée."""
        self.update_log("Installation annulée par l'utilisateur")

        # Remettre l'interface dans un état propre
        self.reset_ui_state()

        # Retourner automatiquement à la page de sélection après annulation
        self.back_to_selection.emit()

    def reset_ui_state(self):
        """Remet l'interface dans un état propre."""
        # Remettre les boutons dans leur état initial
        self.cancel_button.setEnabled(True)
        self.cancel_button.setText("Annuler")
        self.cancel_button.setVisible(True)
        self.finish_button.setVisible(False)

        # Remettre les labels dans un état neutre
        self.current_app_label.setText("Aucune application")
        self.current_step_label.setText("Prêt")
        self.subtitle_label.setText("0 application(s) à installer")

        # Remettre les barres de progression à zéro
        self.global_progress_bar.setValue(0)
        self.current_progress_bar.setValue(0)
        self.global_percent_label.setText("0%")
        self.current_percent_label.setText("0%")

    def on_finish_clicked(self):
        """Émet le signal pour revenir à la page de sélection."""
        self.reset_ui_state()
        self.back_to_selection.emit()