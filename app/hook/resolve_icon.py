# app/utils/resolve_icon.py
from pathlib import Path
import sys
from typing import Optional
from .environment import is_frozen, get_project_root

def resolve_icon(icon_name: str) -> Optional[str]:
    """Résout le chemin absolu d'une icône donnée."""
    candidates = []

    # 1. Cas exécutable gelé (PyInstaller)
    if is_frozen():
        meipass = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        candidates.extend([
            meipass / "ui" / "icons" / icon_name,
            Path(sys.executable).parent / "ui" / "icons" / icon_name
        ])

    # 2. Cas développement
    project_root = get_project_root()
    candidates.append(project_root / "app" / "ui" / "icons" / icon_name)

    # 3. Chemin absolu direct
    candidates.append(Path("./app/ui/icons") / icon_name)

    # Debug
    print(f"\nSearching for icon '{icon_name}' in:")
    for path in candidates:
        print(f"  - {path}")
        if path.exists():
            print(f"  OK Found at: {path}")
            return str(path)

    print(f"  ERROR Icon not found: {icon_name}")
    return None
