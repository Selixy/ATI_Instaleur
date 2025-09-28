"""
Installateur MSI avec détection réelle et simulation.
Module: core.installer.msi.installer
"""

import time
import random
import platform
from typing import Optional

from ..hook.base_installer import BaseInstaller
from ..hook.status import InstallationResult, InstallationStatus, InstallationMethod
from ..hook.progress import ProgressInfo
from ..windows_package_detector import get_windows_detector


class MsiInstaller(BaseInstaller):
    """Installateur MSI avec simulation adorable."""

    def __init__(self):
        super().__init__(InstallationMethod.MSI)

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
        """Vérifie si MSI est disponible (Windows seulement)."""
        if platform.system() != "Windows":
            return InstallationResult(
                status=InstallationStatus.INSTALLER_NOT_AVAILABLE,
                message="MSI n'est disponible que sur Windows",
                method=self.method
            )

        return InstallationResult(
            status=InstallationStatus.SUCCESS,
            message="MSI Installer disponible sur Windows !",
            method=self.method
        )

    def check_package_status(self, package_name: str) -> InstallationResult:
        """Vérifie réellement si le package/application est installé sur le système."""
        try:
            detector = get_windows_detector()

            # Vérifier si l'application est installée
            is_installed = detector.is_package_installed_by_name(package_name)

            if is_installed:
                return InstallationResult(
                    status=InstallationStatus.ALREADY_INSTALLED,
                    message=f"'{package_name}' est déjà installé sur le système",
                    package_name=package_name,
                    method=self.method
                )
            else:
                return InstallationResult(
                    status=InstallationStatus.NOT_FOUND,
                    message=f"'{package_name}' n'est pas installé",
                    package_name=package_name,
                    method=self.method
                )

        except Exception as e:
            return InstallationResult(
                status=InstallationStatus.FAILED,
                message=f"Erreur lors de la vérification de '{package_name}': {e}",
                package_name=package_name,
                method=self.method
            )

    def install_package(self, package_name: str, force_reinstall: bool = False, **kwargs) -> InstallationResult:
        """
        SIMULATION MIGNONNE D'UNE INSTALLATION MSI
        (avec l'interface Windows!)
        """
        start_time = time.time()

        # Si on annule, on s'arrête
        if self.is_cancelled:
            return InstallationResult(
                status=InstallationStatus.CANCELLED,
                message="Installation MSI annulée",
                package_name=package_name,
                method=self.method
            )

        # On dit qu'on commence
        self.progress_tracker.start_package(package_name)

        # Début de l'installation MSI
        progress_info = ProgressInfo(
            current_progress=0,
            global_progress=self._calculate_global_progress(0),
            message=f"📦 Lancement de l'installation MSI de {package_name}...",
            package_name=package_name,
            current_step="Préparation de l'installeur MSI..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Étape 1: Validation du fichier MSI
        time.sleep(0.5)
        if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

        progress_info = ProgressInfo(
            current_progress=10,
            global_progress=self._calculate_global_progress(10),
            message=f"🔒 Validation du fichier MSI de {package_name}...",
            package_name=package_name,
            current_step="Vérification de la signature..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Étape 2: Interface Windows
        time.sleep(0.4)
        if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

        progress_info = ProgressInfo(
            current_progress=20,
            global_progress=self._calculate_global_progress(20),
            message=f"🪟 Ouverture de l'interface Windows Installer...",
            package_name=package_name,
            current_step="Chargement de l'assistant d'installation..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Simulation de l'installation MSI avec étapes Windows
        stages = [
            (30, "📋 Lecture des informations du package..."),
            (40, "📁 Création des dossiers d'installation..."),
            (50, "📄 Copie des fichiers..."),
            (65, "📝 Écriture dans le registre Windows..."),
            (75, "🔧 Configuration des composants..."),
            (85, "⚙️ Installation des services..."),
            (92, "🔗 Création des raccourcis..."),
            (97, "✅ Finalisation de l'installation...")
        ]

        for progress, step_msg in stages:
            if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

            # Temps variable selon l'étape
            time.sleep(random.uniform(0.3, 0.7))

            progress_info = ProgressInfo(
                current_progress=progress,
                global_progress=self._calculate_global_progress(progress),
                message=step_msg,
                package_name=package_name,
                current_step=step_msg.replace("📋 ", "").replace("📁 ", "").replace("📄 ", "")
                             .replace("📝 ", "").replace("🔧 ", "").replace("⚙️ ", "")
                             .replace("🔗 ", "").replace("✅ ", "")
            )
            if self.progress_tracker.callback:
                self.progress_tracker.callback(progress_info)

        # Fin de l'installation
        time.sleep(0.3)
        if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

        progress_info = ProgressInfo(
            current_progress=100,
            global_progress=self._calculate_global_progress(100),
            message=f"🎉 {package_name} installé avec succès via MSI !",
            package_name=package_name,
            current_step="Installation MSI terminée !"
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Résultat final
        return InstallationResult(
            status=InstallationStatus.SUCCESS,
            message=f"Excellent ! {package_name} installé via Windows Installer !",
            package_name=package_name,
            method=self.method,
            execution_time=time.time() - start_time
        )

    def _make_cancelled_result(self, package_name: str, start_time: float) -> InstallationResult:
        """Helper pour quand on annule"""
        return InstallationResult(
            status=InstallationStatus.CANCELLED,
            message=f"😔 Installation MSI de {package_name} annulée",
            package_name=package_name,
            method=self.method,
            execution_time=time.time() - start_time
        )