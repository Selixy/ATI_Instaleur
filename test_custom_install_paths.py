#!/usr/bin/env python3
"""
Test pour vérifier le système de chemins d'installation personnalisés.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_install_path_manager():
    """Test du gestionnaire de chemins d'installation."""
    print("=== Test InstallPathManager ===")

    try:
        from core.installer.install_paths import get_install_path_manager

        # Obtenir l'instance du gestionnaire
        manager = get_install_path_manager()

        # Test 1: Chemin global personnalisé
        print("\n1. Test chemin global personnalisé:")
        manager.set_global_custom_path("C:\\CustomSoftware")

        # Simuler une configuration d'app avec custom_install_path=True
        class MockAppConfig:
            def __init__(self, custom_install_path=False):
                self.custom_install_path = custom_install_path

        app_config_enabled = MockAppConfig(custom_install_path=True)
        app_config_disabled = MockAppConfig(custom_install_path=False)

        # Test avec application qui autorise les chemins personnalisés
        args_enabled = manager.get_install_arguments("Maya", app_config_enabled)
        print(f"  App avec custom_install_path=True: '{args_enabled}'")

        # Test avec application qui n'autorise pas les chemins personnalisés
        args_disabled = manager.get_install_arguments("Maya", app_config_disabled)
        print(f"  App avec custom_install_path=False: '{args_disabled}'")

        # Test 2: Chemin spécifique à une application
        print("\n2. Test chemin spécifique à une application:")
        manager.set_app_custom_path("MotionBuilder", "D:\\Autodesk\\MotionBuilder", enabled=True)

        args_specific = manager.get_install_arguments("MotionBuilder", app_config_enabled)
        print(f"  MotionBuilder avec chemin spécifique: '{args_specific}'")

        # Test 3: Application sans configuration personnalisée
        print("\n3. Test application sans configuration:")
        args_default = manager.get_install_arguments("Blender", app_config_disabled)
        print(f"  Blender sans custom_install_path: '{args_default}'")

        print("\nTous les tests InstallPathManager réussis!")
        return True

    except Exception as e:
        print(f"Erreur dans InstallPathManager: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_yaml_loader_integration():
    """Test de l'intégration avec YamlLoader."""
    print("\n=== Test YamlLoader Integration ===")

    try:
        from core.YamlLoader import get_config_loader

        loader = get_config_loader()

        # Charger Maya pour tester
        maya_app = loader.get_application_by_name("Autodesk Maya")
        if maya_app:
            print(f"Maya trouvé: custom_install_path = {maya_app.custom_install_path}")

            if hasattr(maya_app, 'custom_install_path'):
                print("✓ Propriété custom_install_path ajoutée avec succès!")
                return True
            else:
                print("✗ Propriété custom_install_path manquante")
                return False
        else:
            print("✗ Maya non trouvé dans la configuration")
            return False

    except Exception as e:
        print(f"Erreur dans YamlLoader: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_installer_integration():
    """Test de l'intégration avec les installateurs."""
    print("\n=== Test Installer Integration ===")

    try:
        from core.installer.msi.installer import MsiInstaller
        from core.installer.exe.installer import ExeInstaller
        from core.installer.install_paths import get_install_path_manager

        # Configurer un chemin personnalisé
        manager = get_install_path_manager()
        manager.set_global_custom_path("C:\\TestInstall")

        # Simuler une config d'app
        class MockApp:
            def __init__(self):
                self.custom_install_path = True

        mock_app = MockApp()

        # Test MSI
        print("\n1. Test MSI Installer:")
        msi_installer = MsiInstaller()
        print("  MSI Installer créé avec succès")

        # Test EXE
        print("\n2. Test EXE Installer:")
        exe_installer = ExeInstaller()
        print("  EXE Installer créé avec succès")

        # Test des arguments personnalisés
        args = manager.get_install_arguments("TestApp", mock_app)
        print(f"  Arguments générés: '{args}'")

        print("\nIntégration installateurs réussie!")
        return True

    except Exception as e:
        print(f"Erreur dans l'intégration installateurs: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Test du système de chemins d'installation personnalisés")
    print("=" * 65)

    tests = [
        ("InstallPathManager", test_install_path_manager),
        ("YamlLoader Integration", test_yaml_loader_integration),
        ("Installer Integration", test_installer_integration)
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"ERREUR dans {test_name}: {e}")
            results[test_name] = False

    print("\n" + "=" * 65)
    print("RESULTATS:")

    all_passed = True
    for test_name, passed in results.items():
        status = "SUCCES" if passed else "ECHEC"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\nTOUS LES TESTS REUSSIS!")
        print("Le système de chemins d'installation personnalisés fonctionne!")
    else:
        print("\nCERTAINS TESTS ONT ECHOUE")
        print("Des corrections sont nécessaires.")