"""
Test simple de la structure factorisée (sans dépendances).
"""

def test_factorized_concept():
    """Test du concept de configuration factorisée."""
    print("Test du concept de configuration factorisee")
    print("=" * 50)

    # Structure simulée pour montrer le concept
    mock_factorized_config = {
        'editors': {
            'autodesk': {
                'name': 'Autodesk',
                'default_silent_args': '--mode unattended --accept_eula',
                'base_url': 'https://efulfillment.autodesk.com/NetSWDLD',
                'applications': [
                    {
                        'name': 'Maya',
                        'category': '3D/Animation',
                        'has_versions': True,
                        'default_version_index': 1,
                        'versions': [
                            {
                                'name': '2025',
                                'version': '2025',
                                'methods': [{'type': 'exe', 'url': '${base_url}/2025/MAYA/maya.exe'}]
                            },
                            {
                                'name': '2024.3 (Recommande)',
                                'version': '2024.3',
                                'methods': [{'type': 'exe', 'url': '${base_url}/2024/MAYA/maya.exe'}]
                            }
                        ]
                    },
                    {
                        'name': 'MotionBuilder',
                        'category': '3D/Animation',
                        'has_versions': True,
                        'default_version_index': 3,
                        'versions': [
                            {'name': '2025', 'version': '2025'},
                            {'name': '2024', 'version': '2024'},
                            {'name': '2023', 'version': '2023'},
                            {'name': '2022 (Recommande)', 'version': '2022'}
                        ]
                    }
                ]
            },
            'microsoft': {
                'name': 'Microsoft',
                'default_silent_args': '/quiet /norestart',
                'applications': [
                    {
                        'name': 'Visual Studio Code',
                        'category': 'Developpement',
                        'has_versions': True,
                        'default_version_index': 0,
                        'versions': [
                            {'name': 'Stable (Recommande)', 'version': 'stable'},
                            {'name': 'Insiders (Beta)', 'version': 'insiders'}
                        ]
                    }
                ]
            },
            'blender_foundation': {
                'name': 'Blender Foundation',
                'default_silent_args': '/quiet /norestart',
                'base_url': 'https://download.blender.org/release',
                'applications': [
                    {
                        'name': 'Blender',
                        'category': '3D/Animation',
                        'has_versions': True,
                        'default_version_index': 0,
                        'versions': [
                            {'name': '3.6 (Recommande)', 'version': '3.6.17'},
                            {'name': '4.3.2 LTS', 'version': '4.3.2'},
                            {'name': '4.2.3 LTS', 'version': '4.2.3'}
                        ]
                    }
                ]
            }
        },
        'categories': {
            'development': {
                'name': 'Developpement',
                'applications': [
                    {
                        'name': 'Git',
                        'description': 'Systeme de controle de version decentralise',
                        'methods': [{'type': 'exe', 'url': 'https://github.com/git-for-windows/git/releases/latest/download/Git.exe'}]
                    }
                ]
            }
        }
    }

    print("AVANTAGES de la structure factorisee:")
    print()

    # 1. Factorisation par éditeur
    print("1. FACTORISATION PAR EDITEUR:")
    for editor_id, editor_data in mock_factorized_config['editors'].items():
        print(f"   {editor_data['name']}:")
        print(f"     - Args silencieux par defaut: {editor_data.get('default_silent_args', 'N/A')}")
        print(f"     - URL de base: {editor_data.get('base_url', 'N/A')}")
        print(f"     - Applications: {len(editor_data['applications'])}")

        for app in editor_data['applications']:
            versions_info = ""
            if app.get('has_versions'):
                default_idx = app.get('default_version_index', 0)
                versions = app.get('versions', [])
                if versions and 0 <= default_idx < len(versions):
                    default_version = versions[default_idx]['name']
                    versions_info = f" | {len(versions)} versions | Defaut: {default_version}"

            print(f"       * {app['name']} ({app['category']}){versions_info}")
        print()

    # 2. Template variables
    print("2. VARIABLES TEMPLATE:")
    autodesk = mock_factorized_config['editors']['autodesk']
    base_url = autodesk['base_url']
    print(f"   Base URL Autodesk: {base_url}")

    maya_app = autodesk['applications'][0]  # Maya
    if maya_app['has_versions']:
        for version in maya_app['versions'][:2]:  # Montrer 2 versions
            template_url = version['methods'][0]['url']
            resolved_url = template_url.replace('${base_url}', base_url)
            print(f"     Maya {version['version']}: {template_url} -> {resolved_url}")

    print()

    # 3. Réduction de duplication
    print("3. REDUCTION DE DUPLICATION:")
    print("   AVANT (structure plate):")
    print("     - Chaque app Autodesk repetait '--mode unattended --accept_eula'")
    print("     - URLs completes repetees pour chaque version")
    print("     - Parametres disperses dans tout le fichier")
    print()
    print("   APRES (structure factorisee):")
    print("     - Args silencieux definis une fois par editeur")
    print("     - Base URL definie une fois, utilisee partout")
    print("     - Groupement logique par editeur/categorie")

    print()

    # 4. Organisation
    print("4. ORGANISATION:")
    apps_by_editor = {}
    apps_by_category = {}

    # Simuler le groupement
    for editor_id, editor_data in mock_factorized_config['editors'].items():
        editor_name = editor_data['name']
        apps_by_editor[editor_name] = len(editor_data['applications'])

        for app in editor_data['applications']:
            category = app['category']
            apps_by_category[category] = apps_by_category.get(category, 0) + 1

    # Ajouter les apps des catégories générales
    for cat_id, cat_data in mock_factorized_config['categories'].items():
        category = cat_data['name']
        apps_by_category[category] = apps_by_category.get(category, 0) + len(cat_data['applications'])

    print("   Repartition par editeur:")
    for editor, count in apps_by_editor.items():
        print(f"     - {editor}: {count} applications")

    print("   Repartition par categorie:")
    for category, count in apps_by_category.items():
        print(f"     - {category}: {count} applications")

    print()
    print("5. MAINTENANCE:")
    print("   - Modification d'un parametre Autodesk -> un seul endroit")
    print("   - Ajout d'une nouvelle version Maya -> juste dans la section Autodesk")
    print("   - URLs plus courtes et lisibles")
    print("   - Structure plus claire pour nouveaux developpeurs")

    print()
    print("STRUCTURE FINALE:")
    print("config_factorized.yaml")
    print("├── editors/")
    print("│   ├── autodesk/ (parametres communs + apps)")
    print("│   ├── microsoft/ (parametres communs + apps)")
    print("│   ├── adobe/ (parametres communs + apps)")
    print("│   └── foundry/ (parametres communs + apps)")
    print("├── categories/ (apps independantes)")
    print("│   ├── development/ (Git, TortoiseGit...)")
    print("│   └── utilities/ (7-Zip, VLC...)")
    print("└── global_settings/ (parametres globaux)")

    print("\nTest du concept factorise reussi!")

if __name__ == "__main__":
    test_factorized_concept()