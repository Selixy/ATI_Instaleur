"""
Module d'installation MSI - Version simplifiée !
Module: core.installer.msi
"""

from .installer import MsiInstaller

# Fonction utilitaire pour créer un installateur MSI configuré
def create_msi_installer():
    return MsiInstaller()

# Fonction pour vérifier la disponibilité de MSI (Windows seulement)
def is_msi_available():
    import platform
    return platform.system() == "Windows"

__all__ = [
    'MsiInstaller',
    'create_msi_installer',
    'is_msi_available'
]