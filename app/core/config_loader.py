"""
Chargeur de configuration épuré pour les applications à installer.
Version avec support PyInstaller.
"""

import yaml
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class InstallationMethod:
    """Représente une méthode d'installation pour une application."""
    type: str  # winget, chocolatey, direct_download, etc.
    package: str = ""
    url: str = ""
    priority: int = 1
    extra_args: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.extra_args is None:
            self.extra_args = {}


@dataclass
class Application:
    """Représente une application à installer."""
    name: str
    description: str
    category: str
    icon: str = ""
    methods: List[InstallationMethod] = None
    requirements: List[str] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.methods is None:
            self.methods = []
        if self.requirements is None:
            self.requirements = []
    
    def get_preferred_method(self) -> Optional[InstallationMethod]:
        """Retourne la méthode d'installation préférée (priorité la plus basse)."""
        if not self.methods:
            return None
        return min(self.methods, key=lambda x: x.priority)
    
    def get_methods_by_type(self, method_type: str) -> List[InstallationMethod]:
        """Retourne toutes les méthodes d'un type donné."""
        return [method for method in self.methods if method.type == method_type]


class ConfigurationLoader:
    """Chargeur de configuration simplifié avec support PyInstaller."""
    
    def __init__(self, config_path: Optional[str] = None):
        self._is_frozen = getattr(sys, 'frozen', False)
        
        if config_path is None:
            self.config_path = self._find_config_file()
        else:
            self.config_path = Path(config_path)
        
        self.applications: List[Application] = []
        self.load_configuration()
    
    def _find_config_file(self) -> Optional[Path]:
        """Trouve le fichier de configuration selon le contexte d'exécution."""
        candidates = []
        
        if self._is_frozen:
            # Mode PyInstaller
            exe_dir = Path(sys.executable).parent
            meipass = Path(getattr(sys, "_MEIPASS", exe_dir))
            
            candidates = [
                exe_dir / "config" / "config.yaml",
                exe_dir / "config.yaml", 
                meipass / "config" / "config.yaml",
                meipass / "config.yaml",
            ]
        else:
            # Mode développement - chercher depuis la racine du projet
            current_file = Path(__file__).resolve()
            # core/config_loader.py -> core/ -> app/ -> projet/
            project_root = current_file.parent.parent.parent
            
            candidates = [
                project_root / "config" / "config.yaml",
                project_root / "config.yaml",
                project_root / "app" / "config" / "config.yaml",
                project_root / "app" / "config.yaml",
            ]
        
        # Debug
        print(f"[ConfigLoader] Mode: {'PyInstaller' if self._is_frozen else 'Développement'}")
        print(f"[ConfigLoader] Recherche config.yaml dans:")
        
        for candidate in candidates:
            print(f"  - {candidate}")
            if candidate.exists():
                print(f"  OK Trouvé: {candidate}")
                return candidate

        print("  ERROR config.yaml introuvable!")
        return None
    
    def load_configuration(self) -> None:
        """Charge la configuration depuis le fichier YAML."""
        if not self.config_path or not self.config_path.exists():
            print(f"[ERROR] Fichier de configuration non trouvé: {self.config_path}")
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)
            
            self._parse_applications(config_data.get('applications', []))
            print(f"[INFO] Configuration chargée: {len(self.applications)} applications depuis {self.config_path}")
            
        except yaml.YAMLError as e:
            print(f"[ERROR] Erreur YAML lors du chargement: {e}")
        except Exception as e:
            print(f"[ERROR] Erreur lors du chargement: {e}")
    
    def _parse_applications(self, apps_data: List[Dict]) -> None:
        """Parse les applications depuis la configuration."""
        self.applications = []
        
        for app_data in apps_data:
            try:
                methods = []
                for method_data in app_data.get('methods', []):
                    method = InstallationMethod(
                        type=method_data.get('type', ''),
                        package=method_data.get('package', ''),
                        url=method_data.get('url', ''),
                        priority=method_data.get('priority', 1),
                        extra_args=method_data.get('extra_args', {})
                    )
                    methods.append(method)
                
                app = Application(
                    name=app_data['name'],
                    description=app_data.get('description', ''),
                    category=app_data.get('category', 'Autres'),
                    icon=app_data.get('icon', ''),
                    methods=methods,
                    requirements=app_data.get('requirements', []),
                    enabled=app_data.get('enabled', True)
                )
                
                # Ne charger que les applications activées
                if app.enabled:
                    self.applications.append(app)
                    
            except KeyError as e:
                print(f"[WARNING] Application ignorée, champ requis manquant: {e}")
            except Exception as e:
                print(f"[WARNING] Erreur lors du parsing d'une application: {e}")
    
    # Méthodes d'accès public - signatures conservées
    
    def get_all_applications(self) -> List[Application]:
        """Retourne toutes les applications."""
        return self.applications.copy()
    
    def get_applications_by_category(self, category_name: str) -> List[Application]:
        """Retourne les applications d'une catégorie."""
        return [app for app in self.applications if app.category == category_name]
    
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


# Instance globale
_config_loader: Optional[ConfigurationLoader] = None

def get_config_loader() -> ConfigurationLoader:
    """Retourne l'instance globale du chargeur de configuration."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigurationLoader()
    return _config_loader

def reload_configuration() -> None:
    """Recharge la configuration."""
    global _config_loader
    if _config_loader is not None:
        _config_loader.load_configuration()