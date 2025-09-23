"""
Installateur Winget avec gestion complète des erreurs.
Module: core.installer.winget.installer
"""

import subprocess
import time
from typing import Optional

from ..hook.base_installer import BaseInstaller
from ..hook.status import InstallationResult, InstallationStatus, InstallationMethod
from .parser import WingetOutputParser
from .validator import WingetValidator


class WingetInstaller(BaseInstaller):
    """Installateur Winget avec gestion robuste des erreurs."""
    
    def __init__(self):
        super().__init__(InstallationMethod.WINGET)
        self.parser = WingetOutputParser()
        self.validator = WingetValidator()
    
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
        """Vérifie le statut d'un package Winget."""
        
        # Vérifier d'abord que Winget est disponible
        winget_check = self.check_availability()
        if not winget_check.is_success:
            return winget_check
        
        self.progress_tracker.emit_progress(10, f"Vérification du statut de '{package_name}'...")
        
        try:
            # Vérifier si le package est installé
            installed_version = self._get_installed_version(package_name)
            self.progress_tracker.emit_progress(40, "Vérification de l'installation actuelle...")
            
            # Vérifier la version disponible
            available_info = self._get_available_info(package_name)
            self.progress_tracker.emit_progress(80, "Vérification des versions disponibles...")
            
            if not available_info['exists']:
                return InstallationResult(
                    status=InstallationStatus.NOT_FOUND,
                    message=f"Package '{package_name}' non trouvé dans les sources Winget",
                    package_name=package_name,
                    method=self.method
                )
            
            available_version = available_info['version']
            
            # Déterminer le statut final
            if installed_version:
                if available_version and self.validator.is_newer_version(available_version, installed_version):
                    self.progress_tracker.emit_progress(100, "Vérification terminée - Mise à jour disponible")
                    return InstallationResult(
                        status=InstallationStatus.UPGRADE_AVAILABLE,
                        message=f"'{package_name}' installé (v{installed_version}), mise à jour disponible (v{available_version})",
                        package_name=package_name,
                        method=self.method,
                        installed_version=installed_version,
                        available_version=available_version
                    )
                else:
                    self.progress_tracker.emit_progress(100, "Vérification terminée - Déjà installé")
                    return InstallationResult(
                        status=InstallationStatus.ALREADY_INSTALLED,
                        message=f"'{package_name}' déjà installé (v{installed_version})",
                        package_name=package_name,
                        method=self.method,
                        installed_version=installed_version,
                        available_version=available_version or installed_version
                    )
            else:
                self.progress_tracker.emit_progress(100, "Vérification terminée - Prêt pour installation")
                return InstallationResult(
                    status=InstallationStatus.SUCCESS,
                    message=f"'{package_name}' disponible pour installation (v{available_version})",
                    package_name=package_name,
                    method=self.method,
                    available_version=available_version or "inconnue"
                )
                
        except subprocess.TimeoutExpired:
            return InstallationResult(
                status=InstallationStatus.NETWORK_ERROR,
                message=f"Timeout lors de la vérification de '{package_name}'",
                package_name=package_name,
                method=self.method
            )
        except Exception as e:
            return InstallationResult(
                status=InstallationStatus.FAILED,
                message=f"Erreur lors de la vérification de '{package_name}': {str(e)}",
                package_name=package_name,
                method=self.method
            )
    
    def install_package(self, package_name: str, force_reinstall: bool = False, **kwargs) -> InstallationResult:
        """
        Installe un package via Winget.
        
        Args:
            package_name: Nom du package à installer
            force_reinstall: Force la réinstallation même si déjà présent
            **kwargs: Arguments supplémentaires
            
        Returns:
            InstallationResult: Résultat de l'installation
        """
        start_time = time.time()
        
        if self.is_cancelled:
            return InstallationResult(
                status=InstallationStatus.CANCELLED,
                message="Installation annulée par l'utilisateur",
                package_name=package_name,
                method=self.method
            )
        
        self.progress_tracker.start_package(package_name)
        self.progress_tracker.emit_progress(0, f"Démarrage de l'installation de '{package_name}'...")
        
        # Vérifier le statut du package
        status_check = self.check_package_status(package_name)
        
        if status_check.status == InstallationStatus.ALREADY_INSTALLED and not force_reinstall:
            self.progress_tracker.emit_progress(100, f"'{package_name}' déjà installé")
            return InstallationResult(
                status=InstallationStatus.ALREADY_INSTALLED,
                message=f"'{package_name}' déjà installé (v{status_check.installed_version})",
                package_name=package_name,
                method=self.method,
                installed_version=status_check.installed_version,
                execution_time=time.time() - start_time
            )
        
        if status_check.status == InstallationStatus.NOT_FOUND:
            return status_check
        
        if not status_check.is_success and status_check.status != InstallationStatus.UPGRADE_AVAILABLE:
            return status_check
        
        self.progress_tracker.emit_progress(15, f"Préparation de l'installation...")
        
        try:
            # Construire la commande d'installation
            cmd = [
                'winget', 'install', package_name,
                '--exact',
                '--silent',
                '--accept-source-agreements',
                '--accept-package-agreements'
            ]
            
            if force_reinstall:
                cmd.append('--force')
            
            self.progress_tracker.emit_progress(20, f"Exécution: {' '.join(cmd)}")
            
            # Exécuter l'installation avec suivi en temps réel
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            output_lines = []
            while True:
                if self.is_cancelled:
                    process.terminate()
                    return InstallationResult(
                        status=InstallationStatus.CANCELLED,
                        message="Installation annulée par l'utilisateur",
                        package_name=package_name,
                        method=self.method,
                        execution_time=time.time() - start_time
                    )
                
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                
                if output:
                    line = output.strip()
                    if line:  # Ignorer les lignes vides
                        output_lines.append(line)
                        
                        # Analyser la progression et émettre les messages importants
                        progress = self.parser.estimate_progress(line, len(output_lines))
                        
                        if self.parser.is_important_line(line):
                            self.progress_tracker.emit_progress(progress, line)
                        else:
                            self.progress_tracker.emit_progress(progress)
            
            return_code = process.poll()
            full_output = '\n'.join(output_lines)
            execution_time = time.time() - start_time
            
            # Analyser le résultat final
            result = self.parser.analyze_installation_result(
                return_code, full_output, package_name, status_check.installed_version
            )
            result.method = self.method
            result.execution_time = execution_time
            
            # Message de fin selon le résultat
            if result.is_success:
                if result.status == InstallationStatus.ALREADY_INSTALLED:
                    self.progress_tracker.emit_progress(100, f"'{package_name}' était déjà installé")
                else:
                    self.progress_tracker.emit_progress(100, f"Installation de '{package_name}' réussie")
            else:
                self.progress_tracker.emit_progress(100, f"Échec de l'installation de '{package_name}': {result.message}")
            
            return result
            
        except subprocess.TimeoutExpired:
            return InstallationResult(
                status=InstallationStatus.NETWORK_ERROR,
                message=f"Timeout lors de l'installation de '{package_name}'",
                package_name=package_name,
                method=self.method,
                execution_time=time.time() - start_time
            )
        except PermissionError:
            return InstallationResult(
                status=InstallationStatus.PERMISSION_DENIED,
                message=f"Permissions insuffisantes pour installer '{package_name}'",
                package_name=package_name,
                method=self.method,
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return InstallationResult(
                status=InstallationStatus.FAILED,
                message=f"Erreur lors de l'installation de '{package_name}': {str(e)}",
                package_name=package_name,
                method=self.method,
                execution_time=time.time() - start_time
            )
    
    def _get_installed_version(self, package_name: str) -> Optional[str]:
        """Récupère la version installée d'un package."""
        try:
            result = subprocess.run(
                ['winget', 'list', package_name, '--exact'],
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0:
                return self.parser.extract_installed_version(result.stdout, package_name)
            
        except (subprocess.TimeoutExpired, Exception):
            pass
        
        return None
    
    def _get_available_info(self, package_name: str) -> dict:
        """Récupère les informations sur la version disponible."""
        try:
            result = subprocess.run(
                ['winget', 'show', package_name, '--exact'],
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0:
                version = self.parser.extract_available_version(result.stdout)
                return {
                    'exists': True,
                    'version': version
                }
            
        except (subprocess.TimeoutExpired, Exception):
            pass
        
        return {
            'exists': False,
            'version': None
        }