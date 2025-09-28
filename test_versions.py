"""
Test des versions multiples dans le config loader.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.core.config_loader import ConfigurationLoader

    def test_versions_functionality():
        """Test de la fonctionnalité des versions multiples."""
        print("Test de la fonctionnalité des versions multiples")
        print("=" * 50)

        # Charger la configuration
        config_loader = ConfigurationLoader()

        print(f"Applications chargées: {len(config_loader.applications)}")
        print()

        # Trouver les applications avec versions
        apps_with_versions = [app for app in config_loader.applications if app.has_versions]

        print(f"Applications avec versions multiples: {len(apps_with_versions)}")
        print()

        for app in apps_with_versions:
            print(f"📦 {app.name}")
            print(f"   Description: {app.description}")
            print(f"   Catégorie: {app.category}")
            print(f"   Nombre de versions: {len(app.versions)}")

            for i, version in enumerate(app.versions):
                print(f"   Version {i+1}: {version.name} (v{version.version})")
                print(f"      Méthodes: {len(version.methods)}")
                for method in version.methods:
                    print(f"        - {method.type}: {method.url[:50]}...")
            print()

        # Test d'une application normale (sans versions)
        apps_without_versions = [app for app in config_loader.applications if not app.has_versions]
        print(f"Applications classiques (sans versions): {len(apps_without_versions)}")

        if apps_without_versions:
            app = apps_without_versions[0]
            print(f"Exemple: {app.name}")
            print(f"   Méthodes: {len(app.methods)}")
            for method in app.methods:
                print(f"   - {method.type}: {method.url[:50]}...")

        print("\nTest terminé avec succès!")

    if __name__ == "__main__":
        test_versions_functionality()

except Exception as e:
    print(f"Erreur: {e}")
    import traceback
    traceback.print_exc()