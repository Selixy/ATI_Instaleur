from .YamlLoader import (
    get_yaml_loader,
    get_config_loader,
    YamlLoader,
    ConfigurationLoader,
    Application,
    InstallationMethod,
    ApplicationVersion,
    create_main_installer,
    get_available_methods
)

# Import sécurisé de l'installer
try:
    from .installer import ApplicationInstaller, InstallationStatus, InstallationProgress
except ImportError:
    # Créer des classes factices si l'installer n'est pas disponible
    ApplicationInstaller = None
    InstallationStatus = None
    InstallationProgress = None

__all__ = [
    'get_yaml_loader',
    'get_config_loader',
    'YamlLoader',
    'ConfigurationLoader',
    'Application',
    'InstallationMethod',
    'ApplicationVersion',
    'create_main_installer',
    'get_available_methods',
    'ApplicationInstaller',
    'InstallationStatus',
    'InstallationProgress'
]