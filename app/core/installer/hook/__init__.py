"""
Module hooks - Fonctions communes pour les installateurs.
Module: app.config.installer.hooks
"""

from .status import (
    InstallationStatus, 
    InstallationMethod, 
    InstallationResult
)
from .progress import (
    ProgressInfo, 
    ProgressTracker, 
    ProgressEstimator
)
from .base_installer import BaseInstaller

# Fonction utilitaire pour créer un tracker de progression
def create_progress_tracker():
    """
    Factory function pour créer un tracker de progression.
    
    Returns:
        ProgressTracker: Instance configurée
    """
    return ProgressTracker()

# Fonction pour créer un résultat d'erreur standard
def create_error_result(status: InstallationStatus, message: str, 
                       package_name: str = "", method: InstallationMethod = None):
    """
    Crée un InstallationResult d'erreur standardisé.
    
    Args:
        status: Statut d'erreur
        message: Message d'erreur
        package_name: Nom du package (optionnel)
        method: Méthode d'installation (optionnel)
    
    Returns:
        InstallationResult: Résultat d'erreur
    """
    return InstallationResult(
        status=status,
        message=message,
        package_name=package_name,
        method=method
    )

__all__ = [
    # Status
    'InstallationStatus',
    'InstallationMethod', 
    'InstallationResult',
    
    # Progress
    'ProgressInfo',
    'ProgressTracker',
    'ProgressEstimator',
    
    # Base
    'BaseInstaller',
    
    # Utilities
    'create_progress_tracker',
    'create_error_result'
]