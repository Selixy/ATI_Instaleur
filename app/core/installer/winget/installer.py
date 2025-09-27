"""
Installateur Winget avec gestion complète des erreurs.
Module: core.installer.winget.installer
"""

import subprocess
import time
from typing import Optional

from ..hook.base_installer import BaseInstaller
from ..hook.status import InstallationResult, InstallationStatus, InstallationMethod
from ..hook.progress import ProgressInfo


class WingetInstaller(BaseInstaller):
    """Installateur Winget avec gestion robuste des erreurs."""
    
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
        
        # Utiliser le cache si disponible et valide
        if not force_refresh and not self._should_refresh_cache() and self._is_available is not None:
            status = InstallationStatus.SUCCESS if self._is_available else InstallationStatus.INSTALLER_NOT_AVAILABLE
            return InstallationResult(
                status=status,
                message=f"Winget {self._version_info}" if self._is_available else "Winget non disponible",
                method=self.method
            )
        
        try:
            result = subprocess.run(
                ['winget', '--version'],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self._update_cache(True, version)
                return InstallationResult(
                    status=InstallationStatus.SUCCESS,
                    message=f"Winget {version} disponible",
                    method=self.method,
                    raw_output=result.stdout
                )
            else:
                self._update_cache(False, "")
                return InstallationResult(
                    status=InstallationStatus.INSTALLER_NOT_AVAILABLE,
                    message="Winget présent mais non fonctionnel",
                    method=self.method,
                    raw_output=result.stderr,
                    return_code=result.returncode
                )
                
        except FileNotFoundError:
            self._update_cache(False, "")
            return InstallationResult(
                status=InstallationStatus.INSTALLER_NOT_AVAILABLE,
                message="Winget non installé sur ce système",
                method=self.method
            )
        except subprocess.TimeoutExpired:
            self._update_cache(False, "")
            return InstallationResult(
                status=InstallationStatus.NETWORK_ERROR,
                message="Timeout lors de la vérification de Winget",
                method=self.method
            )
        except Exception as e:
            self._update_cache(False, "")
            return InstallationResult(
                status=InstallationStatus.FAILED,
                message=f"Erreur lors de la vérification de Winget: {str(e)}",
                method=self.method
            )
    
    def check_package_status(self, package_name: str) -> InstallationResult:
        """Version simplifiée - on fait semblant que le package existe toujours !"""
        self.progress_tracker.emit_progress(50, f"🔍 Je cherche {package_name}...")
        time.sleep(0.2)
        self.progress_tracker.emit_progress(100, f"✅ {package_name} est prêt à être téléchargé !")

        return InstallationResult(
            status=InstallationStatus.SUCCESS,
            message=f"'{package_name}' est disponible !",
            package_name=package_name,
            method=self.method
        )
    
    def install_package(self, package_name: str, force_reinstall: bool = False, **kwargs) -> InstallationResult:
        """
        SIMULATION ULTRA SIMPLE D'UN TÉLÉCHARGEMENT
        (pour un enfant de 3 ans!)
        """
        start_time = time.time()

        # Si on annule, on s'arrête
        if self.is_cancelled:
            return InstallationResult(
                status=InstallationStatus.CANCELLED,
                message="Téléchargement annulé",
                package_name=package_name,
                method=self.method
            )

        # On dit qu'on commence et on met à jour l'interface
        self.progress_tracker.start_package(package_name)

        # Créer une ProgressInfo complète pour mettre à jour le nom de l'app
        progress_info = ProgressInfo(
            current_progress=0,
            global_progress=self._calculate_global_progress(0),
            message=f"🚀 Je commence à télécharger {package_name}...",
            package_name=package_name,
            current_step="Initialisation..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Petite simulation simple
        import random

        # Étape 1: On prépare le téléchargement
        time.sleep(0.3)
        if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

        # Mise à jour avec recherche
        progress_info = ProgressInfo(
            current_progress=3,
            global_progress=self._calculate_global_progress(3),
            message=f"🔍 Je cherche {package_name}...",
            package_name=package_name,
            current_step="Recherche du logiciel..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Simulation de téléchargement avec progression réaliste
        total_mb = random.randint(50, 500)  # Taille du fichier entre 50 et 500 MB
        downloaded_mb = 0
        last_time = time.time()

        # Message initial du téléchargement (une seule fois)
        progress_info = ProgressInfo(
            current_progress=3,
            global_progress=self._calculate_global_progress(3),
            message=f"📥 Démarrage du téléchargement de {package_name} ({total_mb} MB)...",
            package_name=package_name,
            current_step=f"Téléchargement de {total_mb} MB"
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Boucle de téléchargement de 3% à 95%
        while downloaded_mb < total_mb:
            if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

            # Vitesse de téléchargement aléatoire (entre 5 et 25 MB par "tick")
            download_speed = random.randint(5, 25)
            downloaded_mb = min(downloaded_mb + download_speed, total_mb)

            # Calculer le pourcentage (de 3% à 95%)
            download_percent = (downloaded_mb / total_mb) * 92  # 92% = 95% - 3%
            progress = int(3 + download_percent)  # Commence à 3%, va jusqu'à 95%

            # Calculer la vitesse en MB/s
            current_time = time.time()
            time_elapsed = current_time - last_time
            speed_mbs = download_speed / max(time_elapsed, 0.1)  # Éviter division par 0

            # Message pour l'étape courante (sera affiché dans current_step_label)
            step_message = f"{downloaded_mb}/{total_mb} MB • {speed_mbs:.1f} MB/s"

            # Mettre à jour la progression avec l'info de téléchargement dans l'étape
            progress_info = ProgressInfo(
                current_progress=progress,
                global_progress=self._calculate_global_progress(progress),
                message="",  # Pas de nouveau log
                package_name=self.progress_tracker.current_package,
                current_step=step_message  # Les infos de téléchargement vont ici
            )

            if self.progress_tracker.callback:
                self.progress_tracker.callback(progress_info)

            last_time = current_time
            time.sleep(random.uniform(0.1, 0.3))  # Pause entre 0.1 et 0.3 secondes

        # Message final du téléchargement
        progress_info = ProgressInfo(
            current_progress=95,
            global_progress=self._calculate_global_progress(95),
            message=f"✅ Téléchargement terminé ! {total_mb} MB récupérés",
            package_name=package_name,
            current_step="Installation du logiciel..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Étape 9: Installation
        time.sleep(0.5)
        if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

        progress_info = ProgressInfo(
            current_progress=97,
            global_progress=self._calculate_global_progress(97),
            message=f"🔧 J'installe {package_name}...",
            package_name=package_name,
            current_step="Configuration du logiciel..."
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # Étape 10: Fini !
        time.sleep(0.3)
        if self.is_cancelled: return self._make_cancelled_result(package_name, start_time)

        progress_info = ProgressInfo(
            current_progress=100,
            global_progress=self._calculate_global_progress(100),
            message=f"🎉 {package_name} est installé !",
            package_name=package_name,
            current_step="Installation terminée !"
        )
        if self.progress_tracker.callback:
            self.progress_tracker.callback(progress_info)

        # On dit que c'est réussi
        return InstallationResult(
            status=InstallationStatus.SUCCESS,
            message=f"Super ! {package_name} est maintenant sur ton ordinateur !",
            package_name=package_name,
            method=self.method,
            execution_time=time.time() - start_time
        )

    def _make_cancelled_result(self, package_name: str, start_time: float) -> InstallationResult:
        """Petit helper pour quand on annule"""
        return InstallationResult(
            status=InstallationStatus.CANCELLED,
            message=f"😔 Téléchargement de {package_name} annulé",
            package_name=package_name,
            method=self.method,
            execution_time=time.time() - start_time
        )
    
