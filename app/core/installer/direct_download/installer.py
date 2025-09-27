"""
Installateur Direct Download avec simulation mignonne.
Module: core.installer.direct_download.installer
"""

import time
import random
from typing import Optional

from ..hook.base_installer import BaseInstaller
from ..hook.status import InstallationResult, InstallationStatus, InstallationMethod
from ..hook.progress import ProgressInfo


class DirectDownloadInstaller(BaseInstaller):
    """Installateur Direct Download avec simulation adorable."""

    def __init__(self):
        super().__init__(InstallationMethod.DIRECT_DOWNLOAD)

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
        """Direct Download est toujours disponible !"""
        return InstallationResult(
            status=InstallationStatus.SUCCESS,
            message="Téléchargement direct toujours disponible !",
            method=self.method
        )

    def check_package_status(self, package_name: str) -> InstallationResult:
        """Version simplifiée - on fait semblant que le package existe toujours !"""
        self.progress_tracker.emit_progress(50, f"🔍 Je cherche {package_name} en ligne...")
        time.sleep(0.2)
        self.progress_tracker.emit_progress(100, f"✅ {package_name} trouvé sur le site officiel !")

        return InstallationResult(
            status=InstallationStatus.SUCCESS,
            message=f"'{package_name}' disponible en téléchargement direct !",
            package_name=package_name,
            method=self.method
        )

    def install_package(self, package_name: str, force_reinstall: bool = False, **kwargs) -> InstallationResult:
        """
        SIMULATION ULTRA MIGNONNE D'UN TÉLÉCHARGEMENT DIRECT
        (avec des messages adorables!)
        """
        start_time = time.time()

        # Si on annule, on s'arrête
        if self.is_cancelled:
            return InstallationResult(
                status=InstallationStatus.CANCELLED,
                message="Téléchargement direct annulé",
                package_name=package_name,
                method=self.method
            )

        # On dit qu'on commence et on met à jour l'interface
        self.progress_tracker.start_package(package_name)

        # Créer une ProgressInfo complète pour mettre à jour le nom de l'app
        progress_info = ProgressInfo(
            current_progress=0,
            global_progress=self._calculate_global_progress(0),
            message=f"🌐 Je vais télécharger {package_name} directement !",
            package_name=package_name,
            current_step="Connexion au site officiel..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Petite simulation simple
        import random

        # Étape 1: Connexion au site
        time.sleep(0.4)
        if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

        progress_info = ProgressInfo(
            current_progress=5,
            global_progress=self._calculate_global_progress(5),
            message=f"🌍 Connexion au site de {package_name}...",
            package_name=package_name,
            current_step="Recherche du fichier..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Simulation de téléchargement direct avec progression réaliste
        total_mb = random.randint(30, 200)  # Taille plus petite pour direct download
        downloaded_mb = 0
        last_time = time.time()

        # Message initial du téléchargement
        progress_info = ProgressInfo(
            current_progress=5,
            global_progress=self._calculate_global_progress(5),
            message=f"📥 Téléchargement direct de {package_name} ({total_mb} MB)...",
            package_name=package_name,
            current_step=f"Téléchargement direct de {total_mb} MB"
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Boucle de téléchargement de 5% à 90%
        while downloaded_mb < total_mb:
            if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

            # Vitesse de téléchargement direct (généralement plus rapide)
            download_speed = random.randint(8, 35)
            downloaded_mb = min(downloaded_mb + download_speed, total_mb)

            # Calculer le pourcentage (de 5% à 90%)
            download_percent = (downloaded_mb / total_mb) * 85  # 85% = 90% - 5%
            progress = int(5 + download_percent)

            # Calculer la vitesse en MB/s
            current_time = time.time()
            time_elapsed = current_time - last_time
            speed_mbs = download_speed / max(time_elapsed, 0.1)

            # Message pour l'étape courante
            step_message = f"{downloaded_mb}/{total_mb} MB • {speed_mbs:.1f} MB/s (direct)"

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
            time.sleep(random.uniform(0.08, 0.25))  # Plus rapide que winget

        # Message final du téléchargement
        progress_info = ProgressInfo(
            current_progress=90,
            global_progress=self._calculate_global_progress(90),
            message=f"✅ Téléchargement direct terminé ! {total_mb} MB récupérés",
            package_name=package_name,
            current_step="Extraction du fichier..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Étape extraction
        time.sleep(0.4)
        if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

        progress_info = ProgressInfo(
            current_progress=95,
            global_progress=self._calculate_global_progress(95),
            message=f"📂 Extraction de {package_name}...",
            package_name=package_name,
            current_step="Installation en cours..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Étape finale
        time.sleep(0.3)
        if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

        progress_info = ProgressInfo(
            current_progress=100,
            global_progress=self._calculate_global_progress(100),
            message=f"🎉 {package_name} installé via téléchargement direct !",
            package_name=package_name,
            current_step="Installation terminée !"
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # On dit que c'est réussi
        return InstallationResult(
            status=InstallationStatus.SUCCESS,
            message=f"Super ! {package_name} téléchargé et installé directement !",
            package_name=package_name,
            method=self.method,
            execution_time=time.time() - start_time
        )

    def _make_cancelled_result(self, package_name: str, start_time: float) -> InstallationResult:
        """Helper pour quand on annule"""
        return InstallationResult(
            status=InstallationStatus.CANCELLED,
            message=f"😔 Téléchargement direct de {package_name} annulé",
            package_name=package_name,
            method=self.method,
            execution_time=time.time() - start_time
        )