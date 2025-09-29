# app/config/title_bar_buttons.py
from typing import Dict, List, Any
from .hook import resolve_buttons_config

ButtonConfig = Dict[str, Any]

_BASE_BUTTONS_CONFIG: List[ButtonConfig] = [
    {
        "text": "",
        "icon": "home.png",
        "action": "on_custom_path_click",
        "tooltip": "Configurer le chemin d'installation personnalisé",
        "tag": "home",
        "clickable": True
    },
]

TITLE_BAR_BUTTONS = resolve_buttons_config(_BASE_BUTTONS_CONFIG)