"""
Module d'installation Chocolatey - Version simplifiée !
Module: core.installer.chocolatey
"""

from .installer import ChocolateyInstaller

# Fonction utilitaire pour créer un installateur Chocolatey configuré
def create_chocolatey_installer():
    return ChocolateyInstaller()

# Fonction pour vérifier la disponibilité de Chocolatey
def is_chocolatey_available():
    try:
        import subprocess
        result = subprocess.run(['choco', '--version'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False  # On fait semblant qu'il n'est pas installé pour la simulation

__all__ = [
    'ChocolateyInstaller',
    'create_chocolatey_installer',
    'is_chocolatey_available'
]