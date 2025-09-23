#!/usr/bin/env python3
"""
Test spécialisé pour les styles après build PyInstaller.
Utiliser ce script DEPUIS le dossier de l'exécutable construit.
"""

import sys
from pathlib import Path

def test_pyinstaller_environment():
    """Test de l'environnement PyInstaller."""
    print("=== ENVIRONNEMENT PYINSTALLER ===")
    
    # Détection du mode PyInstaller
    is_frozen = getattr(sys, 'frozen', False)
    print(f"Mode PyInstaller: {is_frozen}")
    
    if is_frozen:
        print(f"Exécutable: {sys.executable}")
        if hasattr(sys, "_MEIPASS"):
            print(f"MEIPASS: {sys._MEIPASS}")
    
    # Chemin du script
    script_dir = Path(__file__).parent
    print(f"Dossier script: {script_dir}")
    
    # Chercher _internal
    internal_dir = script_dir / "_internal"
    if internal_dir.exists():
        print(f"✓ Dossier _internal trouvé: {internal_dir}")
        
        # Lister le contenu d'_internal
        ui_dir = internal_dir / "ui"
        if ui_dir.exists():
            print(f"✓ Dossier ui trouvé: {ui_dir}")
            
            # Styles
            styles_paths = [
                ui_dir / "styles",
                ui_dir / "update_styles"
            ]
            
            for style_path in styles_paths:
                if style_path.exists():
                    qss_files = list(style_path.rglob("*.qss"))
                    print(f"✓ {style_path.name}: {len(qss_files)} fichiers QSS")
                    for qss in qss_files[:3]:  # Afficher les 3 premiers
                        print(f"    - {qss.name}")
                else:
                    print(f"❌ {style_path} non trouvé")
    else:
        print("❌ Dossier _internal non trouvé")

def test_imports():
    """Test des imports des modules de styles."""
    print("\n=== TEST IMPORTS ===")
    
    # Ajouter _internal au path
    internal_path = Path(__file__).parent / "_internal"
    if internal_path.exists():
        sys.path.insert(0, str(internal_path))
        print(f"✓ {internal_path} ajouté au sys.path")
    
    try:
        print("Import ui.update_styles...")
        from ui.update_styles import get_style_loader
        print("✓ Import ui.update_styles réussi")
        
        print("Création du StyleLoader...")
        loader = get_style_loader(debug=True)
        print("✓ StyleLoader créé")
        
        return loader
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_style_loading(loader):
    """Test du chargement des styles."""
    if not loader:
        print("\n❌ Pas de loader disponible pour les tests")
        return
    
    print("\n=== TEST CHARGEMENT STYLES ===")
    
    # Debug des chemins
    loader.finder.debug_paths()
    
    # Test de chargement de base.qss
    print("\nTest chargement base.qss...")
    content = loader.load_qss_content("base.qss")
    
    if content:
        print(f"✓ Style base.qss chargé: {len(content)} caractères")
        
        # Extraire les premières lignes pour vérification
        lines = content.split('\n')[:5]
        print("Aperçu du contenu:")
        for line in lines:
            if line.strip():
                print(f"  {line[:60]}...")
    else:
        print("❌ Impossible de charger base.qss")
    
    # Test des modes disponibles
    available_modes = loader.get_available_modes()
    print(f"\nModes disponibles: {available_modes}")
    
    # Cache info
    cache_info = loader.get_cache_info()
    print(f"Cache info: {cache_info}")

def test_theme_detection():
    """Test de détection du thème système."""
    print("\n=== TEST DÉTECTION THÈME ===")
    
    try:
        from ui.update_styles.style_finder import StyleFinder
        
        finder = StyleFinder(debug=True)
        print(f"Mode système détecté: {finder.mode}")
        
        # Test refresh du mode
        new_mode = finder.refresh_mode()
        print(f"Mode après refresh: {new_mode}")
        
    except Exception as e:
        print(f"❌ Erreur détection thème: {e}")

def main():
    """Fonction principale de test."""
    print("TEST DES STYLES - BUILD PYINSTALLER")
    print("=" * 50)
    
    # Tests séquentiels
    test_pyinstaller_environment()
    loader = test_imports()
    test_style_loading(loader)
    test_theme_detection()
    
    print("\n" + "=" * 50)
    print("Tests terminés!")
    
    if loader:
        print("✅ Le système de styles semble fonctionnel")
    else:
        print("❌ Problèmes détectés dans le système de styles")

if __name__ == "__main__":
    main()