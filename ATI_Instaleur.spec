# ATI_Instaleur.spec
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# ne pas utilisez le chemin absolu du projet
root = Path(".")

# Collecte des fichiers
datas = []

# Collecte du fichier de configuration YAML
config_file = root / "config" / "config.yaml"
if config_file.exists():
    datas.append((str(config_file), "config"))
    print(f"Configuration trouvée: {config_file}")
else:
    # Chercher dans d'autres emplacements possibles
    alternative_configs = [
        root / "config.yaml",
        root / "app" / "config" / "config.yaml",
        root / "app" / "config.yaml"
    ]
    
    for alt_config in alternative_configs:
        if alt_config.exists():
            datas.append((str(alt_config), "config"))
            print(f"Configuration trouvée: {alt_config}")
            break
    else:
        print("WARNING: Aucun fichier config.yaml trouvé!")

# Collecte des fichiers QSS
styles_dir = root / "app" / "ui" / "styles"
if styles_dir.exists() and styles_dir.is_dir():
    for qss_file in styles_dir.glob("*.qss"):
        datas.append((str(qss_file), "ui/styles"))
    print(f"QSS trouvés: {len([p for p in styles_dir.glob('*.qss')])}")

# Collecte des icônes
icons_dir = root / "app" / "ui" / "icons"
if icons_dir.exists() and icons_dir.is_dir():
    for ico_file in icons_dir.glob("*.*"):
        datas.append((str(ico_file), "ui/icons"))
    print(f"Icônes trouvées: {len([p for p in icons_dir.glob('*.*')])}")

# Debug: Afficher tous les fichiers qui seront inclus
print("\nFichiers de données qui seront inclus:")
for src, dst in datas:
    print(f"  {src} -> {dst}")

# Icône principale
app_icon = root / "app" / "ui" / "icons" / "app.ico"
icon_path = str(app_icon) if app_icon.exists() else None

a = Analysis(
    ['app/__main__.py'],
    pathex=[str(root)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'qframelesswindow',
        'qframelesswindow.windows',
        'core.actions.title_bar_menu_action',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['qframelesswindow.mac', 'qframelesswindow.linux'],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    name='ATI_Instaleur',
    icon=icon_path,
    console=False,  # <-- Changez cette ligne de True à False
    disable_windowed_traceback=False,
)

coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, name='ATI_Instaleur')