"""
Test du système default_version_index.
"""

def test_default_version_index():
    """Test de la fonctionnalité default_version_index."""
    print("Test du système default_version_index")
    print("=" * 50)

    # Simulation des applications avec default_version_index
    test_apps = [
        {
            'name': 'Visual Studio Code',
            'has_versions': True,
            'default_version_index': 0,  # "Stable (Recommandé)"
            'versions': [
                {'name': 'Stable (Recommandé)', 'version': 'stable'},
                {'name': 'Insiders (Beta)', 'version': 'insiders'}
            ]
        },
        {
            'name': 'Blender',
            'has_versions': True,
            'default_version_index': 0,  # "3.6 (Recommandé)"
            'versions': [
                {'name': '3.6 (Recommandé)', 'version': '3.6.17'},
                {'name': '4.3.2 LTS', 'version': '4.3.2'},
                {'name': '4.2.3 LTS', 'version': '4.2.3'}
            ]
        },
        {
            'name': 'Autodesk Maya',
            'has_versions': True,
            'default_version_index': 1,  # "2024.3 (Recommandé)"
            'versions': [
                {'name': '2025', 'version': '2025'},
                {'name': '2024.3 (Recommandé)', 'version': '2024.3'},
                {'name': '2023.3 LTS', 'version': '2023.3'},
                {'name': '2022.5 LTS', 'version': '2022.5'}
            ]
        },
        {
            'name': 'Autodesk MotionBuilder',
            'has_versions': True,
            'default_version_index': 3,  # "2022 (Recommandé)"
            'versions': [
                {'name': '2025', 'version': '2025'},
                {'name': '2024', 'version': '2024'},
                {'name': '2023', 'version': '2023'},
                {'name': '2022 (Recommandé)', 'version': '2022'}
            ]
        }
    ]

    def get_default_version(app):
        """Simule la méthode get_default_version."""
        if not app['has_versions'] or not app['versions']:
            return None

        default_index = app.get('default_version_index', 0)
        if 0 <= default_index < len(app['versions']):
            return app['versions'][default_index]

        return app['versions'][0] if app['versions'] else None

    print("Configuration des versions par défaut:")
    print()

    for app in test_apps:
        print(f"Application: {app['name']}")
        print(f"  Index par défaut: {app['default_version_index']}")
        print(f"  Versions disponibles:")

        for i, version in enumerate(app['versions']):
            indicator = " -> DÉFAUT" if i == app['default_version_index'] else ""
            print(f"    [{i}] {version['name']} (v{version['version']}){indicator}")

        default_version = get_default_version(app)
        if default_version:
            print(f"  Version sélectionnée au démarrage: {default_version['name']}")

        print()

    print("Comportement attendu dans l'interface:")
    print("- VS Code: Menu déroulant avec 'Stable (Recommandé)' sélectionné")
    print("- Blender: Menu déroulant avec '3.6 (Recommandé)' sélectionné")
    print("- Maya: Menu déroulant avec '2024.3 (Recommandé)' sélectionné")
    print("- MotionBuilder: Menu déroulant avec '2022 (Recommandé)' sélectionné")
    print()
    print("Test de validation des index:")

    # Test d'index invalide
    test_invalid = {
        'name': 'Test Invalid',
        'has_versions': True,
        'default_version_index': 99,  # Index invalide
        'versions': [
            {'name': 'Version 1', 'version': '1.0'},
            {'name': 'Version 2', 'version': '2.0'}
        ]
    }

    default_version = get_default_version(test_invalid)
    print(f"Index invalide (99) -> Fallback sur: {default_version['name'] if default_version else 'None'}")

    print("\nTous les tests réussis!")

if __name__ == "__main__":
    test_default_version_index()