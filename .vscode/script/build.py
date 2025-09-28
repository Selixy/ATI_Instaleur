import shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "ATI_Instaleur.spec"
OUT = ROOT / "build"

def run(cmd):
    print("+", " ".join(map(str, cmd)))
    subprocess.check_call(cmd)

def check_resources():
    """Vérifie que les ressources critiques sont présentes avant le build."""
    print("Vérification des ressources...")
    
    # Configuration YAML - vérifier la structure multi-fichiers
    config_dir = ROOT / "app" / "config"

    if not config_dir.exists():
        print("❌ ERREUR: Répertoire de configuration non trouvé: app/config/")
        return False

    # Compter les fichiers YAML dans les sous-dossiers
    yaml_count = 0
    categories = []
    for category_dir in config_dir.iterdir():
        if category_dir.is_dir() and not category_dir.name.startswith('.'):
            yaml_files = list(category_dir.glob("*.yaml")) + list(category_dir.glob("*.yml"))
            if yaml_files:
                yaml_count += len(yaml_files)
                categories.append(f"{category_dir.name} ({len(yaml_files)} fichiers)")

    if yaml_count > 0:
        print(f"✓ Configuration YAML: {yaml_count} fichiers dans {len(categories)} catégories")
        for cat in categories:
            print(f"    - {cat}")
    else:
        print("❌ ERREUR: Aucun fichier YAML trouvé dans app/config/")
        return False
    
    critical_files = [
        (ROOT / "app" / "__main__.py", "Point d'entrée principal"),
        (SPEC, "Fichier .spec"),
    ]
    
    missing = []
    for file_path, description in critical_files:
        if file_path.exists():
            print(f"✓ {description}: {file_path}")
        else:
            print(f"❌ {description}: {file_path}")
            missing.append(description)
    
    # Vérifier les styles QSS
    style_dirs = [
        ROOT / "app" / "ui" / "styles",
        ROOT / "app" / "ui" / "update_styles",
    ]
    
    qss_count = 0
    for style_dir in style_dirs:
        if style_dir.exists():
            qss_files = list(style_dir.rglob("*.qss"))
            qss_count += len(qss_files)
            print(f"✓ Styles dans {style_dir.name}: {len(qss_files)} fichiers")
    
    if qss_count == 0:
        print("⚠️ Aucun fichier QSS trouvé")
    else:
        print(f"✓ Total fichiers QSS: {qss_count}")
    
    # Vérifier les icônes
    icons_dir = ROOT / "app" / "ui" / "icons"
    if icons_dir.exists():
        icon_files = [f for f in icons_dir.rglob("*.*") 
                     if f.suffix.lower() in ['.png', '.ico', '.svg', '.jpg']]
        print(f"✓ Icônes: {len(icon_files)} fichiers")
        
        # Vérifier l'icône principale
        app_icon = icons_dir / "app.ico"
        if app_icon.exists():
            print(f"✓ Icône principale: {app_icon}")
        else:
            print("⚠️ Icône principale app.ico manquante")
    
    if missing:
        print(f"\n❌ Fichiers critiques manquants: {', '.join(missing)}")
        return False
    
    print("✅ Toutes les ressources sont présentes")
    return True

def test_build(exe_dir):
    """Test rapide du build généré."""
    print(f"\nTest du build dans {exe_dir}...")
    
    # Vérifier l'exécutable
    exe_file = exe_dir / "ATI_Instaleur.exe"
    if not exe_file.exists():
        print("❌ Exécutable non trouvé!")
        return False
    
    print(f"✓ Exécutable: {exe_file}")
    
    # Vérifier les ressources dans le build
    resource_checks = [
        ("_internal", "Dossier des ressources PyInstaller"),
        ("_internal/config", "Configuration"),
    ]
    
    for resource_path, description in resource_checks:
        full_path = exe_dir / resource_path
        status = "✓" if full_path.exists() else "❌"
        print(f"{status} {description}: {full_path}")
    
    return True

def create_test_script(exe_dir):
    """Crée un script de test simple pour l'exécutable."""
    test_script = exe_dir / "test_app.py"
    
    test_content = '''#!/usr/bin/env python3
"""Script de test pour l'exécutable."""

import sys
from pathlib import Path

# Ajouter le dossier _internal au path si nécessaire
internal_path = Path(__file__).parent / "_internal"
if internal_path.exists():
    sys.path.insert(0, str(internal_path))

try:
    from core.YamlLoader import get_config_loader
    
    print("Test du chargement de configuration...")
    config = get_config_loader()
    apps = config.get_all_applications()
    
    print(f"✅ Configuration chargée: {len(apps)} applications")
    
    if apps:
        print("Premières applications:")
        for app in apps[:3]:
            print(f"  - {app.name}")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
'''
    
    with open(test_script, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"✓ Script de test créé: {test_script}")

def main():
    print("=== BUILD ATI_INSTALEUR ===")
    
    # 1. Vérification pré-build
    if not check_resources():
        print("\n❌ Arrêt du build - ressources manquantes")
        sys.exit(1)
    
    # 2. Nettoyage
    print(f"\nNettoyage du dossier de build...")
    if OUT.exists():
        shutil.rmtree(OUT)
        print("✓ Dossier de build nettoyé")
    
    # 3. Build PyInstaller
    print(f"\nLancement de PyInstaller...")
    distpath = OUT / "dist"
    workpath = OUT / "work"

    try:
        run([
            sys.executable, "-m", "PyInstaller",
            str(SPEC),
            "--distpath", str(distpath),
            "--workpath", str(workpath),
            "--clean",
            "--noconfirm"
        ])
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur PyInstaller: {e}")
        sys.exit(1)

    # 4. Nettoyage post-build
    root_exe = distpath / "ATI_Instaleur.exe"
    if root_exe.exists():
        root_exe.unlink()
        print("✓ Exécutable racine supprimé")

    # 5. Test du build
    exe_dir = distpath / "ATI_Instaleur"
    if exe_dir.exists():
        test_build(exe_dir)
        create_test_script(exe_dir)
        
        print(f"\n🎉 Build terminé avec succès!")
        print(f"📁 Dossier: {exe_dir}")
        print(f"🚀 Exécutable: {exe_dir / 'ATI_Instaleur.exe'}")
        print(f"🧪 Test: python {exe_dir / 'test_styles.py'}")
    else:
        print("❌ Dossier de build non trouvé")
        sys.exit(1)

if __name__ == "__main__":
    main()