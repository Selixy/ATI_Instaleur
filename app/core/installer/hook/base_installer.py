"""
Classe de base abstraite pour tous les installateurs.
Module: core.installer.hook.base_installer
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import time

from .status import InstallationResult, InstallationStatus, InstallationMethod
from .progress import ProgressTracker


class BaseInstaller(ABC):
    """Classe de base abstraite pour tous les installateurs."""
    
    def __init__(self, method: InstallationMethod):
        self.method = method
        self.progress_tracker = ProgressTracker()
        self._is_available = None
        self._version_info = None
        self._last_check_time = 0
        self._cache_duration = 300  # 5 minutes de cache
    
    def set_progress_callback(self, callback) -> None:
        """Définit le callback de progression."""
        self.progress_tracker.set_callback(callback)
    
    def cancel_installation(self) -> None:
        """Annule l'installation en cours."""
        self.progress_tracker.cancel()
    
    @property
    def is_cancelled(self) -> bool:
        """Vérifie si l'installation est annulée."""
        return self.progress_tracker.is_cancelled
    
    @abstractmethod
    def check_availability(self, force_refresh: bool = False) -> InstallationResult:
        """
        Vérifie si l'installateur est disponible sur le système.
        
        Args:
            force_refresh: Force la vérification même si en cache
            
        Returns:
            InstallationResult: Résultat de la vérification
        """
        pass
    
    @abstractmethod
    def check_package_status(self, package_name: str) -> InstallationResult:
        """
        Vérifie le statut d'un package.
        
        Args:
            package_name: Nom du package à vérifier
            
        Returns:
            InstallationResult: Statut du package
        """
        pass
    
    @abstractmethod
    def install_package(self, package_name: str, **kwargs) -> InstallationResult:
        """
        Installe un package.
        
        Args:
            package_name: Nom du package à installer
            **kwargs: Arguments supplémentaires spécifiques à l'installateur
            
        Returns:
            InstallationResult: Résultat de l'installation
        """
        pass
    
    def install_with_retry(self, package_name: str, max_retries: int = 2, **kwargs) -> InstallationResult:
        """
        Installe un package avec retry automatique.
        
        Args:
            package_name: Nom du package à installer
            max_retries: Nombre maximum de tentatives
            **kwargs: Arguments supplémentaires
            
        Returns:
            InstallationResult: Résultat de l'installation
        """
        for attempt in range(max_retries + 1):
            if self.is_cancelled:
                return InstallationResult(
                    status=InstallationStatus.CANCELLED,
                    message="Installation annulée par l'utilisateur",
                    package_name=package_name,
                    method=self.method
                )
            
            if attempt > 0:
                self.progress_tracker.emit_message(
                    f"Tentative {attempt + 1}/{max_retries + 1} pour {package_name}"
                )
                time.sleep(2)  # Attendre entre les tentatives
            
            result = self.install_package(package_name, **kwargs)
            
            # Ne pas retry si c'est un succès ou certaines erreurs spécifiques
            if (result.is_success or 
                result.status in [InstallationStatus.NOT_FOUND, 
                                InstallationStatus.ALREADY_INSTALLED,
                                InstallationStatus.PERMISSION_DENIED]):
                return result
        
        # Toutes les tentatives ont échoué
        result.message = f"Échec après {max_retries + 1} tentatives: {result.message}"
        return result
    
    def _should_refresh_cache(self) -> bool:
        """Détermine si le cache doit être rafraîchi."""
        current_time = time.time()
        return (current_time - self._last_check_time) > self._cache_duration
    
    def _update_cache(self, is_available: bool, version_info: str) -> None:
        """Met à jour le cache."""
        self._is_available = is_available
        self._version_info = version_info
        self._last_check_time = time.time()
    
    def get_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur l'installateur.
        
        Returns:
            Dict: Informations sur l'installateur
        """
        availability = self.check_availability()
        return {
            'method': self.method.value,
            'available': availability.is_success,
            'version': self._version_info or "inconnue",
            'status': availability.status.value,
            'message': availability.message
        }