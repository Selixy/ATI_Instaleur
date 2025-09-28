# selection_page/selection_page.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QPushButton
)
from PySide6.QtCore import Qt, Signal
from core.YamlLoader import get_config_loader
from core.installer.status_checker import get_status_checker
from .components import CategorySection


class SelectionPage(QWidget):
    """Page principale de sélection des applications."""

    installation_requested = Signal(list)

    def __init__(self):
        super().__init__()
        self.config_loader = get_config_loader()
        self.status_checker = get_status_checker()
        self.category_sections = []
        self.installation_statuses = {}
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

        # Vérification des statuts d'installation avec optimisation
        print("Vérification des statuts d'installation...")
        all_applications = self.config_loader.get_all_applications()

        # Limiter la vérification si trop d'applications
        if len(all_applications) > 50:
            print(f"Optimisation: vérification limitée à 50 premières applications sur {len(all_applications)}")
            apps_to_check = all_applications[:50]
        else:
            apps_to_check = all_applications

        # Vérifier les statuts avec les versions par défaut
        self.installation_statuses = {}
        for app in apps_to_check:
            # Si l'app a des versions, utiliser la version par défaut
            if app.has_versions and app.versions:
                default_version = app.versions[app.default_version_index] if app.default_version_index < len(app.versions) else app.versions[0]
                is_installed = self.status_checker.check_application_status(app, default_version)
            else:
                # Sinon utiliser l'ancienne méthode
                is_installed = self.status_checker.check_application_status(app)

            self.installation_statuses[app.name] = is_installed

        # Pour les apps non vérifiées, on assume qu'elles ne sont pas installées
        for app in all_applications:
            if app.name not in self.installation_statuses:
                self.installation_statuses[app.name] = False

        # Log des statuts trouvés
        installed_count = sum(1 for status in self.installation_statuses.values() if status)
        total_count = len(self.installation_statuses)
        print(f"Statuts trouvés: {installed_count}/{total_count} applications installées")

        # Créer une section pour chaque catégorie
        for category_name, applications in apps_by_category.items():
            if applications:  # Ignorer les catégories vides
                section = CategorySection(category_name, applications, self.installation_statuses)

                # Connecter les signaux pour mettre à jour le bouton d'installation
                for card in section.app_cards:
                    card.toggled.connect(self.update_install_button)
                    # Connecter le signal de changement de version
                    if hasattr(card, 'version_changed'):
                        card.version_changed.connect(self.on_version_changed)

                # Connecter le signal de changement de sélection de la section
                section.app_selection_changed.connect(self.update_install_button)

                self.category_sections.append(section)
                self.scroll_layout.addWidget(section)

        # Ajouter un spacer à la fin
        self.scroll_layout.addStretch()

    def update_install_button(self):
        """Met à jour l'état du bouton d'installation."""
        to_install = self.get_selected_for_installation()
        to_uninstall = self.get_selected_for_uninstallation()

        total_selected = len(to_install) + len(to_uninstall)
        self.install_button.setEnabled(total_selected > 0)

        # Mettre à jour le texte du bouton selon les actions
        if total_selected == 0:
            self.install_button.setText("Installer les applications sélectionnées")
        elif len(to_install) > 0 and len(to_uninstall) == 0:
            self.install_button.setText(f"Installer {len(to_install)} application(s)")
        elif len(to_install) == 0 and len(to_uninstall) > 0:
            self.install_button.setText(f"Désinstaller {len(to_uninstall)} application(s)")
        else:
            self.install_button.setText(f"Traiter {total_selected} application(s) ({len(to_install)} inst., {len(to_uninstall)} désinst.)")

    def select_all_apps(self):
        """Sélectionne toutes les applications (sauf celles déjà installées)."""
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

    def get_selected_for_installation(self):
        """Retourne les applications sélectionnées qui ne sont PAS installées."""
        all_selected = self.get_selected_applications()
        to_install = []

        for app_info in all_selected:
            app_name = app_info['name']
            is_installed = self.installation_statuses.get(app_name, False)
            if not is_installed:
                to_install.append(app_info)

        return to_install

    def get_selected_for_uninstallation(self):
        """Retourne les applications sélectionnées qui SONT installées."""
        all_selected = self.get_selected_applications()
        to_uninstall = []

        for app_info in all_selected:
            app_name = app_info['name']
            is_installed = self.installation_statuses.get(app_name, False)
            if is_installed:
                to_uninstall.append(app_info)

        return to_uninstall

    def start_installation(self):
        """Démarre l'installation des applications sélectionnées (non installées seulement)."""
        # Séparer les applications à installer et à désinstaller
        to_install = self.get_selected_for_installation()
        to_uninstall = self.get_selected_for_uninstallation()

        # Log des listes
        if to_install:
            install_names = [app['name'] for app in to_install]
            print(f"Applications à installer: {install_names}")

        if to_uninstall:
            uninstall_names = [app['name'] for app in to_uninstall]
            print(f"Applications à désinstaller: {uninstall_names}")

        # Pour l'instant, on n'installe que les applications non installées
        if to_install:
            # Convertir en format simple pour compatibilité
            app_names = [app['name'] for app in to_install]
            self.installation_requested.emit(app_names)
        elif to_uninstall:
            # Si seulement des désinstallations, afficher un message
            print("Note: Désinstallation pas encore implémentée - seulement des apps installées sélectionnées")
        else:
            print("Aucune application à traiter")

    def refresh_installation_statuses(self):
        """Rafraîchit les statuts d'installation de toutes les applications."""
        print("Rafraîchissement des statuts d'installation...")

        # Vider le cache du status checker
        self.status_checker.clear_cache()

        # Re-vérifier tous les statuts avec versions
        all_applications = self.config_loader.get_all_applications()
        self.installation_statuses = {}
        for app in all_applications:
            # Si l'app a des versions, utiliser la version par défaut
            if app.has_versions and app.versions:
                default_version = app.versions[app.default_version_index] if app.default_version_index < len(app.versions) else app.versions[0]
                is_installed = self.status_checker.check_application_status(app, default_version)
            else:
                # Sinon utiliser l'ancienne méthode
                is_installed = self.status_checker.check_application_status(app)

            self.installation_statuses[app.name] = is_installed

        # Mettre à jour l'affichage de toutes les cartes
        for section in self.category_sections:
            for card in section.app_cards:
                app_name = card.application.name
                is_installed = self.installation_statuses.get(app_name, False)
                card.set_installed_state(is_installed)

        # Mettre à jour le bouton
        self.update_install_button()

        # Log des nouveaux statuts
        installed_count = sum(1 for status in self.installation_statuses.values() if status)
        total_count = len(self.installation_statuses)
        print(f"Statuts mis à jour: {installed_count}/{total_count} applications installées")

    def on_version_changed(self, app_name: str, version: str):
        """Gestionnaire appelé quand une version d'application change."""
        print(f"Changement de version détecté: {app_name} -> {version}")

        # Re-vérifier le statut d'installation pour cette version spécifique
        try:
            # Trouver l'application
            app_found = None
            for section in self.category_sections:
                for card in section.app_cards:
                    if card.application.name == app_name:
                        app_found = card.application
                        break
                if app_found:
                    break

            if app_found:
                # Vérifier le statut avec la nouvelle version
                selected_version = None
                for card in [c for s in self.category_sections for c in s.app_cards]:
                    if card.application.name == app_name:
                        selected_version = card.get_selected_version()
                        break

                if selected_version:
                    # Créer une clé de cache unique pour cette version
                    cache_key = f"{app_name}:{version}"

                    # Vider le cache pour cette app/version
                    if cache_key in getattr(self.status_checker, '_cache', {}):
                        del self.status_checker._cache[cache_key]

                    # Re-vérifier avec la nouvelle version
                    is_installed = self.status_checker.check_application_status(app_found, selected_version)

                    # Mettre à jour le statut dans notre cache local
                    self.installation_statuses[app_name] = is_installed

                    # Mettre à jour l'affichage de la carte
                    for section in self.category_sections:
                        for card in section.app_cards:
                            if card.application.name == app_name:
                                card.set_installed_state(is_installed)
                                break

                    print(f"Statut mis à jour pour {app_name} v{version}: {'installé' if is_installed else 'non installé'}")

        except Exception as e:
            print(f"Erreur lors de la vérification de version pour {app_name}: {e}")

        # Mettre à jour le bouton d'installation
        self.update_install_button()