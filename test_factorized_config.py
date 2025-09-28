"""
Test de la configuration factorisée par éditeur/catégorie.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_factorized_structure():
    """Test de la structure factorisée."""
    print("Test de la configuration factorisée")
    print("=" * 50)

    try:
        from app.core.config_loader_factorized import FactorizedConfigurationLoader

        # Charger la configuration factorisée
        loader = FactorizedConfigurationLoader()

        print(f"Applications chargées: {len(loader.applications)}")
        print(f"Éditeurs: {len(loader.editors)}")
        print(f"Catégories générales: {len(loader.categories)}")
        print()

        # Test groupement par éditeur
        print("=== GROUPEMENT PAR ÉDITEUR ===")
        apps_by_editor = loader.get_applications_grouped_by_editor()

        for editor_name, apps in apps_by_editor.items():
            print(f"\n📁 {editor_name} ({len(apps)} applications):")
            for app in apps:
                versions_info = ""
                if app.has_versions:
                    default_version = app.get_default_version()
                    default_name = default_version.name if default_version else "N/A"
                    versions_info = f" | {len(app.versions)} versions | Défaut: {default_name}"

                print(f"  - {app.name} ({app.category}){versions_info}")

        # Test groupement par catégorie
        print("\n=== GROUPEMENT PAR CATÉGORIE ===")
        apps_by_category = loader.get_applications_grouped_by_category()

        for category_name, apps in apps_by_category.items():
            print(f"\n📂 {category_name} ({len(apps)} applications):")
            for app in apps:
                editor_info = f" [{app.editor}]" if app.editor else " [Indépendant]"
                print(f"  - {app.name}{editor_info}")

        # Test des variables template
        print("\n=== TEST DES VARIABLES TEMPLATE ===")

        # Rechercher Maya pour tester les URLs résolues
        maya_app = loader.get_application_by_name("Maya")
        if maya_app and maya_app.has_versions:
            print(f"\nMaya - Variables template résolues:")
            for version in maya_app.versions:
                print(f"  Version {version.name}:")
                for method in version.methods:
                    url_preview = method.url[:80] + "..." if len(method.url) > 80 else method.url
                    print(f"    URL: {url_preview}")
                    print(f"    Args: {method.extra_args.get('silent_args', 'N/A')}")

        # Test des applications Adobe/Foundry
        print("\n=== APPLICATIONS AVEC BASE_URL ===")
        for app in loader.applications:
            if app.editor in ["Adobe", "The Foundry"]:
                print(f"{app.name} ({app.editor}):")
                for method in app.methods:
                    print(f"  URL: {method.url}")

        print("\n=== STATISTIQUES ===")
        total_apps = len(loader.applications)
        apps_with_versions = len([app for app in loader.applications if app.has_versions])
        apps_by_editor_count = {editor: len(apps) for editor, apps in apps_by_editor.items()}

        print(f"Total applications: {total_apps}")
        print(f"Applications avec versions: {apps_with_versions}")
        print(f"Répartition par éditeur: {apps_by_editor_count}")

        # Test de compatibilité avec l'ancien système
        print("\n=== COMPATIBILITÉ ANCIEN SYSTÈME ===")
        vscode_app = loader.get_application_by_name("Visual Studio Code")
        if vscode_app:
            print(f"VS Code trouvé: {vscode_app.name}")
            print(f"Catégorie: {vscode_app.category}")
            print(f"Éditeur: {vscode_app.editor}")
            print(f"Versions: {len(vscode_app.versions) if vscode_app.has_versions else 'N/A'}")

        print("\nTest de la configuration factorisée réussi!")

    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()


def test_template_resolution():
    """Test spécifique de la résolution des variables template."""
    print("\n" + "=" * 50)
    print("Test des variables template")
    print("=" * 50)

    # Test manuel de la résolution de template
    from string import Template

    test_cases = [
        {
            'template': '${base_url}/2025/MAYA/test.exe',
            'variables': {'base_url': 'https://efulfillment.autodesk.com/NetSWDLD'},
            'expected': 'https://efulfillment.autodesk.com/NetSWDLD/2025/MAYA/test.exe'
        },
        {
            'template': '${base_url}/nuke/download',
            'variables': {'base_url': 'https://www.foundry.com/products'},
            'expected': 'https://www.foundry.com/products/nuke/download'
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"  Template: {test_case['template']}")
        print(f"  Variables: {test_case['variables']}")

        template = Template(test_case['template'])
        result = template.safe_substitute(test_case['variables'])

        print(f"  Résultat: {result}")
        print(f"  Attendu:  {test_case['expected']}")
        print(f"  Succès: {'✓' if result == test_case['expected'] else '✗'}")

if __name__ == "__main__":
    test_factorized_structure()
    test_template_resolution()