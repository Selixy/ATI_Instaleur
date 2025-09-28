"""
Installateur Winget avec détection réelle et simulation.
Module: core.installer.winget.installer
"""

import subprocess
import platform
import time
import random
from typing import Optional

from ..hook.base_installer import BaseInstaller
from ..hook.status import InstallationResult, InstallationStatus, InstallationMethod
from ..hook.progress import ProgressInfo
from ..windows_package_detector import get_windows_detector


class WingetInstaller(BaseInstaller):
    """Installateur Winget avec détection réelle."""

    def __init__(self):
        super().__init__(InstallationMethod.WINGET)

    def _calculate_global_progress(self, current_progress: int) -> int:
        """Calcule la progression globale basée sur le nombre de packages."""
        if self.progress_tracker.total_packages > 0:
            # Progression des packages terminés
            completed_contribution = (self.progress_tracker.completed_packages / self.progress_tracker.total_packages) * 100
            # Progression du package actuel
            current_contribution = (current_progress / self.progress_tracker.total_packages)
            return int(completed_contribution + current_contribution)
        return current_progress

    def check_availability(self, force_refresh: bool = False) -> InstallationResult:
        """Vérifie si Winget est disponible sur le système."""
        if platform.system() != "Windows":
            return InstallationResult(
                status=InstallationStatus.INSTALLER_NOT_AVAILABLE,
                message="Winget n'est disponible que sur Windows",
                method=self.method
            )

        try:
            result = subprocess.run(
                ["winget", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                version = result.stdout.strip()
                return InstallationResult(
                    status=InstallationStatus.SUCCESS,
                    message=f"Winget disponible (version: {version})",
                    method=self.method
                )
            else:
                return InstallationResult(
                    status=InstallationStatus.INSTALLER_NOT_AVAILABLE,
                    message="Winget n'est pas disponible ou ne fonctionne pas correctement",
                    method=self.method
                )

        except subprocess.TimeoutExpired:
            return InstallationResult(
                status=InstallationStatus.INSTALLER_NOT_AVAILABLE,
                message="Timeout lors de la vérification de Winget",
                method=self.method
            )
        except FileNotFoundError:
            return InstallationResult(
                status=InstallationStatus.INSTALLER_NOT_AVAILABLE,
                message="Winget n'est pas installé sur ce système",
                method=self.method
            )
        except Exception as e:
            return InstallationResult(
                status=InstallationStatus.INSTALLER_NOT_AVAILABLE,
                message=f"Erreur lors de la vérification de Winget: {e}",
                method=self.method
            )

    def check_package_status(self, package_id: str) -> InstallationResult:
        """Vérifie réellement si le package Winget est installé."""
        try:
            # Vérifier d'abord que Winget est disponible
            availability = self.check_availability()
            if not availability.is_success:
                return availability

            detector = get_windows_detector()

            # Vérifier avec Winget d'abord
            is_installed_winget = detector.is_package_installed_by_winget(package_id)

            if is_installed_winget:
                return InstallationResult(
                    status=InstallationStatus.ALREADY_INSTALLED,
                    message=f"Package '{package_id}' déjà installé via Winget",
                    package_name=package_id,
                    method=self.method
                )

            # Fallback: vérifier par nom si l'ID Winget ne donne rien
            # Extraire le nom probable depuis l'ID
            app_name = self._extract_app_name_from_id(package_id)
            is_installed_name = detector.is_package_installed_by_name(app_name)

            if is_installed_name:
                return InstallationResult(
                    status=InstallationStatus.ALREADY_INSTALLED,
                    message=f"Application '{app_name}' déjà installée (détectée par nom)",
                    package_name=package_id,
                    method=self.method
                )

            # Pas installé
            return InstallationResult(
                status=InstallationStatus.NOT_FOUND,
                message=f"Package '{package_id}' n'est pas installé",
                package_name=package_id,
                method=self.method
            )

        except Exception as e:
            return InstallationResult(
                status=InstallationStatus.FAILED,
                message=f"Erreur lors de la vérification de '{package_id}': {e}",
                package_name=package_id,
                method=self.method
            )

    def _extract_app_name_from_id(self, package_id: str) -> str:
        """
        Extrait un nom d'application probable depuis un ID Winget.
        Ex: "Microsoft.VisualStudioCode" -> "Visual Studio Code"
        """
        # Supprimer le préfixe vendeur
        if "." in package_id:
            name_part = package_id.split(".", 1)[1]
        else:
            name_part = package_id

        # Séparer les mots en CamelCase
        import re
        name_with_spaces = re.sub(r'(?<!^)(?=[A-Z])', ' ', name_part)

        return name_with_spaces

    def install_package(self, package_id: str, silent: bool = True, force_reinstall: bool = False, **kwargs) -> InstallationResult:
        """
        SIMULATION D'UNE INSTALLATION WINGET
        (En attendant l'implémentation réelle)
        """
        start_time = time.time()

        # Si on annule, on s'arrête
        if self.is_cancelled:
            return InstallationResult(
                status=InstallationStatus.CANCELLED,
                message="Installation Winget annulée",
                package_name=package_id,
                method=self.method
            )

        # On dit qu'on commence
        self.progress_tracker.start_package(package_id)

        # Début de l'installation Winget
        progress_info = ProgressInfo(
            current_progress=0,
            global_progress=self._calculate_global_progress(0),
            message=f"🚀 Lancement de l'installation Winget de {package_id}...",
            package_name=package_id,
            current_step="Connexion aux serveurs Microsoft..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Étape 1: Recherche du package
        time.sleep(0.3)
        if self.is_cancelled: return self._make_cancelled_result(package_id, start_time)

        progress_info = ProgressInfo(
            current_progress=15,
            global_progress=self._calculate_global_progress(15),
            message=f"🔍 Recherche du package {package_id} dans le catalogue...",
            package_name=package_id,
            current_step="Validation du package ID..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Étape 2: Téléchargement
        time.sleep(0.4)
        if self.is_cancelled: return self._make_cancelled_result(package_id, start_time)

        for progress in range(25, 75, 10):
            if self.is_cancelled: return self._make_cancelled_result(package_id, start_time)

            speed = random.randint(50, 150)
            progress_info = ProgressInfo(
                current_progress=progress,
                global_progress=self._calculate_global_progress(progress),
                message=f"⬇️ Téléchargement de {package_id}...",
                package_name=package_id,
                current_step=f"Téléchargement en cours... {speed} MB/s"
            )
            if self.progress_tracker.callback:
                self.progress_tracker.callback(progress_info)
            time.sleep(0.2)

        # Étape 3: Installation
        time.sleep(0.3)
        if self.is_cancelled: return self._make_cancelled_result(package_id, start_time)

        progress_info = ProgressInfo(
            current_progress=85,
            global_progress=self._calculate_global_progress(85),
            message=f"⚙️ Installation de {package_id}...",
            package_name=package_id,
            current_step="Configuration des composants..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Finalisation
        time.sleep(0.3)
        if self.is_cancelled: return self._make_cancelled_result(package_id, start_time)

        progress_info = ProgressInfo(
            current_progress=100,
            global_progress=self._calculate_global_progress(100),
            message=f"✅ {package_id} installé avec succès via Winget !",
            package_name=package_id,
            current_step="Installation terminée"
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        duration = time.time() - start_time
        return InstallationResult(
            status=InstallationStatus.SUCCESS,
            message=f"Package '{package_id}' installé avec succès en {duration:.1f}s",
            package_name=package_id,
            method=self.method
        )

    def _make_cancelled_result(self, package_id: str, start_time: float) -> InstallationResult:
        """Crée un résultat d'annulation."""
        duration = time.time() - start_time
        return InstallationResult(
            status=InstallationStatus.CANCELLED,
            message=f"Installation de '{package_id}' annulée après {duration:.1f}s",
            package_name=package_id,
            method=self.method
        )