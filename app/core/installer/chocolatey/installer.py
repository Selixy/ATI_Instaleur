"""
Installateur Chocolatey avec simulation mignonne.
Module: core.installer.chocolatey.installer
"""

import time
import random
from typing import Optional

from ..hook.base_installer import BaseInstaller
from ..hook.status import InstallationResult, InstallationStatus, InstallationMethod
from ..hook.progress import ProgressInfo


class ChocolateyInstaller(BaseInstaller):
    """Installateur Chocolatey avec simulation adorable."""

    def __init__(self):
        super().__init__(InstallationMethod.CHOCOLATEY)

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
        """Vérifie si Chocolatey est disponible (simulation)."""
        # Pour la simulation, on fait semblant que Chocolatey est disponible
        return InstallationResult(
            status=InstallationStatus.SUCCESS,
            message="Chocolatey Package Manager v2.0.0 disponible !",
            method=self.method
        )

    def check_package_status(self, package_name: str) -> InstallationResult:
        """Version simplifiée - on fait semblant que le package choco existe !"""
        self.progress_tracker.emit_progress(50, f"🔍 Je cherche {package_name} dans Chocolatey...")
        time.sleep(0.2)
        self.progress_tracker.emit_progress(100, f"✅ {package_name} trouvé sur chocolatey.org !")

        return InstallationResult(
            status=InstallationStatus.SUCCESS,
            message=f"'{package_name}' disponible via Chocolatey !",
            package_name=package_name,
            method=self.method
        )

    def install_package(self, package_name: str, force_reinstall: bool = False, **kwargs) -> InstallationResult:
        """
        SIMULATION MIGNONNE D'UNE INSTALLATION CHOCOLATEY
        (choco install style!)
        """
        start_time = time.time()

        # Si on annule, on s'arrête
        if self.is_cancelled:
            return InstallationResult(
                status=InstallationStatus.CANCELLED,
                message="Installation Chocolatey annulée",
                package_name=package_name,
                method=self.method
            )

        # On dit qu'on commence
        self.progress_tracker.start_package(package_name)

        # Début de l'installation Chocolatey
        progress_info = ProgressInfo(
            current_progress=0,
            global_progress=self._calculate_global_progress(0),
            message=f"🍫 Installation de {package_name} avec Chocolatey...",
            package_name=package_name,
            current_step="Initialisation de Chocolatey..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Étape 1: Vérification des sources
        time.sleep(0.3)
        if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

        progress_info = ProgressInfo(
            current_progress=5,
            global_progress=self._calculate_global_progress(5),
            message=f"🌐 Connexion aux sources Chocolatey...",
            package_name=package_name,
            current_step="Vérification des dépôts..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Étape 2: Recherche du package
        time.sleep(0.4)
        if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

        progress_info = ProgressInfo(
            current_progress=12,
            global_progress=self._calculate_global_progress(12),
            message=f"🔍 Recherche de {package_name} sur chocolatey.org...",
            package_name=package_name,
            current_step="Analyse des dépendances..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Simulation du téléchargement Chocolatey
        total_mb = random.randint(40, 150)  # Taille variable
        downloaded_mb = 0
        last_time = time.time()

        # Message de téléchargement
        progress_info = ProgressInfo(
            current_progress=20,
            global_progress=self._calculate_global_progress(20),
            message=f"📥 Téléchargement de {package_name} via Chocolatey ({total_mb} MB)...",
            package_name=package_name,
            current_step=f"Téléchargement depuis chocolatey.org"
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Boucle de téléchargement (20% à 75%)
        while downloaded_mb < total_mb:
            if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

            # Vitesse Chocolatey (généralement bonne)
            download_speed = random.randint(6, 30)
            downloaded_mb = min(downloaded_mb + download_speed, total_mb)

            # Calculer le pourcentage (de 20% à 75%)
            download_percent = (downloaded_mb / total_mb) * 55  # 55% = 75% - 20%
            progress = int(20 + download_percent)

            # Calculer la vitesse
            current_time = time.time()
            time_elapsed = current_time - last_time
            speed_mbs = download_speed / max(time_elapsed, 0.1)

            # Message pour l'étape courante
            step_message = f"{downloaded_mb}/{total_mb} MB • {speed_mbs:.1f} MB/s (choco)"

            # Mettre à jour la progression
            progress_info = ProgressInfo(
                current_progress=progress,
                global_progress=self._calculate_global_progress(progress),
                message="",  # Pas de nouveau log
                package_name=self.progress_tracker.current_package,
                current_step=step_message
            )

            if self.progress_tracker.callback:
                self.progress_tracker.callback(progress_info)

            last_time = current_time
            time.sleep(random.uniform(0.1, 0.28))

        # Étapes post-téléchargement Chocolatey
        choco_stages = [
            (80, "🔓 Vérification des signatures..."),
            (85, "📦 Extraction du package..."),
            (90, "🔧 Exécution de chocolateyInstall.ps1..."),
            (95, "📝 Mise à jour de la base Chocolatey..."),
            (98, "🧹 Nettoyage des fichiers temporaires...")
        ]

        for progress, step_msg in choco_stages:
            if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

            time.sleep(random.uniform(0.3, 0.6))

            progress_info = ProgressInfo(
                current_progress=progress,
                global_progress=self._calculate_global_progress(progress),
                message=step_msg,
                package_name=package_name,
                current_step=step_msg.replace("🔓 ", "").replace("📦 ", "").replace("🔧 ", "")
                             .replace("📝 ", "").replace("🧹 ", "")
            )
            if self.progress_tracker.callback:
                self.progress_tracker.callback(progress_info)

        # Fin de l'installation
        time.sleep(0.3)
        if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

        progress_info = ProgressInfo(
            current_progress=100,
            global_progress=self._calculate_global_progress(100),
            message=f"🎉 {package_name} installé avec succès via Chocolatey !",
            package_name=package_name,
            current_step="Installation Chocolatey terminée !"
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Résultat final
        return InstallationResult(
            status=InstallationStatus.SUCCESS,
            message=f"Délicieux ! {package_name} installé avec Chocolatey Package Manager !",
            package_name=package_name,
            method=self.method,
            execution_time=time.time() - start_time
        )

    def _make_cancelled_result(self, package_name: str, start_time: float) -> InstallationResult:
        """Helper pour quand on annule"""
        return InstallationResult(
            status=InstallationStatus.CANCELLED,
            message=f"😔 Installation Chocolatey de {package_name} annulée",
            package_name=package_name,
            method=self.method,
            execution_time=time.time() - start_time
        )