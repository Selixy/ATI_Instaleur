"""
Classes et fonctions pour la gestion de la progression d'installation.
Module: core.installer.hook.progress
"""

from dataclasses import dataclass
from typing import Callable, Optional
from datetime import datetime

from .status import InstallationStatus


@dataclass
class ProgressInfo:
    """Informations de progression d'une installation."""
    current_progress: int = 0         # Progression actuelle (0-100)
    global_progress: int = 0          # Progression globale (0-100)
    message: str = ""                 # Message de log
    package_name: str = ""            # Nom du package en cours
    current_step: str = ""            # Étape actuelle
    status: InstallationStatus = InstallationStatus.NOT_STARTED
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    @property
    def formatted_message(self) -> str:
        """Message formaté avec timestamp."""
        time_str = self.timestamp.strftime("%H:%M:%S")
        return f"[{time_str}] {self.message}"


class ProgressTracker:
    """Gestionnaire de progression pour les installations."""
    
    def __init__(self):
        self.callback: Optional[Callable[[ProgressInfo], None]] = None
        self.is_cancelled = False
        self.current_package = ""
        self.total_packages = 0
        self.completed_packages = 0
        
    def set_callback(self, callback: Callable[[ProgressInfo], None]) -> None:
        """Définit le callback de progression."""
        self.callback = callback
    
    def cancel(self) -> None:
        """Marque la progression comme annulée."""
        self.is_cancelled = True
    
    def reset(self, total_packages: int = 1) -> None:
        """Remet à zéro le tracker."""
        self.is_cancelled = False
        self.total_packages = total_packages
        self.completed_packages = 0
        self.current_package = ""
    
    def start_package(self, package_name: str) -> None:
        """Démarre le suivi d'un nouveau package."""
        self.current_package = package_name
    
    def complete_package(self) -> None:
        """Marque le package actuel comme terminé."""
        self.completed_packages += 1
    
    def emit_progress(self, 
                     current_progress: int, 
                     message: str = "",
                     step: str = "",
                     status: InstallationStatus = InstallationStatus.IN_PROGRESS) -> None:
        """
        Émet un signal de progression.
        
        Args:
            current_progress: Progression du package actuel (0-100)
            message: Message de log (optionnel)
            step: Étape actuelle (optionnel)
            status: Statut de l'installation
        """
        if not self.callback:
            return
        
        # Calculer la progression globale
        if self.total_packages > 0:
            package_contribution = (self.completed_packages / self.total_packages) * 100
            current_contribution = (current_progress / 100) * (100 / self.total_packages)
            global_progress = min(int(package_contribution + current_contribution), 100)
        else:
            global_progress = current_progress
        
        progress_info = ProgressInfo(
            current_progress=current_progress,
            global_progress=global_progress,
            message=message,
            package_name=self.current_package,
            current_step=step,
            status=status
        )
        
        self.callback(progress_info)
    
    def emit_message(self, message: str, status: InstallationStatus = InstallationStatus.IN_PROGRESS) -> None:
        """Émet un message sans changer la progression."""
        if not self.callback:
            return
        
        progress_info = ProgressInfo(
            message=message,
            package_name=self.current_package,
            status=status
        )
        
        self.callback(progress_info)


class ProgressEstimator:
    """Estimateur de progression basé sur les sorties textuelles."""
    
    @staticmethod
    def estimate_from_keywords(text: str, line_count: int = 0) -> int:
        """
        Estime la progression basée sur des mots-clés dans le texte.
        
        Args:
            text: Texte à analyser
            line_count: Nombre de lignes traitées
            
        Returns:
            int: Progression estimée (0-100)
        """
        text_lower = text.lower()
        
        # Phases communes d'installation
        if any(word in text_lower for word in ['checking', 'verifying', 'found']):
            return min(20 + line_count, 30)
        elif any(word in text_lower for word in ['downloading', 'download', 'fetching']):
            return min(30 + line_count * 2, 60)
        elif any(word in text_lower for word in ['installing', 'extracting', 'copying']):
            return min(60 + line_count * 2, 90)
        elif any(word in text_lower for word in ['configuring', 'finalizing']):
            return min(85 + line_count, 95)
        elif any(word in text_lower for word in ['completed', 'success', 'installed']):
            return 100
        elif any(word in text_lower for word in ['failed', 'error']):
            return 100
        else:
            # Progression basée sur le nombre de lignes
            return min(10 + line_count, 80)
    
    @staticmethod
    def parse_percentage(text: str) -> Optional[int]:
        """
        Extrait un pourcentage depuis le texte si présent.
        
        Args:
            text: Texte à analyser
            
        Returns:
            int ou None: Pourcentage trouvé ou None
        """
        import re
        
        # Rechercher des patterns comme "45%", "Progress: 67%"
        patterns = [
            r'(\d{1,3})%',
            r'progress:?\s*(\d{1,3})%',
            r'completed:?\s*(\d{1,3})%'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                percentage = int(match.group(1))
                if 0 <= percentage <= 100:
                    return percentage
        
        return None