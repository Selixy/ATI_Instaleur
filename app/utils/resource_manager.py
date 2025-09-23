"""
Gestionnaire de ressources unifié pour l'application.
Gère les chemins en développement et en production (PyInstaller).
"""

import sys
from pathlib import Path
from typing import Optional


class ResourceManager:
    """Gestionnaire centralisé des ressources de l'application."""
    
    def __init__(self):
        self._is_frozen = getattr(sys, 'frozen', False)
        self._project_root = self._determine_project_root()
        
        # Debug info
        print(f"Mode: {'Production (PyInstaller)' if self._is_frozen else 'Développement'}")
        print(f"Racine du projet: {self._project_root}")
    
    def _determine_project_root(self) -> Path:
        """Détermine la racine du projet selon le contexte d'exécution."""
        if self._is_frozen:
            # En mode PyInstaller, la racine est le dossier de l'exécutable
            return Path(sys.executable).parent
        else:
            # En développement, remonter jusqu'à la racine du projet
            current = Path(__file__).resolve()
            # app/utils/resource_manager.py -> app/ -> projet/
            return current.parent.parent.parent
    
    @property
    def is_frozen(self) -> bool:
        """Indique si l'app est en mode production (PyInstaller)."""
        return self._is_frozen
    
    @property
    def project_root(self) -> Path:
        """Racine du projet."""
        return self._project_root
    
    def get_config_path(self, filename: str = "config.yaml") -> Optional[Path]:
        """
        Retourne le chemin vers un fichier de configuration.
        
        Args:
            filename: Nom du fichier de config
            
        Returns:
            Path vers le fichier ou None si non trouvé
        """
        candidates = []
        
        if self._is_frozen:
            # En production, les configs sont dans le dossier de l'exe
            base = Path(sys.executable).parent
            candidates = [
                base / "config" / filename,
                base / filename,
            ]
        else:
            # En développement
            candidates = [
                self._project_root / "config" / filename,
                self._project_root / filename,
                self._project_root / "app" / "config" / filename,
            ]
        
        for candidate in candidates:
            if candidate.exists():
                return candidate
        
        return None
    
    def get_icon_path(self, icon_name: str) -> Optional[Path]:
        """
        Retourne le chemin vers une icône.
        
        Args:
            icon_name: Nom de l'icône (avec extension)
            
        Returns:
            Path vers l'icône ou None si non trouvée
        """
        candidates = []
        
        if self._is_frozen:
            # En production, les icônes sont extraites par PyInstaller
            meipass = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
            candidates = [
                meipass / "ui" / "icons" / icon_name,
                Path(sys.executable).parent / "ui" / "icons" / icon_name,
            ]
        else:
            # En développement
            candidates = [
                self._project_root / "app" / "ui" / "icons" / icon_name,
            ]
        
        for candidate in candidates:
            if candidate.exists():
                return candidate
        
        return None
    
    def get_style_path(self, style_name: str) -> Optional[Path]:
        """
        Retourne le chemin vers un fichier de style QSS.
        
        Args:
            style_name: Nom du fichier de style (avec .qss)
            
        Returns:
            Path vers le style ou None si non trouvé
        """
        candidates = []
        
        if self._is_frozen:
            # En production
            meipass = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
            candidates = [
                meipass / "ui" / "styles" / style_name,
                Path(sys.executable).parent / "ui" / "styles" / style_name,
            ]
        else:
            # En développement
            candidates = [
                self._project_root / "app" / "ui" / "styles" / style_name,
            ]
        
        for candidate in candidates:
            if candidate.exists():
                return candidate
        
        return None
    
    def debug_paths(self):
        """Affiche des informations de debug sur les chemins."""
        print("\n" + "="*50)
        print("DEBUG - CHEMINS DE RESSOURCES")
        print("="*50)
        print(f"Mode: {'Frozen' if self._is_frozen else 'Development'}")
        print(f"Project root: {self._project_root}")
        
        if self._is_frozen:
            print(f"Executable: {sys.executable}")
            if hasattr(sys, "_MEIPASS"):
                print(f"MEIPASS: {sys._MEIPASS}")
        
        # Test quelques ressources
        config = self.get_config_path()
        print(f"Config: {config if config else 'NON TROUVÉ'}")
        
        icon = self.get_icon_path("app.ico")
        print(f"Icône app: {icon if icon else 'NON TROUVÉ'}")
        
        print("="*50)


# Instance globale
_resource_manager: Optional[ResourceManager] = None

def get_resource_manager() -> ResourceManager:
    """Retourne l'instance globale du gestionnaire de ressources."""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager

def get_config_path(filename: str = "config.yaml") -> Optional[Path]:
    """Raccourci pour obtenir un chemin de configuration."""
    return get_resource_manager().get_config_path(filename)

def get_icon_path(icon_name: str) -> Optional[Path]:
    """Raccourci pour obtenir un chemin d'icône."""
    return get_resource_manager().get_icon_path(icon_name)

def get_style_path(style_name: str) -> Optional[Path]:
    """Raccourci pour obtenir un chemin de style."""
    return get_resource_manager().get_style_path(style_name)