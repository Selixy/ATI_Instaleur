# -*- mode: python ; coding: utf-8 -*-
"""
Fichier de build PyInstaller pour ATI_Instaleur
Version corrigée pour inclure correctement les styles QSS
"""

import sys
from pathlib import Path

# Configuration des chemins
PROJECT_ROOT = Path(".")
APP_DIR = PROJECT_ROOT / "app"
CONFIG_DIR = PROJECT_ROOT / "config"

def collect_app_data():
    """Collecte tous les fichiers de données de l'application."""
    datas = []
    
    # 1. Configuration YAML multi-fichiers (CRITIQUE)
    config_dir = APP_DIR / "config"

    if not config_dir.exists():
        print("❌ ERREUR: Répertoire de configuration non trouvé: app/config/")
        sys.exit(1)

    yaml_count = 0
    for category_dir in config_dir.iterdir():
        if category_dir.is_dir() and not category_dir.name.startswith('.'):
            for yaml_file in category_dir.glob("*.yaml"):
                rel_path = yaml_file.relative_to(APP_DIR)
                datas.append((str(yaml_file), str(rel_path.parent)))
                yaml_count += 1
            for yml_file in category_dir.glob("*.yml"):
                rel_path = yml_file.relative_to(APP_DIR)
                datas.append((str(yml_file), str(rel_path.parent)))
                yaml_count += 1

    if yaml_count > 0:
        print(f"✓ Configuration YAML: {yaml_count} fichiers inclus")
    else:
        print("❌ ERREUR: Aucun fichier YAML trouvé dans app/config/")
        sys.exit(1)
    
    # 2. Styles QSS - CORRECTION IMPORTANTE
    style_directories = [
        (APP_DIR / "ui" / "styles", "ui/styles"),
        (APP_DIR / "ui" / "update_styles", "ui/update_styles"),
    ]
    
    total_qss_files = 0
    for source_dir, target_dir in style_directories:
        if source_dir.exists():
            qss_files = list(source_dir.rglob("*.qss"))
            for qss_file in qss_files:
                # Calculer le chemin relatif depuis source_dir pour préserver la structure
                rel_path = qss_file.relative_to(source_dir)
                target_path = target_dir
                if rel_path.parent.name:  # S'il y a un sous-dossier
                    target_path = f"{target_dir}/{rel_path.parent}"
                
                datas.append((str(qss_file), target_path))
                print(f"✓ Style: {qss_file} -> {target_path}")
                total_qss_files += 1
    
    print(f"✓ Total styles QSS: {total_qss_files} fichiers")
    
    # 3. Icônes
    icons_dir = APP_DIR / "ui" / "icons"
    icon_count = 0
    if icons_dir.exists():
        for icon_file in icons_dir.rglob("*.*"):
            if icon_file.suffix.lower() in ['.png', '.ico', '.svg', '.jpg', '.jpeg']:
                rel_path = icon_file.relative_to(APP_DIR)
                datas.append((str(icon_file), str(rel_path.parent)))
                icon_count += 1
        print(f"✓ Icônes: {icon_count} fichiers")
    
    return datas

def get_hidden_imports():
    """Retourne la liste des imports cachés nécessaires."""
    return [
        # PySide6 essentials
        'PySide6.QtCore',
        'PySide6.QtWidgets', 
        'PySide6.QtGui',
        
        # Modules core
        'core.installer.hook.status',
        'core.installer.hook.progress',
        'core.installer.hook.base_installer',
        'core.installer.winget.installer',
        'core.installer.main_installer',
        'core.YamlLoader',

        # Utilitaires
        'utils.resource_manager',
        
        # UI modules - AJOUT IMPORTANT
        'ui.update_styles.style_finder',
        'ui.update_styles.style_loader',
        'ui.threads.installer_thread',
        
        # Système Windows pour la détection de thème
        'winreg',
        
        # PyYAML
        'yaml',
        
        # QFramelessWindow si utilisé
        'qframelesswindow',
        'qframelesswindow.windows',
    ]

def get_excludes():
    """Modules à exclure du build."""
    return [
        # Plateformes non Windows
        'qframelesswindow.mac', 
        'qframelesswindow.linux',
        
        # Modules dev/test
        'pytest',
        'unittest',
        'doctest',
        
        # Modules lourds non utilisés
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
    ]

# Collecte des données
datas = collect_app_data()

# Icône de l'application
app_icon = APP_DIR / "ui" / "icons" / "app.ico"
icon_path = str(app_icon) if app_icon.exists() else None
if not icon_path:
    print("⚠️ app.ico non trouvé, pas d'icône pour l'exécutable")

# Configuration Analysis
a = Analysis(
    ['app/__main__.py'],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=get_hidden_imports(),
    hookspath=[],
    runtime_hooks=[],
    excludes=get_excludes(),
    noarchive=False,
    optimize=0,
)

# Suppression des duplicatas
a.binaries = [x for x in a.binaries if not x[0].startswith('api-')]

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ATI_Instaleur',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Interface graphique
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ATI_Instaleur'
)
