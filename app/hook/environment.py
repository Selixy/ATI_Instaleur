# app/hook/environment.py
import sys
from pathlib import Path
from typing import Optional

def is_frozen():
    """Vérifie si l'application est exécutée en mode gelé (PyInstaller)."""
    return getattr(sys, 'frozen', False)

def get_project_root() -> Path:
    """Retourne le chemin de la racine du projet."""
    if is_frozen():
        return Path(sys.executable).parent
    else:
        return Path(__file__).resolve().parent.parent.parent.parent

def setup_environment():
    """Configure l'environnement Python pour les imports."""
    project_root = get_project_root()
    sys.path.append(str(project_root))

    # Optionnel : affiche les chemins pour le débogage
    if not is_frozen():
        print(f"Project root: {project_root}")
        print("sys.path:", sys.path)
