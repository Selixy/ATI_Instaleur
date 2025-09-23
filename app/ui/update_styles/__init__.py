"""
Module de gestion des styles QSS avec support PyInstaller.
Système de thèmes avec variables et détection automatique du mode système.
"""

from typing import Optional
from .style_loader import StyleLoader

_style_loader: Optional[StyleLoader] = None

def get_style_loader(debug: bool = True, mode: Optional[str] = None) -> StyleLoader:
    """
    Retourne l'instance globale du chargeur de styles.
    
    Args:
        debug: Active les messages de debug
        mode: Force un mode couleur ("light", "dark") ou None pour auto-détection
        
    Returns:
        StyleLoader: Instance du chargeur de styles
    """
    global _style_loader
    if _style_loader is None or (mode and mode != _style_loader.finder.mode):
        _style_loader = StyleLoader(debug=debug, mode=mode)
    return _style_loader

def update_styles(app, qss_filename: str = "base.qss", mode: Optional[str] = None, debug: bool = True) -> bool:
    """
    Applique un style QSS à l'application avec support des variables et thèmes.
    
    Args:
        app: Instance de l'application Qt
        qss_filename: Nom du fichier QSS de base
        mode: Mode couleur forcé ou None pour auto-détection
        debug: Active les messages de debug
        
    Returns:
        bool: True si le style a été appliqué avec succès
    """
    loader = get_style_loader(debug=debug, mode=mode)
    return loader.apply_style_to_app(app, qss_filename)

def clear_style_cache():
    """Vide le cache des styles chargés."""
    loader = get_style_loader()
    loader.clear_cache()

def reload_styles(app, qss_filename: str = "base.qss", debug: bool = True) -> bool:
    """
    Recharge et applique les styles en vidant d'abord le cache.
    
    Args:
        app: Instance de l'application Qt
        qss_filename: Nom du fichier QSS de base  
        debug: Active les messages de debug
        
    Returns:
        bool: True si le style a été rechargé et appliqué avec succès
    """
    clear_style_cache()
    return update_styles(app, qss_filename, debug=debug)

def get_current_mode() -> str:
    """
    Retourne le mode couleur actuel détecté.
    
    Returns:
        str: "light" ou "dark"
    """
    loader = get_style_loader()
    return loader.finder.mode

def set_mode(app, mode: str, qss_filename: str = "base.qss", debug: bool = True) -> bool:
    """
    Force un mode couleur et applique les styles correspondants.
    
    Args:
        app: Instance de l'application Qt
        mode: Mode couleur ("light" ou "dark")
        qss_filename: Nom du fichier QSS de base
        debug: Active les messages de debug
        
    Returns:
        bool: True si le mode a été changé et appliqué avec succès
    """
    global _style_loader
    _style_loader = None  # Force la recréation avec le nouveau mode
    return update_styles(app, qss_filename, mode=mode, debug=debug)