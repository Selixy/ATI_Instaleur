"""
Module d'installation EXE - Version simplifiée !
Module: core.installer.exe
"""

from .installer import ExeInstaller

# Fonction utilitaire pour créer un installateur EXE configuré
def create_exe_installer():
    return ExeInstaller()

# Fonction pour vérifier la disponibilité de EXE (toujours disponible)
def is_exe_available():
    return True

__all__ = [
    'ExeInstaller',
    'create_exe_installer',
    'is_exe_available'
]