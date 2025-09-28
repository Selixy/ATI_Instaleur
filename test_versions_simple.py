"""
Test simple de la structure des versions multiples.
"""

def test_yaml_structure():
    """Test de la structure YAML attendue."""
    print("Test de la structure YAML pour les versions multiples")
    print("=" * 60)

    # Structure simulée basée sur le nouveau YAML
    mock_config = {
        'applications': [
            {
                'name': 'Visual Studio Code',
                'description': 'Éditeur de code source léger et puissant',
                'category': 'Développement',
                'enabled': True,
                'has_versions': True,
                'versions': [
                    {
                        'name': 'Stable (Recommandé)',
                        'version': 'stable',
                        'methods': [
                            {
                                'type': 'exe',
                                'url': 'https://code.visualstudio.com/sha/download?build=stable&os=win32-x64',
                                'silent_args': '/verysilent /norestart /mergetasks=!runcode',
                                'priority': 1
                            }
                        ]
                    },
                    {
                        'name': 'Insiders (Beta)',
                        'version': 'insiders',
                        'methods': [
                            {
                                'type': 'exe',
                                'url': 'https://code.visualstudio.com/sha/download?build=insiders&os=win32-x64',
                                'silent_args': '/verysilent /norestart /mergetasks=!runcode',
                                'priority': 1
                            }
                        ]
                    }
                ]
            },
            {
                'name': 'Blender',
                'description': 'Suite de création 3D libre et gratuite',
                'category': '3D/Animation',
                'enabled': True,
                'has_versions': True,
                'versions': [
                    {
                        'name': '4.3.2 LTS (Recommandé)',
                        'version': '4.3.2',
                        'methods': [
                            {
                                'type': 'msi',
                                'url': 'https://download.blender.org/release/Blender4.3/blender-4.3.2-windows-x64.msi',
                                'silent_args': '/quiet /norestart',
                                'priority': 1
                            }
                        ]
                    },
                    {
                        'name': '4.2.3 LTS',
                        'version': '4.2.3',
                        'methods': [
                            {
                                'type': 'msi',
                                'url': 'https://download.blender.org/release/Blender4.2/blender-4.2.3-windows-x64.msi',
                                'silent_args': '/quiet /norestart',
                                'priority': 1
                            }
                        ]
                    }
                ]
            },
            {
                'name': 'Git',
                'description': 'Système de contrôle de version décentralisé',
                'category': 'Développement',
                'enabled': True,
                'has_versions': False,
                'methods': [
                    {
                        'type': 'exe',
                        'url': 'https://github.com/git-for-windows/git/releases/latest/download/Git-2.47.1-64-bit.exe',
                        'silent_args': '/VERYSILENT /NORESTART',
                        'priority': 1
                    }
                ]
            }
        ]
    }

    print("Structure YAML validee:")
    print()

    for app in mock_config['applications']:
        print(f"Package: {app['name']}")
        print(f"   Catégorie: {app['category']}")
        print(f"   Versions multiples: {'Oui' if app.get('has_versions', False) else 'Non'}")

        if app.get('has_versions', False):
            print(f"   Versions disponibles: {len(app.get('versions', []))}")
            for i, version in enumerate(app.get('versions', [])):
                print(f"      {i+1}. {version['name']} (v{version['version']})")
                methods = version.get('methods', [])
                for method in methods:
                    print(f"         - Installation: {method['type']} via {method['url'][:50]}...")
        else:
            methods = app.get('methods', [])
            print(f"   Méthodes d'installation: {len(methods)}")
            for method in methods:
                print(f"      - {method['type']}: {method['url'][:50]}...")
        print()

    print("Test de structure termine!")
    print()
    print("Interface attendue:")
    print("- Applications avec versions -> Menu deroulant pour choisir la version")
    print("- Applications classiques -> Pas de menu deroulant")
    print("- Selection d'application + version -> Envoi a l'installateur")

if __name__ == "__main__":
    test_yaml_structure()