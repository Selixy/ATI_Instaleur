"""
Charge et applique les styles QSS avec système de variables et thèmes.
Supporte la substitution de variables {{VAR}} et la combinaison base + thème.
"""

from typing import Optional, Dict
import re
from .style_finder import StyleFinder


class StyleLoader:
    """Charge et applique les styles QSS avec système de variables."""

    def __init__(self, debug: bool = True, mode: Optional[str] = None):
        self.debug = debug
        self.finder = StyleFinder(debug=debug, mode=mode)
        self._loaded_styles: Dict[str, str] = {}
        self._variable_cache: Dict[str, Dict[str, str]] = {}
        
        if self.debug:
            self._log(f"StyleLoader initialisé - Mode: {self.finder.mode}")

    def _log(self, message: str):
        """Affiche un message de debug si activé."""
        pass

    def _extract_variables(self, content: str) -> Dict[str, str]:
        """
        Extrait les variables depuis le contenu d'un fichier de thème.
        Format supporté: {{VARIABLE_NAME}}: valeur;
        
        Args:
            content: Contenu du fichier de thème
            
        Returns:
            Dict[str, str]: Variables extraites (nom -> valeur)
        """
        variables = {}
        
        # Pattern pour les définitions de variables: {{VAR}}: valeur;
        variable_pattern = re.compile(r'\{\{([A-Z0-9_]+)\}\}:\s*([^;]+);', re.MULTILINE)
        
        for match in variable_pattern.finditer(content):
            var_name = match.group(1)
            var_value = match.group(2).strip()
            variables[var_name] = var_value
            
        if variables and self.debug:
            self._log(f"Variables extraites: {list(variables.keys())}")
            
        return variables

    def _substitute_variables(self, content: str, variables: Dict[str, str]) -> str:
        """
        Remplace les variables {{VAR}} dans le contenu par leurs valeurs.
        
        Args:
            content: Contenu avec variables à remplacer
            variables: Dictionnaire des variables (nom -> valeur)
            
        Returns:
            str: Contenu avec variables substituées
        """
        if not variables:
            return content
        
        # Pattern pour les utilisations de variables: {{VAR}}
        usage_pattern = re.compile(r'\{\{([A-Z0-9_]+)\}\}')
        
        def replace_variable(match):
            var_name = match.group(1)
            if var_name in variables:
                return variables[var_name]
            else:
                if self.debug:
                    self._log(f"Variable non définie: {var_name}")
                return match.group(0)  # Garder tel quel si non définie
        
        result = usage_pattern.sub(replace_variable, content)
        
        # Compter les substitutions pour le debug
        if self.debug:
            substitutions = len(usage_pattern.findall(content))
            if substitutions > 0:
                self._log(f"Substitutions effectuées: {substitutions}")
        
        return result

    def _load_file_content(self, file_path) -> str:
        """
        Charge le contenu d'un fichier QSS.
        
        Args:
            file_path: Chemin du fichier à charger
            
        Returns:
            str: Contenu du fichier
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self._log(f"Fichier chargé: {file_path} ({len(content)} caractères)")
                return content
        except Exception as e:
            self._log(f"Erreur lors du chargement de {file_path}: {e}")
            return ""

    def _combine_styles(self, base_content: str, theme_content: str) -> str:
        """
        Combine le style de base avec le thème en appliquant les variables.
        
        Args:
            base_content: Contenu du fichier de base
            theme_content: Contenu du fichier de thème
            
        Returns:
            str: Style combiné avec variables substituées
        """
        # Extraire les variables du thème
        variables = self._extract_variables(theme_content)
        
        # Appliquer les variables au contenu de base
        processed_base = self._substitute_variables(base_content, variables)
        
        # Filtrer le contenu du thème pour ne garder que les styles (pas les définitions de variables)
        theme_styles = []
        for line in theme_content.splitlines():
            # Ignorer les lignes de définition de variables
            if not re.match(r'\s*\{\{[A-Z0-9_]+\}\}:\s*[^;]+;\s*$', line):
                theme_styles.append(line)
        
        theme_only_styles = '\n'.join(theme_styles).strip()
        
        # Combiner base + thème
        if theme_only_styles:
            combined = f"{processed_base}\n\n/* Styles du thème {self.finder.mode} */\n{theme_only_styles}"
        else:
            combined = processed_base
        
        return combined

    def load_qss_content(self, filename: str = "base.qss") -> Optional[str]:
        """
        Charge le contenu QSS complet (base + thème avec variables).
        
        Args:
            filename: Nom du fichier de base à charger
            
        Returns:
            Optional[str]: Contenu QSS combiné ou None si échec
        """
        cache_key = f"{filename}|{self.finder.mode}"
        
        # Vérifier le cache
        if cache_key in self._loaded_styles:
            self._log(f"Style trouvé dans le cache: {cache_key}")
            return self._loaded_styles[cache_key]

        self._log(f"Chargement du style: {filename} (mode: {self.finder.mode})")
        
        # Charger le fichier de base
        base_file = self.finder.find_qss_file(filename, prefer_mode=False)
        if not base_file:
            self._log(f"Fichier de base non trouvé: {filename}")
            return None
        
        base_content = self._load_file_content(base_file)
        if not base_content:
            return None

        # Charger le fichier de thème
        theme_file = self.finder.find_mode_file()
        theme_content = ""
        
        if theme_file:
            theme_content = self._load_file_content(theme_file)
            self._log(f"Thème chargé: {theme_file.name}")
        else:
            self._log(f"Aucun fichier de thème trouvé pour le mode '{self.finder.mode}'")

        # Combiner les styles
        try:
            combined_content = self._combine_styles(base_content, theme_content)
            
            # Mettre en cache
            self._loaded_styles[cache_key] = combined_content
            
            self._log(f"Style combiné généré ({len(combined_content)} caractères)")
            return combined_content
            
        except Exception as e:
            self._log(f"Erreur lors de la combinaison des styles: {e}")
            return base_content  # Fallback sur le contenu de base seulement

    def apply_style_to_app(self, app, filename: str = "base.qss") -> bool:
        """
        Applique un style à l'application Qt.
        
        Args:
            app: Instance de l'application Qt
            filename: Nom du fichier de base à appliquer
            
        Returns:
            bool: True si le style a été appliqué avec succès
        """
        self._log(f"Application du style '{filename}' à l'application")
        
        content = self.load_qss_content(filename)
        if not content:
            self._log("Aucun contenu de style à appliquer")
            return False
        
        try:
            app.setStyleSheet(content)
            self._log(f"Style appliqué avec succès ({len(content)} caractères)")
            return True
            
        except Exception as e:
            self._log(f"Erreur lors de l'application du style: {e}")
            return False

    def reload_style(self, app, filename: str = "base.qss") -> bool:
        """
        Recharge et applique un style en vidant d'abord le cache.
        
        Args:
            app: Instance de l'application Qt
            filename: Nom du fichier de base
            
        Returns:
            bool: True si le style a été rechargé et appliqué
        """
        self._log(f"Rechargement du style '{filename}'")
        
        # Vider les caches concernés
        keys_to_remove = [key for key in self._loaded_styles.keys() if key.startswith(filename)]
        for key in keys_to_remove:
            del self._loaded_styles[key]
        
        self.finder.clear_cache()
        
        return self.apply_style_to_app(app, filename)

    def switch_mode(self, app, new_mode: str, filename: str = "base.qss") -> bool:
        """
        Change le mode couleur et applique les styles correspondants.
        
        Args:
            app: Instance de l'application Qt
            new_mode: Nouveau mode ("light", "dark", etc.)
            filename: Nom du fichier de base
            
        Returns:
            bool: True si le changement a réussi
        """
        old_mode = self.finder.mode
        if old_mode == new_mode:
            self._log(f"Mode déjà actif: {new_mode}")
            return True
        
        self._log(f"Changement de mode: {old_mode} → {new_mode}")
        
        # Changer le mode
        self.finder.mode = new_mode
        
        # Vider les caches
        self.clear_cache()
        
        # Appliquer le nouveau style
        success = self.apply_style_to_app(app, filename)
        
        if success:
            self._log(f"Mode changé avec succès vers '{new_mode}'")
        else:
            self._log(f"Échec du changement de mode, retour à '{old_mode}'")
            self.finder.mode = old_mode
        
        return success

    def get_available_modes(self) -> list:
        """
        Retourne la liste des modes couleur disponibles.
        
        Returns:
            list: Liste des modes détectés
        """
        available_files = self.finder.list_available_files()
        modes = set()
        
        for theme_file in available_files['themes']:
            name = theme_file.stem.lower()
            
            # Patterns courants pour les noms de thèmes
            if name in ['light', 'dark']:
                modes.add(name)
            elif name.startswith('theme-'):
                modes.add(name[6:])  # Enlever "theme-"
            elif name.endswith('-theme'):
                modes.add(name[:-6])  # Enlever "-theme"
        
        return sorted(list(modes))

    def clear_cache(self):
        """Vide tous les caches."""
        old_size = len(self._loaded_styles)
        self._loaded_styles.clear()
        self._variable_cache.clear()
        self.finder.clear_cache()
        
        self._log(f"Tous les caches vidés ({old_size} styles, variables, fichiers)")

    def get_cache_info(self) -> Dict[str, int]:
        """
        Retourne des informations sur les caches.
        
        Returns:
            Dict[str, int]: Tailles des différents caches
        """
        return {
            'loaded_styles': len(self._loaded_styles),
            'variables': len(self._variable_cache),
            'finder_cache': len(self.finder._cache)
        }

    def debug_info(self):
        """Affiche des informations de debug détaillées."""
        pass