"""
Module d'installation Direct Download - Version simplifiée !
Module: core.installer.direct_download
"""

from .installer import DirectDownloadInstaller

# Fonction utilitaire pour créer un installateur Direct Download configuré
def create_direct_download_installer():
    return DirectDownloadInstaller()

# Fonction pour vérifier la disponibilité de Direct Download (toujours disponible)
def is_direct_download_available():
    return True

__all__ = [
    'DirectDownloadInstaller',
    'create_direct_download_installer',
    'is_direct_download_available'
]