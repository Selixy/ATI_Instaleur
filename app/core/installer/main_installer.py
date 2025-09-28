"""
Orchestrateur principal pour les installations.
Module: core.installer.main_installer
"""

from typing import List, Dict, Any, Optional, Callable
import time

from .hook.status import InstallationResult, InstallationStatus, InstallationMethod
from .hook.progress import ProgressTracker, ProgressInfo
from . import simulation

# Imports sécurisés des installateurs
try:
    from .winget import WingetInstaller
except ImportError:
    WingetInstaller = None

try:
    from .direct_download import DirectDownloadInstaller
except ImportError:
    DirectDownloadInstaller = None

try:
    from .msi import MsiInstaller
except ImportError:
    MsiInstaller = None

try:
    from .exe import ExeInstaller
except ImportError:
    ExeInstaller = None

try:
    from .chocolatey import ChocolateyInstaller
except ImportError:
    ChocolateyInstaller = None


class MainInstaller:
    """Orchestrateur principal pour les installations de packages."""
    
    def __init__(self, simulation_mode: bool = False):
        self.progress_tracker = ProgressTracker()
        self.installers = {}
        self.simulation_mode = simulation_mode

        # Initialiser les installateurs de manière sécurisée
        installer_classes = {
            InstallationMethod.WINGET: WingetInstaller,
            InstallationMethod.DIRECT_DOWNLOAD: DirectDownloadInstaller,
            InstallationMethod.MSI: MsiInstaller,
            InstallationMethod.EXE: ExeInstaller,
            InstallationMethod.CHOCOLATEY: ChocolateyInstaller
        }

        for method, installer_class in installer_classes.items():
            # Vérifier que la classe existe (pas None à cause des imports ratés)
            if installer_class is None:
                print(f"Classe {method.value} non disponible (import raté)")
                continue

            try:
                installer = installer_class()
                installer.progress_tracker = self.progress_tracker
                self.installers[method] = installer
                print(f"OK Installateur {method.value} initialisé avec succès")
            except Exception as e:
                # Si un installateur ne peut pas être créé, on continue sans lui
                print(f"ERROR Impossible de créer l'installateur {method.value}: {e}")
                continue
        self.is_cancelled = False
        self.installation_stats = {
            'successful': 0,
            'failed': 0,
            'already_installed': 0,
            'not_found': 0,
            'cancelled': 0
        }

        # Vérifier qu'on a au moins un installateur
        if not self.installers and not self.simulation_mode:
            print("WARNING: Aucun installateur disponible !")
        else:
            if self.simulation_mode:
                simulation.enable_simulation_mode()
                print("INFO Mode simulation activé - toutes les méthodes disponibles")
            else:
                available_methods = list(self.installers.keys())
                print(f"INFO Installateurs disponibles: {[m.value for m in available_methods]}")
    
    def set_progress_callback(self, callback: Callable[[ProgressInfo], None]) -> None:
        """Définit le callback de progression pour tous les installateurs."""
        self.progress_tracker.set_callback(callback)
        
        # Propager le callback à tous les installateurs
        for installer in self.installers.values():
            installer.set_progress_callback(callback)
    
    def cancel_installation(self) -> None:
        """Annule toutes les installations en cours."""
        self.is_cancelled = True
        self.progress_tracker.cancel()

        # Propager l'annulation à tous les installateurs
        for installer in self.installers.values():
            installer.cancel_installation()

    def enable_simulation_mode(self) -> None:
        """Active le mode simulation."""
        self.simulation_mode = True
        simulation.enable_simulation_mode()

    def disable_simulation_mode(self) -> None:
        """Désactive le mode simulation."""
        self.simulation_mode = False
        simulation.disable_simulation_mode()

    def is_simulation_enabled(self) -> bool:
        """Vérifie si le mode simulation est activé."""
        return self.simulation_mode
    
    def install_packages(self, packages: List[str], 
                        preferred_method: InstallationMethod = InstallationMethod.WINGET,
                        **kwargs) -> Dict[str, InstallationResult]:
        """
        Installe plusieurs packages.
        
        Args:
            packages: Liste des noms de packages à installer
            preferred_method: Méthode d'installation préférée
            **kwargs: Arguments supplémentaires
            
        Returns:
            Dict[str, InstallationResult]: Résultats par package
        """
        if not packages:
            return {}
        
        self._reset_stats()
        self.progress_tracker.reset(len(packages))
        
        self.progress_tracker.emit_progress(
            0, 
            f"Démarrage de l'installation de {len(packages)} package(s)",
            "Initialisation"
        )
        
        results = {}
        
        for i, package in enumerate(packages):
            if self.is_cancelled:
                # Marquer les packages restants comme annulés
                for remaining_package in packages[i:]:
                    results[remaining_package] = InstallationResult(
                        status=InstallationStatus.CANCELLED,
                        message="Installation annulée par l'utilisateur",
                        package_name=remaining_package,
                        method=preferred_method
                    )
                    self.installation_stats['cancelled'] += 1
                break
            
            self.progress_tracker.start_package(package)
            
            # Installer le package
            result = self.install_single_package(
                package, 
                preferred_method=preferred_method,
                **kwargs
            )
            
            results[package] = result
            self._update_stats(result.status)
            self.progress_tracker.complete_package()
            
            # Petite pause entre les packages (sauf le dernier)
            if not self.is_cancelled and i < len(packages) - 1:
                time.sleep(0.5)
        
        # Message de fin
        self._emit_final_summary()
        
        return results
    
    def install_single_package(self, package_name: str,
                              preferred_method: InstallationMethod = InstallationMethod.WINGET,
                              fallback_methods: Optional[List[InstallationMethod]] = None,
                              **kwargs) -> InstallationResult:
        """
        Installe un seul package avec méthodes de fallback.
        
        Args:
            package_name: Nom du package à installer
            preferred_method: Méthode préférée
            fallback_methods: Méthodes de fallback si la préférée échoue
            **kwargs: Arguments supplémentaires
            
        Returns:
            InstallationResult: Résultat de l'installation
        """
        if self.is_cancelled:
            return InstallationResult(
                status=InstallationStatus.CANCELLED,
                message="Installation annulée par l'utilisateur",
                package_name=package_name,
                method=preferred_method
            )
        
        # Liste des méthodes à essayer
        methods_to_try = [preferred_method]
        if fallback_methods:
            methods_to_try.extend(fallback_methods)
        
        last_result = None
        
        for method in methods_to_try:
            if self.is_cancelled:
                return InstallationResult(
                    status=InstallationStatus.CANCELLED,
                    message="Installation annulée par l'utilisateur",
                    package_name=package_name,
                    method=method
                )
            
            installer = self.installers.get(method)
            if not installer:
                continue
            
            # MODE SIMULATION
            if self.simulation_mode:
                try:
                    # Utiliser la simulation au lieu de l'installateur réel
                    result = simulation.simulate_installation_by_method(method, package_name, **kwargs)
                    return result
                except Exception as e:
                    last_result = InstallationResult(
                        status=InstallationStatus.FAILED,
                        message=f"Erreur pendant la simulation {method.value}: {e}",
                        package_name=package_name,
                        method=method
                    )
                    continue

            # MODE RÉEL
            # Vérifier que l'installateur est disponible (avec protection)
            try:
                availability = installer.check_availability()
                if not availability.is_success:
                    if len(methods_to_try) == 1:
                        # Si c'est la seule méthode, retourner l'erreur
                        return availability
                    else:
                        # Sinon, essayer la méthode suivante
                        last_result = availability
                        continue
            except Exception as e:
                # Si la vérification de disponibilité plante, passer à la méthode suivante
                last_result = InstallationResult(
                    status=InstallationStatus.FAILED,
                    message=f"Erreur lors de la vérification de {method.value}: {e}",
                    package_name=package_name,
                    method=method
                )
                continue

            # Essayer l'installation (avec protection)
            try:
                result = installer.install_package(package_name, **kwargs)
            except Exception as e:
                # Si l'installation plante, créer un résultat d'erreur et continuer
                result = InstallationResult(
                    status=InstallationStatus.FAILED,
                    message=f"Erreur critique avec {method.value}: {e}",
                    package_name=package_name,
                    method=method
                )
                last_result = result
                continue
            
            # Si succès ou déjà installé, on s'arrête
            if result.is_success:
                return result
            
            # Si erreur fatale (package non trouvé, permissions), on s'arrête
            if result.status in [InstallationStatus.NOT_FOUND, 
                               InstallationStatus.PERMISSION_DENIED]:
                return result
            
            # Sinon, on essaie la méthode suivante
            last_result = result
        
        # Toutes les méthodes ont échoué
        return last_result or InstallationResult(
            status=InstallationStatus.FAILED,
            message=f"Aucune méthode d'installation disponible pour '{package_name}'",
            package_name=package_name,
            method=preferred_method
        )

    def install_package(self, package_name: str, **kwargs) -> InstallationResult:
        """
        Méthode pour installer un seul package (alias pour install_single_package).
        Utilisée par le thread pour la compatibilité.
        """
        return self.install_single_package(package_name, **kwargs)
    
    def check_system_compatibility(self) -> Dict[InstallationMethod, InstallationResult]:
        """
        Vérifie la compatibilité du système avec les différentes méthodes.

        Returns:
            Dict: Résultats de compatibilité par méthode
        """
        results = {}

        if self.simulation_mode:
            # En mode simulation, toutes les méthodes sont disponibles
            for method in InstallationMethod:
                results[method] = simulation.simulate_availability_check(method)
        else:
            # Mode réel
            for method, installer in self.installers.items():
                results[method] = installer.check_availability()

        return results
    
    def get_installation_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques d'installation.
        
        Returns:
            Dict: Statistiques détaillées
        """
        total = sum(self.installation_stats.values())
        
        stats = {
            'total_packages': total,
            'counts': self.installation_stats.copy(),
            'success_rate': 0.0 if total == 0 else (self.installation_stats['successful'] / total) * 100
        }
        
        return stats
    
    def _reset_stats(self) -> None:
        """Remet à zéro les statistiques."""
        for key in self.installation_stats:
            self.installation_stats[key] = 0
    
    def _update_stats(self, status: InstallationStatus) -> None:
        """Met à jour les statistiques selon le statut."""
        if status == InstallationStatus.SUCCESS:
            self.installation_stats['successful'] += 1
        elif status == InstallationStatus.ALREADY_INSTALLED:
            self.installation_stats['already_installed'] += 1
        elif status == InstallationStatus.NOT_FOUND:
            self.installation_stats['not_found'] += 1
        elif status == InstallationStatus.CANCELLED:
            self.installation_stats['cancelled'] += 1
        else:
            self.installation_stats['failed'] += 1
    
    def _emit_final_summary(self) -> None:
        """Émet un résumé final de l'installation."""
        stats = self.get_installation_stats()
        
        if stats['total_packages'] == 0:
            return
        
        summary_parts = []
        
        if stats['counts']['successful'] > 0:
            summary_parts.append(f"{stats['counts']['successful']} installés")
        
        if stats['counts']['already_installed'] > 0:
            summary_parts.append(f"{stats['counts']['already_installed']} déjà présents")
        
        if stats['counts']['failed'] > 0:
            summary_parts.append(f"{stats['counts']['failed']} échoués")
        
        if stats['counts']['not_found'] > 0:
            summary_parts.append(f"{stats['counts']['not_found']} non trouvés")
        
        if stats['counts']['cancelled'] > 0:
            summary_parts.append(f"{stats['counts']['cancelled']} annulés")
        
        summary = f"Installation terminée: {', '.join(summary_parts)} (sur {stats['total_packages']})"
        
        final_status = InstallationStatus.SUCCESS
        if stats['counts']['cancelled'] > 0:
            final_status = InstallationStatus.CANCELLED
        elif stats['counts']['failed'] > 0 or stats['counts']['not_found'] > 0:
            final_status = InstallationStatus.FAILED
        
        self.progress_tracker.emit_progress(100, summary, "Terminé", final_status)