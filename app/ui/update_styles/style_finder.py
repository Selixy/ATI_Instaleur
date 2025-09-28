"""
Localise les fichiers QSS avec support PyInstaller et détection du thème système.
"""

from pathlib import Path
from typing import Optional, Dict, List
import platform
import sys

try:
    import winreg
except ImportError:
    winreg = None


class StyleFinder:
    """Localise les fichiers QSS avec support PyInstaller."""

    def __init__(self, debug: bool = True, mode: Optional[str] = None):
        self.debug = debug
        self._cache: Dict[str, Path] = {}
        self.mode = mode or self._detect_system_mode()
        self._is_frozen = getattr(sys, 'frozen', False)
        
        if self.debug:
            self._log(f"Initialisation StyleFinder - Mode: {self.mode}, Frozen: {self._is_frozen}")

    def _log(self, message: str):
        """Affiche un message de debug si activé."""
        pass

    def _detect_system_mode(self) -> str:
        """
        Détecte automatiquement le mode couleur du système.
        
        Returns:
            str: "light" ou "dark"
        """
        if platform.system() == "Windows" and winreg:
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                )
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                mode = "light" if value == 1 else "dark"
                self._log(f"Mode système détecté: {mode}")
                return mode
            except Exception as e:
                self._log(f"Impossible de détecter le mode système: {e}")
                return "light"
        else:
            self._log("Détection de mode non supportée sur cette plateforme")
            return "light"

    def _get_base_paths(self) -> List[Path]:
        """
        Retourne les chemins de base selon le contexte d'exécution.
        
        Returns:
            List[Path]: Chemins de base où chercher les styles
        """
        paths = []
        
        if self._is_frozen:
            # Mode PyInstaller - ressources extraites
            exe_dir = Path(sys.executable).parent
            meipass = Path(getattr(sys, "_MEIPASS", exe_dir))
            
            paths = [
                meipass / "ui" / "styles",
                meipass / "ui" / "update_styles", 
                exe_dir / "ui" / "styles",
                exe_dir / "ui" / "update_styles",
                # Fallback vers le répertoire de l'exécutable
                exe_dir / "styles",
            ]
        else:
            # Mode développement
            current_file = Path(__file__).resolve()
            # ui/update_styles/style_finder.py
            
            paths = [
                current_file.parent,  # ui/update_styles/
                current_file.parent.parent / "styles",  # ui/styles/
                current_file.parent.parent.parent / "styles",  # styles/ à la racine
            ]
        
        return paths

    def _get_search_paths(self, prefer_mode: bool) -> List[Path]:
        """
        Retourne les chemins de recherche selon le type de fichier.
        
        Args:
            prefer_mode: Si True, cherche dans les dossiers de couleurs en priorité
            
        Returns:
            List[Path]: Chemins ordonnés pour la recherche
        """
        base_paths = self._get_base_paths()
        search_paths = []
        
        if prefer_mode:
            # Priorité aux dossiers de couleurs
            for base in base_paths:
                search_paths.extend([
                    base / "color",
                    base / "colors", 
                    base / "themes",
                ])
            # Puis les dossiers de base
            search_paths.extend(base_paths)
        else:
            # Priorité aux dossiers de base
            search_paths.extend(base_paths)
            # Puis les dossiers de couleurs
            for base in base_paths:
                search_paths.extend([
                    base / "color",
                    base / "colors",
                    base / "themes",
                ])
        
        return search_paths

    def find_qss_file(self, filename: str, prefer_mode: bool = True) -> Optional[Path]:
        """
        Trouve un fichier QSS dans les chemins appropriés.
        
        Args:
            filename: Nom du fichier à chercher
            prefer_mode: Si True, cherche d'abord dans les dossiers de couleurs
            
        Returns:
            Optional[Path]: Chemin du fichier trouvé ou None
        """
        cache_key = f"{'mode' if prefer_mode else 'base'}_{filename}_{self.mode}"
        
        # Vérifier le cache
        if cache_key in self._cache:
            cached_path = self._cache[cache_key]
            if cached_path.exists():
                return cached_path
            else:
                # Le fichier en cache n'existe plus, le supprimer
                del self._cache[cache_key]

        search_paths = self._get_search_paths(prefer_mode)
        
        self._log(f"Recherche '{filename}' (prefer_mode={prefer_mode}) dans {len(search_paths)} chemins:")
        
        for path in search_paths:
            qss_file = path / filename
            self._log(f"  Vérification: {qss_file}")
            
            if qss_file.exists() and qss_file.is_file():
                self._log(f"OK Fichier trouvé: {qss_file}")
                self._cache[cache_key] = qss_file
                return qss_file

        self._log(f"ERROR Fichier '{filename}' introuvable")
        return None

    def find_mode_file(self, mode: Optional[str] = None) -> Optional[Path]:
        """
        Trouve le fichier de couleurs pour un mode donné.
        
        Args:
            mode: Mode couleur ou None pour utiliser le mode actuel
            
        Returns:
            Optional[Path]: Chemin du fichier de mode trouvé ou None
        """
        target_mode = mode or self.mode
        possible_names = [
            f"{target_mode}.qss",
            f"{target_mode}-theme.qss",
            f"theme-{target_mode}.qss",
        ]
        
        for name in possible_names:
            result = self.find_qss_file(name, prefer_mode=True)
            if result:
                return result
        
        return None

    def list_available_files(self) -> Dict[str, List[Path]]:
        """
        Liste tous les fichiers QSS disponibles par catégorie.
        
        Returns:
            Dict[str, List[Path]]: Fichiers groupés par catégorie
        """
        files = {
            'base': [],
            'themes': [],
            'other': []
        }
        
        search_paths = self._get_search_paths(prefer_mode=False)
        
        for path in search_paths:
            if not path.exists() or not path.is_dir():
                continue
                
            for qss_file in path.glob("*.qss"):
                filename = qss_file.name.lower()
                
                if filename in ['base.qss', 'main.qss', 'app.qss']:
                    files['base'].append(qss_file)
                elif any(theme in filename for theme in ['light', 'dark', 'theme']):
                    files['themes'].append(qss_file)
                else:
                    files['other'].append(qss_file)
        
        return files

    def clear_cache(self):
        """Vide le cache des fichiers trouvés."""
        old_size = len(self._cache)
        self._cache.clear()
        self._log(f"Cache vidé ({old_size} entrées supprimées)")

    def refresh_mode(self) -> str:
        """
        Actualise la détection du mode système.
        
        Returns:
            str: Nouveau mode détecté
        """
        old_mode = self.mode
        self.mode = self._detect_system_mode()
        
        if old_mode != self.mode:
            self._log(f"Mode changé: {old_mode} → {self.mode}")
            self.clear_cache()  # Vider le cache car le mode a changé
        
        return self.mode

    def debug_paths(self):
        """Affiche des informations détaillées pour le debug."""
        pass