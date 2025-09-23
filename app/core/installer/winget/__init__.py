"""
Module d'installation Winget.
Module: core.installer.winget
"""

from .installer import WingetInstaller
from .parser import WingetOutputParser
from .validator import WingetValidator

# Fonction utilitaire pour créer un installateur Winget configuré
def create_winget_installer():
    """
    Factory function pour créer un installateur Winget.
    
    Returns:
        WingetInstaller: Instance configurée
    """
    return WingetInstaller()

# Fonction pour vérifier la disponibilité de Winget
def is_winget_available():
    """
    Vérifie rapidement si Winget est disponible.
    
    Returns:
        bool: True si Winget est disponible
    """
    installer = WingetInstaller()
    result = installer.check_availability()
    return result.is_success

__all__ = [
    'WingetInstaller', 
    'WingetOutputParser', 
    'WingetValidator',
    'create_winget_installer',
    'is_winget_available'
]