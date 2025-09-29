"""
Module YamlLoader - Chargeur unique pour configuration multi-fichiers YAML.
Remplace tous les anciens loaders et gère la structure organisée par dossiers de catégorie.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

# Import conditionnel pour éviter les erreurs de dépendances
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None


@dataclass
class InstallationMethod:
    """Représente une méthode d'installation pour une application."""
    type: str = ""
    package: str = ""
    url: str = ""
    priority: int = 1
    extra_args: Dict[str, Any] = None

    def __post_init__(self):
        if self.extra_args is None:
            self.extra_args = {}


@dataclass
class ApplicationVersion:
    """Représente une version spécifique d'une application."""
    name: str = ""
    version: str = ""
    methods: List[InstallationMethod] = None

    def __post_init__(self):
        if self.methods is None:
            self.methods = []


@dataclass
class Application:
    """Représente une application à installer."""
    name: str = ""
    description: str = ""
    category: str = ""
    icon: str = ""
    methods: List[InstallationMethod] = None
    requirements: List[str] = None
    enabled: bool = True
    has_versions: bool = False
    versions: List[ApplicationVersion] = None
    default_version_index: int = 0
    custom_install_path: bool = False
    source_file: str = ""

    def __post_init__(self):
        if self.methods is None:
            self.methods = []
        if self.requirements is None:
            self.requirements = []
        if self.versions is None:
            self.versions = []

    def get_preferred_method(self) -> Optional[InstallationMethod]:
        """Retourne la méthode d'installation préférée (priorité la plus basse)."""
        if not self.methods:
            return None
        return min(self.methods, key=lambda x: x.priority)

    def get_methods_by_type(self, method_type: str) -> List[InstallationMethod]:
        """Retourne toutes les méthodes d'un type donné."""
        return [method for method in self.methods if method.type == method_type]

    def get_default_version(self) -> Optional[ApplicationVersion]:
        """Retourne la version par défaut basée sur default_version_index."""
        if not self.has_versions or not self.versions:
            return None

        if 0 <= self.default_version_index < len(self.versions):
            return self.versions[self.default_version_index]

        return self.versions[0] if self.versions else None

    @property
    def is_success(self) -> bool:
        """Propriété pour compatibilité avec certains usages."""
        return self.enabled


class YamlLoader:
    """
    Chargeur YAML unique pour la configuration multi-fichiers organisée par dossiers.
    Remplace tous les anciens config_loader.
    """

    def __init__(self, config_dir: Optional[str] = None):
        self._is_frozen = getattr(sys, 'frozen', False)

        if config_dir is None:
            self.config_dir = self._find_config_directory()
        else:
            self.config_dir = Path(config_dir)

        self.applications: List[Application] = []
        self.files_by_category: Dict[str, List[str]] = {}

        self._load_all_configurations()

    def _find_config_directory(self) -> Optional[Path]:
        """Trouve le répertoire de configuration."""
        candidates = []

        if self._is_frozen:
            # Mode PyInstaller
            exe_dir = Path(sys.executable).parent
            meipass = Path(getattr(sys, "_MEIPASS", exe_dir))

            candidates = [
                exe_dir / "config",
                exe_dir / "app" / "config",
                meipass / "config",
                meipass / "app" / "config",
            ]
        else:
            # Mode développement
            current_file = Path(__file__).resolve()
            # core/YamlLoader.py -> core/ -> app/ -> projet/
            project_root = current_file.parent.parent.parent

            candidates = [
                project_root / "app" / "config",
                project_root / "config",
            ]

        for candidate in candidates:
            if candidate.exists() and candidate.is_dir():
                return candidate
        return None

    def _scan_category_directories(self) -> Dict[str, List[Path]]:
        """Scanne les dossiers de catégorie et trouve tous les fichiers YAML."""
        category_files = {}

        if not self.config_dir or not self.config_dir.exists():
            return category_files

        # Scanner tous les sous-dossiers
        for category_dir in self.config_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                category_name = category_dir.name
                yaml_files = []

                # Trouver tous les fichiers YAML dans ce dossier
                for yaml_file in category_dir.glob("*.yaml"):
                    yaml_files.append(yaml_file)
                for yml_file in category_dir.glob("*.yml"):
                    yaml_files.append(yml_file)

                if yaml_files:
                    category_files[category_name] = yaml_files

        return category_files

    def _load_yaml_file(self, yaml_file: Path) -> List[Dict]:
        """Charge un fichier YAML et retourne les applications."""
        if not YAML_AVAILABLE:
            return self._simulate_yaml_content(yaml_file)

        try:
            with open(yaml_file, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
            return data.get('applications', []) if data else []
        except Exception as e:
            return []

    def _simulate_yaml_content(self, yaml_file: Path) -> List[Dict]:
        """Simule le contenu YAML basé sur le nom du fichier (pour tests sans yaml module)."""
        file_name = yaml_file.stem
        folder_name = yaml_file.parent.name

        # Mapping des catégories
        category_mapping = {
            'CGI': '3D/Animation',
            'Developpement': 'Développement',
            'Graphisme': 'Graphisme',
            'Communication': 'Communication',
            'Utilitaires': 'Utilitaires'
        }

        category = category_mapping.get(folder_name, folder_name)

        # Simuler des applications basées sur les noms de fichiers connus
        simulated_apps = []

        if file_name == 'Maya':
            simulated_apps.append({
                'name': 'Autodesk Maya',
                'description': 'Logiciel de modélisation et d\'animation 3D',
                'category': category,
                'enabled': True,
                'has_versions': True,
                'default_version_index': 1,
                'versions': [
                    {'name': '2025', 'version': '2025', 'methods': [{'type': 'exe', 'url': 'https://autodesk.com/maya2025.exe', 'silent_args': '--mode unattended'}]},
                    {'name': '2024 (Recommandé)', 'version': '2024.3', 'methods': [{'type': 'exe', 'url': 'https://autodesk.com/maya2024.exe', 'silent_args': '--mode unattended'}]}
                ]
            })
        elif file_name == 'VS_Code':
            simulated_apps.append({
                'name': 'Visual Studio Code',
                'description': 'Éditeur de code source léger et puissant',
                'category': category,
                'enabled': True,
                'has_versions': True,
                'default_version_index': 0,
                'versions': [
                    {'name': 'Stable (Recommandé)', 'version': 'stable', 'methods': [{'type': 'exe', 'url': 'https://code.visualstudio.com/stable.exe', 'silent_args': '/verysilent'}]},
                    {'name': 'Insiders (Beta)', 'version': 'insiders', 'methods': [{'type': 'exe', 'url': 'https://code.visualstudio.com/insiders.exe', 'silent_args': '/verysilent'}]}
                ]
            })
        else:
            # Application générique
            app_name = file_name.replace('_', ' ')
            simulated_apps.append({
                'name': app_name,
                'description': f'Application {app_name}',
                'category': category,
                'enabled': True,
                'methods': [{'type': 'exe', 'url': f'https://example.com/{file_name.lower()}.exe', 'silent_args': '/S'}]
            })

        return simulated_apps

    def _parse_methods(self, methods_data: List[Dict]) -> List[InstallationMethod]:
        """Parse les méthodes d'installation."""
        methods = []
        for method_data in methods_data:
            method = InstallationMethod(
                type=method_data.get('type', ''),
                package=method_data.get('package', ''),
                url=method_data.get('url', ''),
                priority=method_data.get('priority', 1),
                extra_args=method_data.get('extra_args', {})
            )
            # Ajouter silent_args comme extra_args pour compatibilité
            if 'silent_args' in method_data:
                method.extra_args['silent_args'] = method_data['silent_args']

            methods.append(method)
        return methods

    def _parse_versions(self, versions_data: List[Dict]) -> List[ApplicationVersion]:
        """Parse les versions d'une application."""
        versions = []
        for version_data in versions_data:
            version_methods = self._parse_methods(version_data.get('methods', []))

            app_version = ApplicationVersion(
                name=version_data.get('name', ''),
                version=version_data.get('version', ''),
                methods=version_methods
            )
            versions.append(app_version)
        return versions

    def _parse_applications_from_file(self, yaml_file: Path, category_name: str) -> List[Application]:
        """Parse les applications depuis un fichier YAML."""
        applications = []

        apps_data = self._load_yaml_file(yaml_file)

        for app_data in apps_data:
            try:
                has_versions = app_data.get('has_versions', False)
                methods = []
                versions = []

                if has_versions:
                    versions = self._parse_versions(app_data.get('versions', []))
                else:
                    methods = self._parse_methods(app_data.get('methods', []))

                app = Application(
                    name=app_data['name'],
                    description=app_data.get('description', ''),
                    category=app_data.get('category', category_name),
                    icon=app_data.get('icon', ''),
                    methods=methods,
                    requirements=app_data.get('requirements', []),
                    enabled=app_data.get('enabled', True),
                    has_versions=has_versions,
                    versions=versions,
                    default_version_index=app_data.get('default_version_index', 0),
                    source_file=str(yaml_file)
                )

                if app.enabled:
                    applications.append(app)

            except KeyError as e:
                pass
            except Exception as e:
                pass

        return applications

    def _load_all_configurations(self) -> None:
        """Charge toutes les configurations depuis les dossiers de catégorie."""
        if not self.config_dir:
            print("[YamlLoader] Répertoire de configuration non trouvé")
            return

        # Scanner les dossiers de catégorie
        category_files = self._scan_category_directories()

        total_files = 0
        total_apps = 0

        # Charger chaque fichier YAML
        for category_name, yaml_files in category_files.items():
            self.files_by_category[category_name] = []

            for yaml_file in yaml_files:
                self.files_by_category[category_name].append(str(yaml_file))

                # Parser les applications de ce fichier
                apps = self._parse_applications_from_file(yaml_file, category_name)
                self.applications.extend(apps)

                total_files += 1
                total_apps += len(apps)

                print(f"[YamlLoader] Chargé {yaml_file.name}: {len(apps)} applications")

        print(f"[YamlLoader] Chargement terminé: {total_apps} applications depuis {total_files} fichiers")

    # Interface publique - API standardisée

    def get_all_applications(self) -> List[Application]:
        """Retourne toutes les applications."""
        return self.applications.copy()

    def get_applications_by_category(self, category_name: str) -> List[Application]:
        """Retourne les applications d'une catégorie."""
        return [app for app in self.applications if app.category == category_name]

    def get_applications_by_folder(self, folder_name: str) -> List[Application]:
        """Retourne les applications d'un dossier spécifique."""
        return [app for app in self.applications if folder_name in app.source_file]

    def get_application_by_name(self, name: str) -> Optional[Application]:
        """Retourne une application par son nom."""
        for app in self.applications:
            if app.name == name:
                return app
        return None

    def get_applications_names(self) -> List[str]:
        """Retourne la liste des noms d'applications."""
        return [app.name for app in self.applications]

    def get_applications_grouped_by_category(self) -> Dict[str, List[Application]]:
        """Retourne les applications groupées par catégorie."""
        grouped = {}
        for app in self.applications:
            grouped.setdefault(app.category, []).append(app)
        return grouped

    def get_applications_grouped_by_folder(self) -> Dict[str, List[Application]]:
        """Retourne les applications groupées par dossier source."""
        grouped = {}
        for app in self.applications:
            folder_name = Path(app.source_file).parent.name
            grouped.setdefault(folder_name, []).append(app)
        return grouped

    def get_category_folders(self) -> List[str]:
        """Retourne la liste des dossiers de catégorie trouvés."""
        return list(self.files_by_category.keys())

    def get_files_by_category(self) -> Dict[str, List[str]]:
        """Retourne les fichiers par catégorie."""
        return self.files_by_category.copy()

    def reload_configuration(self) -> None:
        """Recharge toute la configuration."""
        self.applications.clear()
        self.files_by_category.clear()
        self._load_all_configurations()

    # Méthodes de compatibilité avec l'ancien système

    def check_system_compatibility(self) -> Dict[str, Any]:
        """Vérifie la compatibilité système - simulation pour compatibilité."""
        from collections import namedtuple
        Result = namedtuple('Result', ['is_success'])

        return {
            'msi': Result(is_success=True),
            'exe': Result(is_success=True)
        }


# Instance globale unique
_yaml_loader_instance: Optional[YamlLoader] = None

def get_yaml_loader() -> YamlLoader:
    """Retourne l'instance globale unique du YamlLoader."""
    global _yaml_loader_instance
    if _yaml_loader_instance is None:
        _yaml_loader_instance = YamlLoader()
    return _yaml_loader_instance

def reload_yaml_configuration() -> None:
    """Recharge la configuration YAML."""
    global _yaml_loader_instance
    if _yaml_loader_instance is not None:
        _yaml_loader_instance.reload_configuration()

# Aliases pour compatibilité avec l'ancien système
get_config_loader = get_yaml_loader
ConfigurationLoader = YamlLoader

# Fonction factory pour compatibilité
def create_main_installer():
    """Factory function pour créer un installateur principal configuré."""
    # Retourner le YamlLoader pour compatibilité
    return get_yaml_loader()

def get_available_methods():
    """Retourne les méthodes d'installation disponibles sur ce système."""
    loader = get_yaml_loader()
    compatibility = loader.check_system_compatibility()

    available = []
    for method, result in compatibility.items():
        if result.is_success:
            available.append(method)

    return available