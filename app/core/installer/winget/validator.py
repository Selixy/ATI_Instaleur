"""
Validateur pour les packages et versions Winget.
Module: core.installer.winget.validator
"""

import re
from typing import List, Optional, Tuple


class WingetValidator:
    """Validateur spécialisé pour Winget."""
    
    def is_valid_package_name(self, package_name: str) -> bool:
        """
        Vérifie si un nom de package Winget est valide.
        
        Args:
            package_name: Nom du package à valider
            
        Returns:
            bool: True si le nom est valide
        """
        if not package_name or not isinstance(package_name, str):
            return False
        
        package_name = package_name.strip()
        
        # Un nom de package Winget ne doit pas être vide
        if not package_name:
            return False
        
        # Ne doit pas contenir certains caractères interdits
        forbidden_chars = ['<', '>', ':', '"', '|', '?', '*', '\n', '\r', '\t']
        if any(char in package_name for char in forbidden_chars):
            return False
        
        # Longueur raisonnable
        if len(package_name) > 200:
            return False
        
        return True
    
    def is_newer_version(self, available: str, installed: str) -> bool:
        """
        Compare deux versions pour déterminer si la première est plus récente.
        
        Args:
            available: Version disponible
            installed: Version installée
            
        Returns:
            bool: True si available > installed
        """
        if not available or not installed:
            return False
        
        try:
            available_parts = self._parse_version(available)
            installed_parts = self._parse_version(installed)
            
            if not available_parts or not installed_parts:
                return False
            
            # Normaliser la longueur des listes
            max_len = max(len(available_parts), len(installed_parts))
            available_parts.extend([0] * (max_len - len(available_parts)))
            installed_parts.extend([0] * (max_len - len(installed_parts)))
            
            return available_parts > installed_parts
            
        except (ValueError, AttributeError, TypeError):
            # En cas d'erreur, comparer les chaînes directement
            return available > installed
    
    def validate_version_format(self, version: str) -> bool:
        """
        Valide le format d'une version.
        
        Args:
            version: Version à valider
            
        Returns:
            bool: True si le format est valide
        """
        if not version or not isinstance(version, str):
            return False
        
        version = version.strip()
        
        # Patterns acceptés pour les versions
        version_patterns = [
            r'^\d+$',                           # 1
            r'^\d+\.\d+$',                      # 1.0
            r'^\d+\.\d+\.\d+$',                 # 1.0.0
            r'^\d+\.\d+\.\d+\.\d+$',            # 1.0.0.0
            r'^\d+\.\d+\.\d+-\w+$',             # 1.0.0-beta
            r'^\d+\.\d+\.\d+\.\d+-\w+$',        # 1.0.0.0-beta
            r'^\d+\.\d+-\w+$',                  # 1.0-beta
            r'^\d+-\w+$',                       # 1-beta
        ]
        
        return any(re.match(pattern, version) for pattern in version_patterns)
    
    def normalize_package_name(self, package_name: str) -> str:
        """
        Normalise un nom de package.
        
        Args:
            package_name: Nom du package à normaliser
            
        Returns:
            str: Nom normalisé
        """
        if not package_name:
            return ""
        
        # Supprimer les espaces en début/fin
        normalized = package_name.strip()
        
        # Remplacer les espaces multiples par un seul
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    def suggest_alternatives(self, package_name: str) -> List[str]:
        """
        Suggère des alternatives pour un nom de package.
        
        Args:
            package_name: Nom du package original
            
        Returns:
            List[str]: Liste des suggestions
        """
        if not package_name:
            return []
        
        suggestions = []
        name_lower = package_name.lower()
        
        # Suggestions basées sur des patterns courants
        common_mappings = {
            'chrome': ['Google.Chrome'],
            'firefox': ['Mozilla.Firefox'],
            'vscode': ['Microsoft.VisualStudioCode'],
            'visual studio code': ['Microsoft.VisualStudioCode'],
            'notepad++': ['Notepad++.Notepad++'],
            'notepad plus plus': ['Notepad++.Notepad++'],
            '7zip': ['7zip.7zip'],
            '7-zip': ['7zip.7zip'],
            'python': ['Python.Python.3', 'Python.Python.3.11'],
            'git': ['Git.Git'],
            'node': ['OpenJS.NodeJS'],
            'nodejs': ['OpenJS.NodeJS'],
            'docker': ['Docker.DockerDesktop'],
            'spotify': ['Spotify.Spotify'],
            'discord': ['Discord.Discord'],
            'zoom': ['Zoom.Zoom'],
            'teams': ['Microsoft.Teams'],
            'office': ['Microsoft.Office'],
        }
        
        # Chercher des correspondances exactes
        if name_lower in common_mappings:
            suggestions.extend(common_mappings[name_lower])
        
        # Chercher des correspondances partielles
        for key, values in common_mappings.items():
            if key in name_lower or name_lower in key:
                suggestions.extend(values)
        
        # Supprimer les doublons tout en préservant l'ordre
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in seen:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:5]  # Limiter à 5 suggestions
    
    def extract_publisher_and_name(self, full_package_name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extrait l'éditeur et le nom d'un package Winget complet.
        
        Args:
            full_package_name: Nom complet (ex: "Microsoft.VisualStudioCode")
            
        Returns:
            Tuple[str, str]: (publisher, name) ou (None, None) si échec
        """
        if not full_package_name or '.' not in full_package_name:
            return None, None
        
        parts = full_package_name.split('.', 1)
        if len(parts) != 2:
            return None, None
        
        publisher, name = parts
        
        # Valider que les parties ne sont pas vides
        if not publisher.strip() or not name.strip():
            return None, None
        
        return publisher.strip(), name.strip()
    
    def is_winget_id_format(self, package_name: str) -> bool:
        """
        Vérifie si un nom suit le format ID Winget (Publisher.PackageName).
        
        Args:
            package_name: Nom à vérifier
            
        Returns:
            bool: True si c'est un format d'ID Winget
        """
        if not package_name:
            return False
        
        publisher, name = self.extract_publisher_and_name(package_name)
        return publisher is not None and name is not None
    
    def _parse_version(self, version: str) -> Optional[List[int]]:
        """
        Parse une version en liste d'entiers.
        
        Args:
            version: Version à parser (ex: "1.2.3-beta")
            
        Returns:
            List[int] ou None: Parties numériques de la version
        """
        if not version:
            return None
        
        try:
            # Supprimer les suffixes (beta, alpha, etc.)
            clean_version = re.sub(r'-.*$', '', version)
            
            # Séparer par les points
            parts = clean_version.split('.')
            
            # Convertir en entiers
            return [int(part) for part in parts if part.isdigit()]
            
        except (ValueError, AttributeError):
            return None
    
    def validate_system_requirements(self) -> Tuple[bool, str]:
        """
        Valide que le système peut utiliser Winget.
        
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        import platform
        
        # Vérifier que c'est Windows
        if platform.system() != 'Windows':
            return False, "Winget n'est disponible que sur Windows"
        
        # Vérifier la version de Windows (Windows 10 1709+ ou Windows 11)
        try:
            version = platform.version()
            # Format typique: "10.0.19041" pour Windows 10 build 19041
            version_parts = version.split('.')
            
            if len(version_parts) >= 3:
                major = int(version_parts[0])
                minor = int(version_parts[1])
                build = int(version_parts[2])
                
                # Windows 11 (build 22000+) ou Windows 10 1709+ (build 16299+)
                if major >= 10:
                    if major > 10 or build >= 16299:
                        return True, "Système compatible avec Winget"
                    else:
                        return False, "Windows 10 version 1709 ou plus récente requis"
        
        except (ValueError, IndexError):
            pass
        
        # Si on ne peut pas déterminer la version, on assume que c'est OK
        return True, "Version Windows non déterminée, supposée compatible"