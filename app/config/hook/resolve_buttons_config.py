from typing import Dict, List, Any
from hook import resolve_icon

ButtonConfig = Dict[str, Any]

def resolve_buttons_config(buttons_config: List[ButtonConfig]) -> List[ButtonConfig]:
    """Résout les chemins des icônes pour chaque bouton."""
    resolved_config = []
    for button in buttons_config:
        resolved_button = button.copy()
        if "icon" in resolved_button:
            resolved_icon_path = resolve_icon(resolved_button["icon"])
            if resolved_icon_path:
                resolved_button["icon"] = resolved_icon_path
            else:
                print(f"Warning: Icon not found: {resolved_button['icon']}")
        resolved_config.append(resolved_button)
    return resolved_config
