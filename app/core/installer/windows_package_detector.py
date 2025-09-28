"""
Détecteur de packages installés sur Windows.
Module: core.installer.windows_package_detector
"""

import subprocess
import platform
import winreg
from typing import List, Dict, Set, Optional
from pathlib import Path


class WindowsPackageDetector:
    """Détecte les packages installés sur Windows via différentes méthodes."""

    def __init__(self):
        self._winget_cache: Optional[Set[str]] = None
        self._uninstall_cache: Optional[Set[str]] = None
        self._programs_cache: Optional[Set[str]] = None

    def is_package_installed_by_winget(self, package_id: str) -> bool:
        """
        Vérifie si un package est installé via Winget.

        Args:
            package_id: ID du package Winget (ex: "Microsoft.VisualStudioCode")

        Returns:
            bool: True si installé, False sinon
        """
        if not self._is_winget_available():
            return False

        try:
            # Utiliser le cache si disponible
            if self._winget_cache is None:
                self._load_winget_packages()

            if self._winget_cache is None:
                return False

            # Vérifier différentes variantes du nom
            return any(
                package_id.lower() in installed.lower() or
                installed.lower() in package_id.lower()
                for installed in self._winget_cache
            )

        except Exception:
            return False

    def is_package_installed_by_name(self, app_name: str) -> bool:
        """
        Vérifie si une application est installée par son nom.

        Args:
            app_name: Nom de l'application (ex: "Visual Studio Code")

        Returns:
            bool: True si installée, False sinon
        """
        # Nettoyer le nom pour la recherche
        clean_name = self._clean_app_name(app_name)

        # Vérifier dans le registre des programmes installés
        if self._check_in_uninstall_registry(clean_name):
            return True

        # Vérifier dans Program Files
        if self._check_in_program_files(clean_name):
            return True

        return False

    def get_installed_programs_list(self) -> Set[str]:
        """
        Retourne la liste de tous les programmes installés.

        Returns:
            Set[str]: Ensemble des noms de programmes installés
        """
        if self._programs_cache is None:
            self._load_installed_programs()

        return self._programs_cache or set()

    def _is_winget_available(self) -> bool:
        """Vérifie si Winget est disponible."""
        try:
            result = subprocess.run(
                ["winget", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def _load_winget_packages(self):
        """Charge la liste des packages Winget installés."""
        try:
            result = subprocess.run(
                ["winget", "list"],
                capture_output=True,
                text=True,
                timeout=10,  # Timeout réduit
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )

            if result.returncode != 0:
                self._winget_cache = set()
                return

            packages = set()
            lines = result.stdout.split('\n')

            # Ignorer les premières lignes d'en-tête
            for line in lines[2:]:
                if line.strip() and not line.startswith('-'):
                    # Extraire le nom et l'ID du package
                    parts = line.split()
                    if len(parts) >= 2:
                        packages.add(parts[0])  # Nom
                        if len(parts) >= 3:
                            packages.add(parts[1])  # ID

            self._winget_cache = packages

        except Exception:
            self._winget_cache = set()

    def _load_installed_programs(self):
        """Charge la liste de tous les programmes installés."""
        programs = set()

        # Registre des programmes installés
        programs.update(self._get_uninstall_registry_programs())

        # Program Files
        programs.update(self._get_program_files_programs())

        self._programs_cache = programs

    def _get_uninstall_registry_programs(self) -> Set[str]:
        """Récupère les programmes depuis le registre de désinstallation."""
        programs = set()

        # Clés de registre à vérifier
        registry_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]

        for hkey, subkey_path in registry_keys:
            try:
                with winreg.OpenKey(hkey, subkey_path) as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                                    if display_name:
                                        programs.add(display_name.strip())
                                except FileNotFoundError:
                                    pass
                            i += 1
                        except OSError:
                            break
            except Exception:
                continue

        return programs

    def _get_program_files_programs(self) -> Set[str]:
        """Récupère les programmes depuis Program Files."""
        programs = set()

        program_dirs = [
            Path(r"C:\Program Files"),
            Path(r"C:\Program Files (x86)"),
        ]

        # Ajouter le dossier utilisateur AppData
        user_dir = Path.home() / "AppData" / "Local" / "Programs"
        if user_dir.exists():
            program_dirs.append(user_dir)

        for prog_dir in program_dirs:
            if prog_dir.exists():
                try:
                    for item in prog_dir.iterdir():
                        if item.is_dir():
                            programs.add(item.name)
                except Exception:
                    continue

        return programs

    def _check_in_uninstall_registry(self, app_name: str) -> bool:
        """Vérifie dans le registre de désinstallation."""
        if self._uninstall_cache is None:
            self._uninstall_cache = self._get_uninstall_registry_programs()

        clean_search = app_name.lower()
        return any(clean_search in installed.lower() for installed in self._uninstall_cache)

    def _check_in_program_files(self, app_name: str) -> bool:
        """Vérifie dans les dossiers Program Files."""
        program_files = self._get_program_files_programs()
        clean_search = app_name.lower()
        return any(clean_search in folder.lower() for folder in program_files)

    def _clean_app_name(self, app_name: str) -> str:
        """Nettoie le nom d'une application pour la recherche."""
        # Supprimer les mots courants qui peuvent perturber la recherche
        words_to_remove = [
            "the", "and", "or", "for", "with", "by", "inc", "corp", "corporation",
            "ltd", "limited", "software", "app", "application", "program", "tool",
            "suite", "pack", "package", "edition", "version", "v", "professional",
            "pro", "standard", "express", "community", "enterprise", "ultimate",
            "premium", "free", "lite", "basic", "advanced", "full"
        ]

        clean = app_name.lower()

        # Supprimer les versions (ex: "2024", "v1.0")
        import re
        clean = re.sub(r'\b(v?\d+\.?\d*)\b', '', clean)

        # Supprimer les mots courants
        for word in words_to_remove:
            clean = clean.replace(f" {word} ", " ")
            clean = clean.replace(f" {word}", "")
            clean = clean.replace(f"{word} ", "")

        # Nettoyer les espaces multiples et caractères spéciaux
        clean = re.sub(r'[^\w\s]', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()

        return clean

    def clear_cache(self):
        """Vide tous les caches."""
        self._winget_cache = None
        self._uninstall_cache = None
        self._programs_cache = None

    def debug_search(self, app_name: str) -> Dict[str, any]:
        """
        Debug: retourne des informations détaillées sur la recherche.

        Args:
            app_name: Nom de l'application à rechercher

        Returns:
            Dict contenant les détails de la recherche
        """
        clean_name = self._clean_app_name(app_name)

        # Récupérer les listes
        if self._uninstall_cache is None:
            self._uninstall_cache = self._get_uninstall_registry_programs()

        program_files = self._get_program_files_programs()

        # Rechercher des correspondances partielles
        registry_matches = [
            prog for prog in self._uninstall_cache
            if clean_name.lower() in prog.lower() or prog.lower() in clean_name.lower()
        ]

        pf_matches = [
            folder for folder in program_files
            if clean_name.lower() in folder.lower() or folder.lower() in clean_name.lower()
        ]

        return {
            "original_name": app_name,
            "cleaned_name": clean_name,
            "registry_matches": registry_matches[:5],  # Limiter à 5 pour debug
            "program_files_matches": pf_matches[:5],
            "found_in_registry": len(registry_matches) > 0,
            "found_in_program_files": len(pf_matches) > 0,
            "total_registry_programs": len(self._uninstall_cache),
            "total_program_files": len(program_files)
        }


# Instance globale
_detector_instance: Optional[WindowsPackageDetector] = None

def get_windows_detector() -> WindowsPackageDetector:
    """Retourne l'instance globale du détecteur Windows."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = WindowsPackageDetector()
    return _detector_instance