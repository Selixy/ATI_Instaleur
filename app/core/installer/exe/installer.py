"""
Installateur EXE réel.
Module: core.installer.exe.installer
"""

import sys
import requests
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from ..hook.base_installer import BaseInstaller
from ..hook.status import InstallationResult, InstallationStatus, InstallationMethod
from ..hook.progress import ProgressInfo
from ..install_paths import get_install_path_manager


class ExeInstaller(BaseInstaller):
    """Installateur EXE réel."""

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
        """Installation réelle d'un package EXE - télécharge ou copie uniquement le .exe."""
        import time
        import shutil
        import sys
        start_time = time.time()

        # Récupérer les informations de l'application
        app_config = kwargs.get('app_config')
        if not app_config:
            return InstallationResult(
                status=InstallationStatus.FAILED,
                message=f"Configuration de l'application '{package_name}' manquante",
                package_name=package_name,
                method=self.method
            )

        # Trouver la méthode EXE dans la configuration
        exe_method = None
        for method in app_config.get('methods', []):
            if method.get('type') == 'exe':
                exe_method = method
                break

        if not exe_method:
            return InstallationResult(
                status=InstallationStatus.FAILED,
                message=f"Aucune méthode EXE trouvée pour '{package_name}'",
                package_name=package_name,
                method=self.method
            )

        download_url = exe_method.get('url')
        local_exe = exe_method.get('local_exe', None)

        # Vérifier qu'on a au moins une source
        if not download_url and not local_exe:
            return InstallationResult(
                status=InstallationStatus.FAILED,
                message=f"URL de téléchargement et fichier local manquants pour '{package_name}'",
                package_name=package_name,
                method=self.method
            )

        # Gérer les chemins d'installation personnalisés
        path_manager = get_install_path_manager()
        custom_install_path = None
        if app_config.get('custom_install_path', False):
            custom_install_path = path_manager.get_custom_path(package_name)

        # Démarrer l'installation
        self.progress_tracker.start_package(package_name)

        try:
            # Cas 1: Fichier local - on copie
            if local_exe:
                if self.is_cancelled:
                    return self._make_cancelled_result(package_name, start_time)

                self._update_progress(10, f"📁 Recherche de l'installateur local pour {package_name}...", package_name)

                local_installer_path = self._find_local_installer_path(local_exe)
                if not local_installer_path or not local_installer_path.exists():
                    return InstallationResult(
                        status=InstallationStatus.FAILED,
                        message=f"Installateur local non trouvé : {local_exe}",
                        package_name=package_name,
                        method=self.method
                    )

                self._update_progress(30, f"📋 Copie de l'installateur local...", package_name)

                # Déterminer le répertoire de destination
                if custom_install_path:
                    destination_dir = Path(custom_install_path)
                else:
                    destination_dir = Path.home() / "Desktop"

                destination_dir.mkdir(parents=True, exist_ok=True)
                destination_file = destination_dir / local_installer_path.name

                # Copier le fichier
                shutil.copy2(local_installer_path, destination_file)

                self._update_progress(100, f"✅ {package_name} copié avec succès vers {destination_file}", package_name)

                return InstallationResult(
                    status=InstallationStatus.SUCCESS,
                    message=f"{package_name} copié vers {destination_file}",
                    package_name=package_name,
                    method=self.method,
                    execution_time=time.time() - start_time
                )

            # Cas 2: URL - on télécharge
            else:
                if self.is_cancelled:
                    return self._make_cancelled_result(package_name, start_time)

                self._update_progress(5, f"📥 Téléchargement de {package_name}...", package_name)
                exe_file_path = self._download_exe_to_destination(download_url, package_name, custom_install_path)

                if not exe_file_path:
                    return InstallationResult(
                        status=InstallationStatus.FAILED,
                        message=f"Échec du téléchargement de '{package_name}'",
                        package_name=package_name,
                        method=self.method
                    )

                if self.is_cancelled:
                    return self._make_cancelled_result(package_name, start_time)

                self._update_progress(100, f"✅ {package_name} téléchargé avec succès vers {exe_file_path}", package_name)

                return InstallationResult(
                    status=InstallationStatus.SUCCESS,
                    message=f"{package_name} téléchargé vers {exe_file_path}",
                    package_name=package_name,
                    method=self.method,
                    execution_time=time.time() - start_time
                )

        except Exception as e:
            return InstallationResult(
                status=InstallationStatus.FAILED,
                message=f"Erreur lors du traitement de '{package_name}': {str(e)}",
                package_name=package_name,
                method=self.method,
                execution_time=time.time() - start_time
            )

    def _find_local_installer_path(self, local_exe: str) -> Optional[Path]:
        """
        Trouve le chemin vers l'installateur local.
        Gère les modes développement et build (PyInstaller).
        """
        is_frozen = getattr(sys, 'frozen', False)

        if is_frozen:
            # Mode PyInstaller - les fichiers sont dans le répertoire de l'exécutable
            exe_dir = Path(sys.executable).parent
            candidates = [
                exe_dir / "_internal" / "installers" / local_exe,  # PyInstaller onedir
                exe_dir / "installers" / local_exe,
                exe_dir / local_exe
            ]

            # Essayer aussi _MEIPASS pour les fichiers intégrés
            if hasattr(sys, '_MEIPASS'):
                meipass = Path(sys._MEIPASS)
                candidates.extend([
                    meipass / "installers" / local_exe,
                    meipass / local_exe
                ])
        else:
            # Mode développement - partir du fichier actuel vers la racine du projet
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent.parent.parent
            candidates = [
                project_root / "installers" / local_exe
            ]

        # Tester chaque candidat
        for candidate in candidates:
            if candidate.exists():
                return candidate

        return None

    def _download_exe_to_destination(self, url: str, package_name: str, custom_path: Optional[str] = None) -> Optional[Path]:
        """Télécharge l'installateur EXE sur le Bureau ou dans le répertoire spécifié."""
        try:
            # Déterminer le répertoire de destination
            if custom_path:
                destination_dir = Path(custom_path)
            else:
                # Bureau par défaut
                destination_dir = Path.home() / "Desktop"

            # Créer le répertoire si nécessaire
            destination_dir.mkdir(parents=True, exist_ok=True)

            # Déterminer le nom du fichier
            parsed_url = urlparse(url)
            filename = Path(parsed_url.path).name
            if not filename or not filename.endswith('.exe'):
                filename = f"{package_name}_installer.exe"

            exe_path = destination_dir / filename

            # Télécharger le fichier
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(exe_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self.is_cancelled:
                        return None

                    f.write(chunk)
                    downloaded += len(chunk)

                    # Mettre à jour la progression du téléchargement (5% à 100%)
                    if total_size > 0:
                        progress = 5 + int((downloaded / total_size) * 95)
                        self._update_progress(progress, f"📥 Téléchargement de {package_name}... ({downloaded // 1024}KB/{total_size // 1024}KB)", package_name)

            return exe_path

        except Exception as e:
            print(f"Erreur lors du téléchargement: {e}")
            return None

    def _update_progress(self, progress: int, message: str, package_name: str):
        """Met à jour la progression."""
        if self.progress_tracker.callback:
            progress_info = ProgressInfo(
                current_progress=progress,
                global_progress=self._calculate_global_progress(progress),
                message=message,
                package_name=package_name,
                current_step=message
            )
            self.progress_tracker.callback(progress_info)


    def _make_cancelled_result(self, package_name: str, start_time: float) -> InstallationResult:
        """Helper pour quand on annule"""
        return InstallationResult(
            status=InstallationStatus.CANCELLED,
            message=f"😔 Installation EXE de {package_name} annulée",
            package_name=package_name,
            method=self.method,
            execution_time=time.time() - start_time
        )