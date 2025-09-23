"""
Thread Qt pour l'installation des applications.
Utilise la nouvelle architecture modulaire core.installer avec config_loader.
Module: ui.threads.installer_thread
"""

from PySide6.QtCore import QThread, Signal
from typing import List
import time

from core.installer import create_main_installer, InstallationStatus, InstallationMethod
from core.installer.hook import ProgressInfo
from core.config_loader import get_config_loader


class InstallerThread(QThread):
    """
    Thread Qt qui utilise la nouvelle architecture core.installer.
    Maintient la compatibilité avec l'interface existante.
    """
    
    # Signaux Qt pour l'interface - SIGNATURES IDENTIQUES À L'ORIGINAL
    update_global_progress = Signal(int)    # Progression globale (0-100)
    update_current_progress = Signal(int)   # Progression du package en cours (0-100)
    update_log = Signal(str)               # Message de log
    update_current_app = Signal(str)       # Nom de l'app en cours
    finished = Signal()                    # Installation terminée
    cancelled = Signal()                   # Installation annulée
    
    def __init__(self, apps_to_install: List[str]):
        """
        Initialise le thread avec la liste des applications.
        
        Args:
            apps_to_install: Liste des noms d'applications à installer
        """
        super().__init__()
        self.apps_to_install = apps_to_install.copy()
        self.is_cancelled = False
        
        # Chargeur de configuration
        self.config_loader = get_config_loader()
        
        # Utiliser la nouvelle architecture
        self.installer = create_main_installer()
        self.installer.set_progress_callback(self._on_progress_update)
        
        # Statistiques pour compatibilité
        self.current_app_index = 0
        self.successful_installs = 0
        self.failed_installs = 0
        self.already_installed_count = 0
    
    def stop_installation(self):
        """Méthode publique pour arrêter l'installation - SIGNATURE IDENTIQUE."""
        self.update_log.emit("Annulation en cours...")
        self.is_cancelled = True
        self.installer.cancel_installation()
    
    def run(self):
        """Méthode principale du thread Qt."""
        try:
            total_apps = len(self.apps_to_install)
            
            self.update_log.emit(f"Démarrage de l'installation de {total_apps} application(s)")
            
            # Vérifier la compatibilité du système
            compatibility = self.installer.check_system_compatibility()
            available_methods = [method for method, result in compatibility.items() if result.is_success]
            
            if not available_methods:
                self.update_log.emit("Aucune méthode d'installation disponible sur ce système")
                self.finished.emit()
                return
            
            # Afficher les méthodes disponibles
            method_names = [method.value for method in available_methods]
            self.update_log.emit(f"Méthodes disponibles: {', '.join(method_names)}")
            
            # Convertir les noms d'applications en packages à installer
            packages_to_install = self._resolve_packages_from_config()
            
            if not packages_to_install:
                self.update_log.emit("Aucun package valide trouvé dans la configuration")
                self.finished.emit()
                return
            
            # Lancer les installations avec les vrais packages ID
            results = self.installer.install_packages(
                packages_to_install,
                preferred_method=InstallationMethod.WINGET
            )
            
            # Traiter les résultats finaux
            self._process_final_results(results)
            
            if self.is_cancelled:
                self.cancelled.emit()
            else:
                self.finished.emit()
                
        except Exception as e:
            self.update_log.emit(f"Erreur critique dans le thread: {str(e)}")
            self.finished.emit()
    
    def _resolve_packages_from_config(self) -> List[str]:
        """
        Convertit les noms d'applications en packages ID à installer selon la configuration.
        
        Returns:
            List[str]: Liste des packages ID à installer
        """
        packages_to_install = []
        
        for app_name in self.apps_to_install:
            app = self.config_loader.get_application_by_name(app_name)
            
            if not app:
                self.update_log.emit(f"⚠️ Application '{app_name}' non trouvée dans la configuration")
                continue
            
            # Chercher une méthode Winget en priorité
            winget_methods = app.get_methods_by_type("winget")
            if winget_methods:
                # Prendre la méthode Winget avec la meilleure priorité
                best_method = min(winget_methods, key=lambda x: x.priority)
                if best_method.package:
                    packages_to_install.append(best_method.package)
                    self.update_log.emit(f"📦 {app_name} → {best_method.package}")
                else:
                    self.update_log.emit(f"⚠️ {app_name} - Méthode Winget sans package défini")
            else:
                # Pas de méthode Winget disponible
                self.update_log.emit(f"⚠️ {app_name} - Aucune méthode Winget disponible")
                
                # Optionnel: essayer d'autres méthodes
                preferred_method = app.get_preferred_method()
                if preferred_method:
                    if preferred_method.type == "direct_download":
                        self.update_log.emit(f"🌐 {app_name} - Installation manuelle requise: {preferred_method.url}")
                    else:
                        self.update_log.emit(f"⚠️ {app_name} - Méthode {preferred_method.type} non supportée actuellement")
        
        return packages_to_install
    
    def _on_progress_update(self, progress_info: ProgressInfo):
        """
        Callback appelé par l'installateur pour les mises à jour de progression.
        Traduit les ProgressInfo vers les signaux Qt attendus par l'UI.
        """
        if self.is_cancelled:
            return
        
        # Mettre à jour l'index de l'app courante si un nouveau package commence
        if progress_info.package_name:
            # Essayer de retrouver le nom d'application depuis le package ID
            app_display_name = self._get_app_name_from_package(progress_info.package_name)
            
            if app_display_name and app_display_name in self.apps_to_install:
                new_index = self.apps_to_install.index(app_display_name)
                if new_index != self.current_app_index:
                    self.current_app_index = new_index
                    self.update_current_app.emit(app_display_name)
            else:
                # Fallback: afficher le nom du package
                self.update_current_app.emit(progress_info.package_name)
        
        # Émettre la progression actuelle
        if progress_info.current_progress > 0:
            self.update_current_progress.emit(progress_info.current_progress)
        
        # Émettre la progression globale
        if progress_info.global_progress > 0:
            self.update_global_progress.emit(progress_info.global_progress)
        
        # Émettre le message de log s'il n'est pas vide
        if progress_info.message.strip():
            self.update_log.emit(progress_info.message)
    
    def _get_app_name_from_package(self, package_id: str) -> str:
        """
        Retrouve le nom d'application depuis un package ID.
        
        Args:
            package_id: ID du package (ex: "BlenderFoundation.Blender")
            
        Returns:
            str: Nom de l'application ou le package ID si non trouvé
        """
        for app in self.config_loader.get_all_applications():
            winget_methods = app.get_methods_by_type("winget")
            for method in winget_methods:
                if method.package == package_id:
                    return app.name
        
        return package_id  # Fallback
    
    def _process_final_results(self, results: dict):
        """Traite les résultats finaux et met à jour les statistiques."""
        self.successful_installs = 0
        self.failed_installs = 0
        self.already_installed_count = 0
        
        for package_id, result in results.items():
            # Retrouver le nom d'application pour l'affichage
            app_name = self._get_app_name_from_package(package_id)
            
            if result.status == InstallationStatus.SUCCESS:
                self.successful_installs += 1
                self.update_log.emit(f"✅ {app_name} installé avec succès")
            elif result.status == InstallationStatus.ALREADY_INSTALLED:
                self.already_installed_count += 1
                self.update_log.emit(f"ℹ️ {app_name} déjà installé")
            else:
                self.failed_installs += 1
                if result.status == InstallationStatus.NOT_FOUND:
                    self.update_log.emit(f"❌ {app_name} non trouvé ({package_id})")
                elif result.status == InstallationStatus.PERMISSION_DENIED:
                    self.update_log.emit(f"❌ {app_name} - Permissions insuffisantes")
                elif result.status == InstallationStatus.NETWORK_ERROR:
                    self.update_log.emit(f"❌ {app_name} - Erreur réseau")
                else:
                    self.update_log.emit(f"❌ {app_name} - {result.message}")
        
        # Message de résumé final
        total = len(results)
        summary_parts = []
        
        if self.successful_installs > 0:
            summary_parts.append(f"{self.successful_installs} installés")
        if self.already_installed_count > 0:
            summary_parts.append(f"{self.already_installed_count} déjà présents")
        if self.failed_installs > 0:
            summary_parts.append(f"{self.failed_installs} échoués")
        
        if summary_parts:
            summary = f"Installation terminée: {', '.join(summary_parts)} (sur {total})"
        else:
            summary = "Installation terminée"
        
        self.update_log.emit(summary)
        
        # S'assurer que les barres de progression sont à 100%
        self.update_global_progress.emit(100)
        self.update_current_progress.emit(100)
    
    # Méthodes de compatibilité pour l'interface existante
    
    def get_total_apps_count(self) -> int:
        """Retourne le nombre total d'applications."""
        return len(self.apps_to_install)
    
    def get_current_app_index(self) -> int:
        """Retourne l'index de l'application courante."""
        return self.current_app_index
    
    def get_current_app_name(self) -> str:
        """Retourne le nom de l'application courante."""
        if 0 <= self.current_app_index < len(self.apps_to_install):
            return self.apps_to_install[self.current_app_index]
        return ""
    
    def get_installation_summary(self) -> dict:
        """
        Retourne un résumé de l'installation.
        
        Returns:
            dict: Informations sur l'installation
        """
        return {
            "total_apps": self.get_total_apps_count(),
            "current_index": self.get_current_app_index(),
            "current_app": self.get_current_app_name(),
            "apps_list": self.apps_to_install.copy(),
            "is_cancelled": self.is_cancelled,
            "successful_installs": self.successful_installs,
            "failed_installs": self.failed_installs,
            "already_installed": self.already_installed_count
        }
    
    def set_simulation_speed(self, speed_factor: float):
        """Méthode de compatibilité - sans effet en installation réelle."""
        pass
    
    def is_running_installation(self) -> bool:
        """Vérifie si une installation est en cours."""
        return self.isRunning() and not self.is_cancelled