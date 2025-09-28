"""
Module d'installation principal.
Module: core.installer
"""

# Import des classes principales
from .main_installer import MainInstaller

# Import des hooks communs
from .hook import (
    InstallationStatus,
    InstallationMethod, 
    InstallationResult,
    ProgressInfo,
    ProgressTracker,
    BaseInstaller
)

# Import des installateurs spécifiques
# Note: Les installateurs spécifiques sont importés de manière sécurisée dans main_installer.py


# Aliases pour compatibilité avec l'ancien code
ApplicationInstaller = MainInstaller  # Votre ancien nom
InstallationProgress = ProgressInfo    # Votre ancien nom


def create_main_installer() -> MainInstaller:
    """
    Factory function pour créer un installateur principal configuré.
    
    Returns:
        MainInstaller: Instance configurée et prête à l'emploi
    """
    return MainInstaller()


def get_available_methods() -> list:
    """
    Retourne les méthodes d'installation disponibles sur ce système.
    
    Returns:
        list: Liste des méthodes disponibles
    """
    installer = create_main_installer()
    compatibility = installer.check_system_compatibility()
    
    available = []
    for method, result in compatibility.items():
        if result.is_success:
            available.append(method)
    
    return available


__all__ = [
    # Classes principales
    'MainInstaller',
    
    # Hooks communs
    'InstallationStatus',
    'InstallationMethod', 
    'InstallationResult',
    'ProgressInfo',
    'ProgressTracker',
    'BaseInstaller',
    
    # Aliases pour compatibilité
    'ApplicationInstaller',  # = MainInstaller
    'InstallationProgress',  # = ProgressInfo
    
    # Factory functions
    'create_main_installer',
    'get_available_methods'
]