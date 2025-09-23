from typing import Optional
from .style_loader import StyleLoader

_style_loader: Optional[StyleLoader] = None

def get_style_loader(debug: bool = True, mode: Optional[str] = None) -> StyleLoader:
    global _style_loader
    if _style_loader is None or (mode and mode != _style_loader.finder.mode):
        _style_loader = StyleLoader(debug=debug, mode=mode)
    return _style_loader

def update_styles(app, qss_filename: str = "base.qss", mode: Optional[str] = None, debug: bool = True) -> bool:
    loader = get_style_loader(debug=debug, mode=mode)
    return loader.apply_style_to_app(app, qss_filename)

def clear_style_cache():
    loader = get_style_loader()
    loader.clear_cache()
