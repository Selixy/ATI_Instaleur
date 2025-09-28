"""
Service de vérification du statut d'installation des applications.
Module: core.installer.status_checker
"""

from typing import Dict, List, Set
from core.installer.main_installer import MainInstaller
from core.installer.hook.status import InstallationStatus, InstallationMethod
from core.YamlLoader import Application


class InstallationStatusChecker:
    """Service pour vérifier le statut d'installation des applications."""

    def __init__(self):
        self.main_installer = MainInstaller()
        self._cache: Dict[str, bool] = {}

    def check_application_status(self, app: Application) -> bool:
        """
        Vérifie si une application est installée.

        Args:
            app: L'application à vérifier

        Returns:
            bool: True si l'application est installée, False sinon
        """
        # Vérifier le cache d'abord
        if app.name in self._cache:
            return self._cache[app.name]

        is_installed = False

        # Vérifier avec la méthode préférée
        preferred_method = app.get_preferred_method()
        if preferred_method:
            is_installed = self._check_with_method(app, preferred_method)

        # Si pas trouvé avec la méthode préférée, essayer les autres
        if not is_installed:
            for method in app.methods:
                if method != preferred_method:
                    if self._check_with_method(app, method):
                        is_installed = True
                        break

        # Mettre en cache le résultat
        self._cache[app.name] = is_installed
        return is_installed

    def _check_with_method(self, app: Application, method) -> bool:
        """
        Vérifie l'installation avec une méthode spécifique.

        Args:
            app: L'application à vérifier
            method: La méthode d'installation à utiliser

        Returns:
            bool: True si installé, False sinon
        """
        try:
            # Mapping des types de méthodes vers les enums
            method_mapping = {
                "winget": InstallationMethod.WINGET,
                "direct_download": InstallationMethod.DIRECT_DOWNLOAD,
                "msi": InstallationMethod.MSI,
                "exe": InstallationMethod.EXE,
                "chocolatey": InstallationMethod.CHOCOLATEY
            }

            method_enum = method_mapping.get(method.type)
            if not method_enum or method_enum not in self.main_installer.installers:
                return False

            installer = self.main_installer.installers[method_enum]

            # Déterminer le package ID selon la méthode
            package_id = self._get_package_id_for_method(app, method)
            if not package_id:
                return False

            # Vérifier le statut
            result = installer.check_package_status(package_id)
            return result.status == InstallationStatus.ALREADY_INSTALLED

        except Exception:
            # En cas d'erreur, on considère que ce n'est pas installé
            return False

    def _get_package_id_for_method(self, app: Application, method) -> str:
        """
        Obtient le package ID approprié selon la méthode d'installation.

        Args:
            app: L'application
            method: La méthode d'installation

        Returns:
            str: Le package ID ou nom pour la vérification
        """
        # Pour Winget et Chocolatey, utiliser le package ID
        if method.type in ["winget", "chocolatey"]:
            return method.package if hasattr(method, 'package') and method.package else app.name

        # Pour les autres méthodes, utiliser le nom de l'application
        return app.name

    def check_multiple_applications(self, apps: List[Application]) -> Dict[str, bool]:
        """
        Vérifie le statut de plusieurs applications en parallèle.

        Args:
            apps: Liste des applications à vérifier

        Returns:
            Dict[str, bool]: Statut d'installation par nom d'application
        """
        results = {}
        for app in apps:
            results[app.name] = self.check_application_status(app)
        return results

    def get_installed_applications(self, apps: List[Application]) -> List[str]:
        """
        Retourne la liste des noms d'applications installées.

        Args:
            apps: Liste des applications à vérifier

        Returns:
            List[str]: Noms des applications installées
        """
        installed = []
        for app in apps:
            if self.check_application_status(app):
                installed.append(app.name)
        return installed

    def get_not_installed_applications(self, apps: List[Application]) -> List[str]:
        """
        Retourne la liste des noms d'applications non installées.

        Args:
            apps: Liste des applications à vérifier

        Returns:
            List[str]: Noms des applications non installées
        """
        not_installed = []
        for app in apps:
            if not self.check_application_status(app):
                not_installed.append(app.name)
        return not_installed

    def clear_cache(self):
        """Vide le cache des statuts d'installation."""
        self._cache.clear()

    def refresh_application_status(self, app_name: str):
        """
        Force la re-vérification du statut d'une application.

        Args:
            app_name: Nom de l'application à rafraîchir
        """
        if app_name in self._cache:
            del self._cache[app_name]


# Instance globale pour un accès facile
_status_checker_instance: InstallationStatusChecker = None

def get_status_checker() -> InstallationStatusChecker:
    """Retourne l'instance globale du vérificateur de statut."""
    global _status_checker_instance
    if _status_checker_instance is None:
        _status_checker_instance = InstallationStatusChecker()
    return _status_checker_instance