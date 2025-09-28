"""
Installateur EXE avec simulation mignonne.
Module: core.installer.exe.installer
"""

import time
import random
from typing import Optional

from ..hook.base_installer import BaseInstaller
from ..hook.status import InstallationResult, InstallationStatus, InstallationMethod
from ..hook.progress import ProgressInfo


class ExeInstaller(BaseInstaller):
    """Installateur EXE avec simulation adorable."""

    def __init__(self):
        super().__init__(InstallationMethod.EXE)

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
        """EXE est toujours disponible !"""
        return InstallationResult(
            status=InstallationStatus.SUCCESS,
            message="Installation EXE toujours disponible !",
            method=self.method
        )

    def check_package_status(self, package_name: str) -> InstallationResult:
        """Vérifie réellement si l'application est installée sur le système."""
        try:
            from ..windows_package_detector import get_windows_detector
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
        SIMULATION ADORABLE D'UNE INSTALLATION EXE
        (comme les vrais installeurs !)
        """
        start_time = time.time()

        # Si on annule, on s'arrête
        if self.is_cancelled:
            return InstallationResult(
                status=InstallationStatus.CANCELLED,
                message="Installation EXE annulée",
                package_name=package_name,
                method=self.method
            )

        # On dit qu'on commence
        self.progress_tracker.start_package(package_name)

        # Début de l'installation EXE
        progress_info = ProgressInfo(
            current_progress=0,
            global_progress=self._calculate_global_progress(0),
            message=f"🔧 Lancement de l'installeur de {package_name}...",
            package_name=package_name,
            current_step="Démarrage de l'installeur..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Étape 1: Décompression de l'installeur
        time.sleep(0.4)
        if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

        progress_info = ProgressInfo(
            current_progress=8,
            global_progress=self._calculate_global_progress(8),
            message=f"📦 Décompression de l'installeur de {package_name}...",
            package_name=package_name,
            current_step="Extraction des fichiers temporaires..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Étape 2: Vérifications
        time.sleep(0.3)
        if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

        progress_info = ProgressInfo(
            current_progress=15,
            global_progress=self._calculate_global_progress(15),
            message=f"🔍 Vérification des prérequis pour {package_name}...",
            package_name=package_name,
            current_step="Analyse du système..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Simulation de l'installation EXE avec étapes réalistes
        stages = [
            (25, "📁 Création du dossier d'installation..."),
            (35, "📄 Copie des fichiers principaux...", "files"),
            (50, "📚 Installation des bibliothèques...", "libs"),
            (65, "🔧 Configuration de l'application...", "config"),
            (75, "📝 Mise à jour du registre...", "registry"),
            (85, "🎨 Installation des ressources...", "resources"),
            (92, "🔗 Création des raccourcis bureau...", "shortcuts"),
            (97, "🧹 Nettoyage des fichiers temporaires...", "cleanup")
        ]

        for progress, step_msg, step_type in stages:
            if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

            # Temps variable selon l'étape (certaines plus longues)
            if step_type == "files":
                time.sleep(random.uniform(0.5, 1.0))  # Copie plus longue
            elif step_type == "libs":
                time.sleep(random.uniform(0.4, 0.8))  # Bibliothèques
            else:
                time.sleep(random.uniform(0.2, 0.5))  # Autres étapes

            progress_info = ProgressInfo(
                current_progress=progress,
                global_progress=self._calculate_global_progress(progress),
                message=step_msg,
                package_name=package_name,
                current_step=step_msg.replace("📁 ", "").replace("📄 ", "").replace("📚 ", "")
                             .replace("🔧 ", "").replace("📝 ", "").replace("🎨 ", "")
                             .replace("🔗 ", "").replace("🧹 ", "")
            )
            if self.progress_tracker.callback:
                self.progress_tracker.callback(progress_info)

        # Fin de l'installation
        time.sleep(0.3)
        if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

        progress_info = ProgressInfo(
            current_progress=100,
            global_progress=self._calculate_global_progress(100),
            message=f"🎉 {package_name} installé avec succès via EXE !",
            package_name=package_name,
            current_step="Installation EXE terminée !"
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Résultat final
        return InstallationResult(
            status=InstallationStatus.SUCCESS,
            message=f"Parfait ! {package_name} installé via son installeur EXE !",
            package_name=package_name,
            method=self.method,
            execution_time=time.time() - start_time
        )

    def _make_cancelled_result(self, package_name: str, start_time: float) -> InstallationResult:
        """Helper pour quand on annule"""
        return InstallationResult(
            status=InstallationStatus.CANCELLED,
            message=f"😔 Installation EXE de {package_name} annulée",
            package_name=package_name,
            method=self.method,
            execution_time=time.time() - start_time
        )