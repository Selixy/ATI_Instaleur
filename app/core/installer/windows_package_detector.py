"""
Détecteur de packages installés sur Windows.
Module: core.installer.windows_package_detector

Utilise le registre Windows
(même méthode que le Panneau de configuration Windows)
"""

import winreg
import re
from typing import Dict, Set, Optional


class WindowsPackageDetector:
    """
    Détecte les packages installés sur Windows via le registre.

    Méthode standard recommandée par Microsoft et la communauté :
    - Rapide et fiable
    - Même source que "Ajout/Suppression de programmes"
    - Détecte plus d'applications que Win32_Product
    """

    def __init__(self):
        self._installed_programs_cache: Optional[Dict[str, Dict]] = None

    def is_package_installed_by_name(self, app_name: str, version: str = None) -> bool:
        """
        Vérifie si une application est installée par son nom et optionnellement sa version.

        Args:
            app_name: Nom de l'application (ex: "Visual Studio Code")
            version: Version spécifique à vérifier (ex: "4.5.3", "2024")

        Returns:
            bool: True si installée, False sinon
        """
        if not app_name or not app_name.strip():
            return False

        installed_programs = self.get_installed_programs()
        clean_search = self._normalize_name(app_name)

        # Si version spécifiée, recherche version-spécifique
        if version:
            return self._check_version_specific(clean_search, version, installed_programs)

        # Sinon, recherche générale (ancien comportement)
        return self._check_general(clean_search, installed_programs)

    def _check_general(self, clean_search: str, installed_programs: Dict[str, Dict]) -> bool:
        """Vérification générale sans version spécifique."""
        # Recherche dans les noms des programmes installés
        for program_name in installed_programs.keys():
            clean_program = self._normalize_name(program_name)

            # Correspondance exacte
            if clean_search == clean_program:
                return True

            # Correspondance partielle (le nom cherché doit être un "mot" complet)
            if self._is_word_match(clean_search, clean_program):
                return True

        # Recherche étendue pour les variations de noms
        return self._extended_search(clean_search, installed_programs)

    def _check_version_specific(self, clean_search: str, version: str, installed_programs: Dict[str, Dict]) -> bool:
        """Vérification avec version spécifique."""
        version_clean = self._normalize_version(version)

        for program_name, program_info in installed_programs.items():
            clean_program = self._normalize_name(program_name)

            # Vérifier si le nom correspond
            name_matches = (
                clean_search == clean_program or
                self._is_word_match(clean_search, clean_program)
            )

            if name_matches:
                # Vérifier la version
                if self._version_matches(program_name, program_info, version_clean):
                    return True

        return False

    def _normalize_version(self, version: str) -> str:
        """Normalise une version pour la comparaison."""
        if not version:
            return ""
        # Garder seulement les chiffres et points, supprimer les espaces
        import re
        normalized = re.sub(r'[^\d\.]', '', version.strip())
        return normalized

    def _version_matches(self, program_name: str, program_info: Dict, target_version: str) -> bool:
        """Vérifie si la version correspond."""
        if not target_version:
            return True

        # Sources de version à vérifier
        version_sources = [
            program_info.get('Version', ''),
            program_info.get('DisplayVersion', ''),
            program_name  # Version peut être dans le nom
        ]

        target_clean = target_version.lower()

        for version_source in version_sources:
            if not version_source:
                continue

            version_clean = str(version_source).lower()

            # Correspondance exacte seulement
            if target_clean == version_clean:
                return True

            # Correspondances spécifiques pour années seulement (Maya 2024, etc.)
            if len(target_clean) == 4 and target_clean.isdigit():
                if target_clean in version_clean:
                    return True

            # Pour les versions avec points, être très strict
            if '.' in target_clean:
                # Seulement pour les années dans le format version (ex: 2024.3)
                version_parts = target_clean.split('.')
                version_major = version_parts[0]

                # Si c'est une année, permettre correspondance partielle
                if len(version_major) == 4 and version_major.isdigit():
                    if version_major in version_clean:
                        return True

                # Pour les autres versions (4.2.1, etc.), correspondance exacte seulement
                # Ne pas faire de correspondance partielle

        return False

    def _extended_search(self, clean_search: str, installed_programs: Dict[str, Dict]) -> bool:
        """Recherche étendue pour les variations de noms courantes."""

        # Variations courantes
        search_variations = [clean_search]

        # Ajouter des variations communes
        if not clean_search.endswith('2'):
            search_variations.append(clean_search + '2')  # DJV -> DJV2

        if not clean_search.endswith(' 2'):
            search_variations.append(clean_search + ' 2')

        # Variations avec des mots clés
        common_prefixes = ['microsoft ', 'adobe ', 'autodesk ', '']
        common_suffixes = [' client', ' app', ' application', ' tool', ' viewer', ' player']

        for prefix in common_prefixes:
            for suffix in common_suffixes:
                variation = prefix + clean_search + suffix
                if variation != clean_search:
                    search_variations.append(variation)

        # Tester toutes les variations
        for variation in search_variations:
            for program_name in installed_programs.keys():
                clean_program = self._normalize_name(program_name)

                # Correspondance exacte avec variation
                if variation == clean_program:
                    return True

                # Le nom de l'app est contenu au début du programme
                if clean_program.startswith(variation + ' '):
                    return True

        return False

    def get_installed_programs(self) -> Dict[str, Dict]:
        """
        Retourne la liste complète des programmes installés depuis le registre.

        Returns:
            Dict[str, Dict]: {nom_programme: {version, publisher, install_date, ...}}
        """
        if self._installed_programs_cache is None:
            self._installed_programs_cache = self._load_from_registry()

        return self._installed_programs_cache

    def _load_from_registry(self) -> Dict[str, Dict]:
        """Charge la liste des programmes depuis le registre Windows."""
        programs = {}

        # Clés de registre standard (même source que Ajout/Suppression de programmes)
        registry_paths = [
            # Applications 64-bit
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            # Applications 32-bit sur système 64-bit
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            # Applications utilisateur
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            # Applications Windows Store/UWP (HKCU)
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\PackageFor"),
            # Applications avec entrées spéciales
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes\Installer\Products")
        ]

        for hkey, path in registry_paths:
            try:
                programs.update(self._read_registry_key(hkey, path))
            except Exception:
                # Ignorer les erreurs et continuer avec les autres clés
                continue

        return programs

    def _read_registry_key(self, hkey: int, path: str) -> Dict[str, Dict]:
        """Lit une clé de registre et extrait les informations des programmes."""
        programs = {}

        try:
            with winreg.OpenKey(hkey, path) as uninstall_key:
                i = 0
                while True:
                    try:
                        # Énumérer les sous-clés
                        subkey_name = winreg.EnumKey(uninstall_key, i)

                        try:
                            with winreg.OpenKey(uninstall_key, subkey_name) as subkey:
                                program_info = self._extract_program_info(subkey)
                                if program_info and 'DisplayName' in program_info:
                                    display_name = program_info['DisplayName']
                                    # Éviter les doublons
                                    if display_name not in programs:
                                        programs[display_name] = program_info

                        except Exception:
                            # Ignorer les sous-clés inaccessibles
                            pass

                        i += 1

                    except OSError:
                        # Fin de l'énumération
                        break

        except Exception:
            # Clé inaccessible
            pass

        return programs

    def _extract_program_info(self, subkey) -> Optional[Dict]:
        """Extrait les informations d'un programme depuis une sous-clé de registre."""
        try:
            # Lire DisplayName (obligatoire)
            display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")

            # Filtrer les entrées système et mises à jour
            if self._should_skip_entry(display_name):
                return None

            program_info = {'DisplayName': display_name}

            # Informations optionnelles
            optional_fields = {
                'DisplayVersion': 'Version',
                'Publisher': 'Publisher',
                'InstallDate': 'InstallDate',
                'InstallLocation': 'InstallLocation',
                'UninstallString': 'UninstallString'
            }

            for reg_key, info_key in optional_fields.items():
                try:
                    value, _ = winreg.QueryValueEx(subkey, reg_key)
                    if value:
                        program_info[info_key] = value
                except FileNotFoundError:
                    pass

            return program_info

        except FileNotFoundError:
            # Pas de DisplayName = pas un programme valide
            return None
        except Exception:
            # Autre erreur
            return None

    def _should_skip_entry(self, display_name: str) -> bool:
        """Détermine si une entrée doit être ignorée (mise à jour système, etc.)."""
        if not display_name:
            return True

        skip_patterns = [
            r'^Security Update for',
            r'^Update for',
            r'^Hotfix for',
            r'^Microsoft Visual C\+\+ \d{4} Redistributable',
            r'KB\d+',
            r'^Microsoft \.NET Framework',
            r'^Windows Software Development Kit',
        ]

        for pattern in skip_patterns:
            if re.search(pattern, display_name, re.IGNORECASE):
                return True

        return False

    def _normalize_name(self, name: str) -> str:
        """Normalise un nom pour la comparaison."""
        if not name:
            return ""

        # Convertir en minuscules et supprimer espaces extra
        normalized = re.sub(r'\s+', ' ', name.lower().strip())

        # Supprimer les caractères spéciaux courants mais garder les tirets
        normalized = re.sub(r'[^\w\s\-\+\#]', ' ', normalized)

        # Normaliser les espaces
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        return normalized

    def _is_word_match(self, search_term: str, target: str) -> bool:
        """Vérifie si le terme recherché correspond comme mot complet dans la cible."""
        if not search_term or not target:
            return False

        # Le terme doit être présent comme mots complets
        search_words = search_term.split()
        target_words = target.split()

        # Pour les noms d'une seule mot, être plus strict
        if len(search_words) == 1:
            search_word = search_words[0]
            # Le mot doit être significatif (au moins 4 caractères)
            if len(search_word) < 4:
                return False

            # Correspondance stricte pour mots simples
            for target_word in target_words:
                # Correspondance exacte
                if search_word == target_word:
                    return True

                # Le mot cible doit commencer par le mot recherché (et être assez long)
                # Ex: "discord" match "Discord" mais pas "disc"
                if (len(target_word) >= len(search_word) and
                    target_word.startswith(search_word) and
                    len(search_word) >= len(target_word) * 0.7):  # Au moins 70% de la longueur
                    return True

            return False

        # Pour les noms multi-mots, au moins 80% des mots doivent matcher
        found_words = 0
        for search_word in search_words:
            if len(search_word) >= 3:  # Ignorer les mots très courts
                for target_word in target_words:
                    # Correspondance stricte pour multi-mots
                    if (search_word == target_word or
                        target_word.startswith(search_word) or
                        search_word.startswith(target_word)):
                        found_words += 1
                        break

        if len(search_words) == 0:
            return False

        return (found_words / len(search_words)) >= 0.8

    def clear_cache(self):
        """Vide le cache des programmes installés."""
        self._installed_programs_cache = None

    def debug_search(self, app_name: str) -> Dict[str, any]:
        """
        Debug: retourne des informations détaillées sur la recherche.

        Args:
            app_name: Nom de l'application à rechercher

        Returns:
            Dict contenant les détails de la recherche
        """
        installed_programs = self.get_installed_programs()
        clean_search = self._normalize_name(app_name)

        matches = []
        exact_matches = []

        for program_name, program_info in installed_programs.items():
            clean_program = self._normalize_name(program_name)

            if clean_search == clean_program:
                exact_matches.append(program_name)
            elif self._is_word_match(clean_search, clean_program):
                matches.append(program_name)

        return {
            "original_name": app_name,
            "normalized_search": clean_search,
            "exact_matches": exact_matches,
            "partial_matches": matches[:5],  # Limiter pour debug
            "total_programs": len(installed_programs),
            "found": len(exact_matches) > 0 or len(matches) > 0
        }

    # Méthodes de compatibilité pour l'ancien système supprimées
    # Plus de support pour winget, chocolatey et direct_download

    def get_installed_programs_list(self) -> Set[str]:
        """
        Méthode de compatibilité - retourne les noms des programmes.
        """
        return set(self.get_installed_programs().keys())


# Instance globale
_detector_instance: Optional[WindowsPackageDetector] = None

def get_windows_detector() -> WindowsPackageDetector:
    """Retourne l'instance globale du détecteur Windows."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = WindowsPackageDetector()
    return _detector_instance