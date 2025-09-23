from typing import Optional, Dict
import re
from .style_finder import StyleFinder


class StyleLoader:
    """Charge et applique les styles QSS avec {{VAR}}."""

    def __init__(self, debug: bool = True, mode: Optional[str] = None):
        self.debug = debug
        self.finder = StyleFinder(debug=debug, mode=mode)
        self._loaded_styles: Dict[str, str] = {}

    def _log(self, message: str):
        if self.debug:
            print(f"[StyleLoader] {message}")

    def _replace_placeholders(self, base_content: str, variant_content: str) -> str:
        definitions = {}
        for line in variant_content.splitlines():
            match = re.match(r"\{\{([A-Z0-9_]+)\}\}:\s*(.+);", line)
            if match:
                key, value = match.groups()
                definitions[key] = value

        pattern = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
        return pattern.sub(lambda m: definitions.get(m.group(1), m.group(0)), base_content)

    def load_qss_content(self, filename: str = "base.qss") -> Optional[str]:
        cache_key = f"{filename}|{self.finder.mode}"
        if cache_key in self._loaded_styles:
            return self._loaded_styles[cache_key]

        contents = []

        # Base
        base_file = self.finder.find_qss_file(filename, prefer_mode=False)
        if base_file:
            with open(base_file, "r", encoding="utf-8") as f:
                contents.append(f.read())

        # Variante
        variant_file = self.finder.find_qss_file(f"{self.finder.mode}.qss", prefer_mode=True)
        variant_content = ""
        if variant_file:
            with open(variant_file, "r", encoding="utf-8") as f:
                variant_content = f.read()

        if not contents:
            return None

        combined = "\n\n".join(contents)
        combined = self._replace_placeholders(combined, variant_content)
        self._loaded_styles[cache_key] = combined
        return combined

    def apply_style_to_app(self, app, filename: str = "base.qss") -> bool:
        content = self.load_qss_content(filename)
        if not content:
            return False
        try:
            app.setStyleSheet(content)
            return True
        except Exception as e:
            self._log(f"Erreur application style: {e}")
            return False

    def clear_cache(self):
        self._loaded_styles.clear()
        self.finder.clear_cache()
