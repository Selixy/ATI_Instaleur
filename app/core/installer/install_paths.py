"""
Gestionnaire des chemins d'installation personnalisés.
Module: core.installer.install_paths
"""

import os
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class InstallationPaths:
    """Configuration des chemins d'installation."""
    base_path: str = ""
    use_custom_path: bool = False

    def get_install_path(self, app_name: str) -> Optional[str]:
        """
        Retourne le chemin d'installation pour une application.

        Args:
            app_name: Nom de l'application

        Returns:
            str: Chemin d'installation ou None pour utiliser le chemin par défaut
        """
        if not self.use_custom_path or not self.base_path:
            return None

        # Créer un chemin personnalisé pour l'application
        custom_path = os.path.join(self.base_path, app_name)
        return custom_path


class InstallPathManager:
    """Gestionnaire des chemins d'installation pour toutes les applications."""

    def __init__(self):
        self.config: Dict[str, InstallationPaths] = {}
        self.global_custom_path: Optional[str] = None

    def set_global_custom_path(self, path: str):
        """Définit un chemin personnalisé global pour toutes les applications."""
        self.global_custom_path = path

    def set_app_custom_path(self, app_name: str, path: str, enabled: bool = True):
        """
        Définit un chemin personnalisé pour une application spécifique.

        Args:
            app_name: Nom de l'application
            path: Chemin de base personnalisé
            enabled: Si True, utilise le chemin personnalisé
        """
        self.config[app_name] = InstallationPaths(
            base_path=path,
            use_custom_path=enabled
        )

    def get_install_arguments(self, app_name: str, app_config) -> str:
        """
        Génère les arguments d'installation avec le chemin personnalisé si nécessaire.

        Args:
            app_name: Nom de l'application
            app_config: Configuration de l'application depuis le YAML

        Returns:
            str: Arguments d'installation additionnels
        """
        # Vérifier si l'application autorise les chemins personnalisés
        if not getattr(app_config, 'custom_install_path', False):
            return ""

        # Obtenir le chemin personnalisé
        install_path = self._get_effective_install_path(app_name)
        if not install_path:
            return ""

        # Générer les arguments selon le type d'installateur
        return self._generate_path_arguments(install_path)

    def _get_effective_install_path(self, app_name: str) -> Optional[str]:
        """Obtient le chemin d'installation effectif pour une application."""
        # Priorité 1: Configuration spécifique à l'application
        if app_name in self.config:
            return self.config[app_name].get_install_path(app_name)

        # Priorité 2: Chemin global personnalisé
        if self.global_custom_path:
            return os.path.join(self.global_custom_path, app_name)

        return None

    def _generate_path_arguments(self, install_path: str) -> str:
        """
        Génère les arguments d'installation pour un chemin donné.

        Args:
            install_path: Chemin d'installation

        Returns:
            str: Arguments d'installation
        """
        # S'assurer que le répertoire existe
        os.makedirs(install_path, exist_ok=True)

        # Arguments communs pour les installateurs Windows
        # MSI: INSTALLDIR="path"
        # EXE: dépend de l'installateur, souvent --install-path ou --destination
        return f'INSTALLDIR="{install_path}"'


# Instance globale
_install_path_manager: Optional[InstallPathManager] = None

def get_install_path_manager() -> InstallPathManager:
    """Retourne l'instance globale du gestionnaire de chemins."""
    global _install_path_manager
    if _install_path_manager is None:
        _install_path_manager = InstallPathManager()
    return _install_path_manager