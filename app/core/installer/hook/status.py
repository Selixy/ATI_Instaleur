"""
Énumérations et classes pour les statuts d'installation.
Module: core.installer.hook.status
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class InstallationStatus(Enum):
    """Statuts d'installation possibles."""
    NOT_STARTED = "not_started"
    CHECKING = "checking"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    ALREADY_INSTALLED = "already_installed"
    UPGRADE_AVAILABLE = "upgrade_available"
    NOT_FOUND = "not_found"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PERMISSION_DENIED = "permission_denied"
    NETWORK_ERROR = "network_error"
    CORRUPTED_INSTALL = "corrupted_install"
    INSTALLER_NOT_AVAILABLE = "installer_not_available"


class InstallationMethod(Enum):
    """Méthodes d'installation disponibles."""
    WINGET = "winget"
    CHOCOLATEY = "chocolatey"
    DIRECT_DOWNLOAD = "direct_download"
    MSI = "msi"
    EXE = "exe"


@dataclass
class InstallationResult:
    """Résultat d'une opération d'installation."""
    status: InstallationStatus
    message: str
    package_name: str = ""
    method: Optional[InstallationMethod] = None
    installed_version: str = ""
    available_version: str = ""
    raw_output: str = ""
    return_code: int = 0
    execution_time: float = 0.0
    
    @property
    def is_success(self) -> bool:
        """Vérifie si l'opération est un succès."""
        return self.status in [InstallationStatus.SUCCESS, InstallationStatus.ALREADY_INSTALLED]
    
    @property
    def is_error(self) -> bool:
        """Vérifie si l'opération est en erreur."""
        return self.status in [
            InstallationStatus.FAILED,
            InstallationStatus.NOT_FOUND,
            InstallationStatus.PERMISSION_DENIED,
            InstallationStatus.NETWORK_ERROR,
            InstallationStatus.CORRUPTED_INSTALL,
            InstallationStatus.INSTALLER_NOT_AVAILABLE
        ]
    
    @property
    def needs_user_action(self) -> bool:
        """Vérifie si une action utilisateur est nécessaire."""
        return self.status in [
            InstallationStatus.UPGRADE_AVAILABLE,
            InstallationStatus.PERMISSION_DENIED
        ]