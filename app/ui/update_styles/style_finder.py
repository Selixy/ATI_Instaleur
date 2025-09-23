from pathlib import Path
from typing import Optional, Dict, List
import platform

try:
    import winreg
except ImportError:
    winreg = None


class StyleFinder:
    """Localise les fichiers QSS."""

    def __init__(self, debug: bool = True, mode: Optional[str] = None):
        self.debug = debug
        self._cache: Dict[str, Path] = {}
        self.mode = mode or self._detect_system_mode()

    def _log(self, message: str):
        if self.debug:
            print(f"[StyleFinder] {message}")

    def _detect_system_mode(self) -> str:
        if platform.system() == "Windows" and winreg:
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                )
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return "light" if value == 1 else "dark"
            except Exception:
                return "light"
        return "light"

    def _get_search_paths(self, prefer_mode: bool) -> List[Path]:
        current_file = Path(__file__).resolve()
        if prefer_mode:
            return [
                current_file.parent / "color",
                current_file.parent.parent / "styles" / "color",
            ]
        else:
            return [
                current_file.parent,
                current_file.parent.parent / "styles",
            ]

    def find_qss_file(self, filename: str, prefer_mode: bool = True) -> Optional[Path]:
        cache_key = f"{'mode' if prefer_mode else 'base'}_{filename}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        for path in self._get_search_paths(prefer_mode):
            qss_file = path / filename
            if qss_file.exists():
                self._log(f"✓ Fichier trouvé: {qss_file}")
                self._cache[cache_key] = qss_file
                return qss_file

        self._log(f"❌ Fichier {filename} introuvable (prefer_mode={prefer_mode})")
        return None

    def clear_cache(self):
        self._cache.clear()
        self._log("Cache vidé")
