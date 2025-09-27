"""
Module d'installation Winget - Version simplifiée !
Module: core.installer.winget
"""

from .installer import WingetInstaller

# Fonction utilitaire pour créer un installateur Winget configuré
def create_winget_installer():
    return WingetInstaller()

# Fonction pour vérifier la disponibilité de Winget
def is_winget_available():
    installer = WingetInstaller()
    result = installer.check_availability()
    return result.is_success

__all__ = [
    'WingetInstaller',
    'create_winget_installer',
    'is_winget_available'
]