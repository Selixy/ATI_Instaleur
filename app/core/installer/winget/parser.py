"""
Parser pour les sorties Winget.
Module: core.installer.winget.parser
"""

import re
from typing import Optional

from ..hook.status import InstallationResult, InstallationStatus, InstallationMethod
from ..hook.progress import ProgressEstimator


class WingetOutputParser:
    """Parser spécialisé pour les sorties Winget."""
    
    def __init__(self):
        self.progress_estimator = ProgressEstimator()
    
    def extract_installed_version(self, list_output: str, package_name: str) -> Optional[str]:
        """
        Extrait la version installée depuis la sortie de 'winget list'.
        
        Args:
            list_output: Sortie de la commande 'winget list'
            package_name: Nom du package recherché
            
        Returns:
            str ou None: Version installée ou None si non trouvée
        """
        lines = list_output.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            package_lower = package_name.lower()
            
            # Chercher une ligne contenant le nom du package
            if package_lower in line_lower:
                # Extraire les colonnes (typiquement: Name | Id | Version | Available | Source)
                parts = [part.strip() for part in line.split()]
                
                # Chercher un pattern de version dans les parties
                for part in parts:
                    if self._is_version_pattern(part):
                        return part
                
                # Si pas de pattern de version trouvé, essayer une approche différente
                # Parfois Winget formate les colonnes avec des espaces fixes
                version_match = re.search(r'\s+(\d+[\.\d\-\w]*)\s+', line)
                if version_match:
                    potential_version = version_match.group(1)
                    if self._is_version_pattern(potential_version):
                        return potential_version
        
        return None
    
    def extract_available_version(self, show_output: str) -> Optional[str]:
        """
        Extrait la version disponible depuis la sortie de 'winget show'.
        
        Args:
            show_output: Sortie de la commande 'winget show'
            
        Returns:
            str ou None: Version disponible ou None si non trouvée
        """
        lines = show_output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Chercher la ligne "Version:"
            if line.lower().startswith('version:'):
                version = line.split(':', 1)[1].strip()
                if version and self._is_version_pattern(version):
                    return version
            
            # Chercher d'autres patterns possibles
            version_patterns = [
                r'version\s*:\s*([^\s\n]+)',
                r'latest\s+version\s*:\s*([^\s\n]+)',
                r'current\s+version\s*:\s*([^\s\n]+)'
            ]
            
            for pattern in version_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    version = match.group(1)
                    if self._is_version_pattern(version):
                        return version
        
        return None
    
    def analyze_installation_result(self, return_code: int, output: str, 
                                  package_name: str, old_version: str = "") -> InstallationResult:
        """
        Analyse le résultat d'une installation Winget.
        
        Args:
            return_code: Code de retour du processus
            output: Sortie complète de la commande
            package_name: Nom du package installé
            old_version: Version précédente si applicable
            
        Returns:
            InstallationResult: Résultat analysé
        """
        output_lower = output.lower()
        
        # Installation réussie
        if return_code == 0:
            return self._analyze_success_output(output, output_lower, package_name, old_version)
        
        # Analyser les erreurs spécifiques
        return self._analyze_error_output(return_code, output, output_lower, package_name)
    
    def _analyze_success_output(self, output: str, output_lower: str, 
                               package_name: str, old_version: str) -> InstallationResult:
        """Analyse une sortie d'installation réussie."""
        
        # Vérifier si c'était déjà installé
        already_installed_indicators = [
            "already installed",
            "no applicable update found",
            "latest version already installed",
            "package already up to date"
        ]
        
        if any(indicator in output_lower for indicator in already_installed_indicators):
            return InstallationResult(
                status=InstallationStatus.ALREADY_INSTALLED,
                message=f"'{package_name}' était déjà installé",
                package_name=package_name,
                installed_version=old_version or "inconnue",
                raw_output=output
            )
        
        # Installation réussie
        new_version = self._extract_version_from_output(output)
        return InstallationResult(
            status=InstallationStatus.SUCCESS,
            message=f"Installation de '{package_name}' réussie",
            package_name=package_name,
            installed_version=new_version or "installée",
            raw_output=output
        )
    
    def _analyze_error_output(self, return_code: int, output: str, 
                             output_lower: str, package_name: str) -> InstallationResult:
        """Analyse une sortie d'erreur."""
        
        error_patterns = [
            # Package non trouvé
            (["not found", "no package found", "no packages were found"], 
             InstallationStatus.NOT_FOUND, f"Package '{package_name}' non trouvé"),
            
            # Permissions insuffisantes
            (["access denied", "administrator", "elevation required", "run as administrator"], 
             InstallationStatus.PERMISSION_DENIED, f"Permissions insuffisantes pour '{package_name}'"),
            
            # Erreurs réseau
            (["network", "connection", "timeout", "unreachable", "download failed"], 
             InstallationStatus.NETWORK_ERROR, f"Erreur réseau lors de l'installation de '{package_name}'"),
            
            # Installation corrompue
            (["corrupted", "hash", "checksum", "integrity", "verification failed"], 
             InstallationStatus.CORRUPTED_INSTALL, f"Installation corrompue pour '{package_name}'"),
        ]
        
        for keywords, status, message in error_patterns:
            if any(keyword in output_lower for keyword in keywords):
                return InstallationResult(
                    status=status,
                    message=message,
                    package_name=package_name,
                    raw_output=output,
                    return_code=return_code
                )
        
        # Erreur générique
        return InstallationResult(
            status=InstallationStatus.FAILED,
            message=f"Échec de l'installation de '{package_name}' (code: {return_code})",
            package_name=package_name,
            raw_output=output,
            return_code=return_code
        )
    
    def estimate_progress(self, line: str, line_count: int) -> int:
        """
        Estime la progression basée sur une ligne de sortie Winget.
        
        Args:
            line: Ligne de sortie
            line_count: Nombre de lignes traitées
            
        Returns:
            int: Progression estimée (0-100)
        """
        line_lower = line.lower()
        
        # Patterns spécifiques à Winget
        if any(word in line_lower for word in ['found', 'selecting', 'agreement']):
            return min(25 + line_count, 35)
        elif any(word in line_lower for word in ['downloading', 'download']):
            return min(35 + line_count * 3, 70)
        elif any(word in line_lower for word in ['installing', 'extracting']):
            return min(70 + line_count * 2, 95)
        elif any(word in line_lower for word in ['successfully', 'completed', 'finished']):
            return 100
        elif any(word in line_lower for word in ['failed', 'error']):
            return 100
        else:
            # Utiliser l'estimateur général
            return self.progress_estimator.estimate_from_keywords(line, line_count)
    
    def is_important_line(self, line: str) -> bool:
        """
        Détermine si une ligne doit être affichée dans les logs.
        
        Args:
            line: Ligne à analyser
            
        Returns:
            bool: True si la ligne est importante
        """
        line_lower = line.lower()
        
        # Lignes importantes à montrer
        important_keywords = [
            'found', 'downloading', 'installing', 'successfully', 'completed',
            'error', 'failed', 'warning', 'already installed', 'not found',
            'agreement', 'license', 'extracting', 'configuring'
        ]
        
        # Lignes à ignorer (trop verbeuses)
        ignore_keywords = [
            'progress:', 'bytes', ' kb/s', ' mb/s', '█', '▓', '░',
            'please wait', 'processing'
        ]
        
        # Ignorer les lignes trop verbeuses
        if any(ignore in line_lower for ignore in ignore_keywords):
            return False
        
        # Ignorer les lignes trop longues (probablement du spam)
        if len(line) > 150:
            return False
        
        # Afficher les lignes importantes
        if any(important in line_lower for important in important_keywords):
            return True
        
        # Afficher les lignes courtes qui peuvent contenir des infos utiles
        return len(line.strip()) < 80 and len(line.strip()) > 5
    
    def _extract_version_from_output(self, output: str) -> Optional[str]:
        """Extrait une version depuis la sortie d'installation."""
        version_patterns = [
            r'version\s+(\d+[\.\d\-\w]*)',
            r'v(\d+[\.\d\-\w]*)',
            r'(\d+\.\d+[\.\d\-\w]*)',
            r'installed\s+(\d+[\.\d\-\w]*)'
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                version = match.group(1)
                if self._is_version_pattern(version):
                    return version
        
        return None
    
    def _is_version_pattern(self, text: str) -> bool:
        """
        Vérifie si un texte ressemble à un numéro de version.
        
        Args:
            text: Texte à vérifier
            
        Returns:
            bool: True si c'est probablement une version
        """
        if not text or len(text) < 1:
            return False
        
        # Pattern pour version (ex: 1.0, 2.5.1, 3.0.0-beta, etc.)
        version_pattern = r'^\d+(\.\d+)*(-[\w\d]+)*$'
        return bool(re.match(version_pattern, text))