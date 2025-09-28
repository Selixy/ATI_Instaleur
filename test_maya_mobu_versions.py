"""
Test des versions multiples pour Maya et MotionBuilder.
"""

def test_maya_mobu_versions():
    """Test de la configuration des versions Maya et MotionBuilder."""
    print("Test des versions Maya et MotionBuilder")
    print("=" * 50)

    # Configuration simulée pour Maya
    maya_config = {
        'name': 'Autodesk Maya',
        'description': 'Logiciel de modélisation et d\'animation 3D',
        'category': '3D/Animation',
        'has_versions': True,
        'versions': [
            {
                'name': '2025 (Recommandé)',
                'version': '2025',
                'methods': [
                    {
                        'type': 'exe',
                        'url': 'https://efulfillment.autodesk.com/NetSWDLD/2025/MAYA/FD0B8EC0-CA1C-3F6E-A3FC-69A7A1BD4C4E/SFX/Autodesk_Maya_2025_ML_Windows_64bit_dlm.sfx.exe',
                        'silent_args': '--mode unattended --accept_eula'
                    }
                ]
            },
            {
                'name': '2024.3',
                'version': '2024.3',
                'methods': [
                    {
                        'type': 'exe',
                        'url': 'https://efulfillment.autodesk.com/NetSWDLD/2024/MAYA/42762096-E3FE-3521-9687-693E0B913A4F/SFX/Autodesk_Maya_2024_1_Update_Windows_64bit_dlm_001_002.sfx.exe',
                        'silent_args': '--mode unattended --accept_eula'
                    }
                ]
            },
            {
                'name': '2023.3 LTS',
                'version': '2023.3',
                'methods': [
                    {
                        'type': 'exe',
                        'url': 'https://efulfillment.autodesk.com/NetSWDLD/2023/MAYA/756B4F18-3772-391C-81C9-69A4F8F12177/SFX/Autodesk_Maya_2023_ML_Windows_64bit_dlm.sfx.exe',
                        'silent_args': '--mode unattended --accept_eula'
                    }
                ]
            },
            {
                'name': '2022.5 LTS',
                'version': '2022.5',
                'methods': [
                    {
                        'type': 'exe',
                        'url': 'https://efulfillment.autodesk.com/NetSWDLD/2022/MAYA/756B4F18-3772-391C-81C9-69A4F8F12177/SFX/Autodesk_Maya_2022_ML_Windows_64bit_dlm.sfx.exe',
                        'silent_args': '--mode unattended --accept_eula'
                    }
                ]
            }
        ]
    }

    # Configuration simulée pour MotionBuilder
    mobu_config = {
        'name': 'Autodesk MotionBuilder',
        'description': 'Logiciel d\'animation 3D en temps réel',
        'category': '3D/Animation',
        'has_versions': True,
        'versions': [
            {
                'name': '2025 (Recommandé)',
                'version': '2025',
                'methods': [
                    {
                        'type': 'exe',
                        'url': 'https://efulfillment.autodesk.com/NetSWDLD/2025/MOBPRO/8E8A1C2E-0952-3C68-842C-69A9FEB04127/SFX/Autodesk_MotionBuilder_2025_ML_Windows_64bit_dlm.sfx.exe',
                        'silent_args': '--mode unattended --accept_eula'
                    }
                ]
            },
            {
                'name': '2024',
                'version': '2024',
                'methods': [
                    {
                        'type': 'exe',
                        'url': 'https://efulfillment.autodesk.com/NetSWDLD/2024/MOBPRO/8E8A1C2E-0952-3C68-842C-69A9FEB04127/SFX/Autodesk_MotionBuilder_2024_ML_Windows_64bit_dlm.sfx.exe',
                        'silent_args': '--mode unattended --accept_eula'
                    }
                ]
            },
            {
                'name': '2023',
                'version': '2023',
                'methods': [
                    {
                        'type': 'exe',
                        'url': 'https://efulfillment.autodesk.com/NetSWDLD/2023/MOBPRO/8E8A1C2E-0952-3C68-842C-69A9FEB04127/SFX/Autodesk_MotionBuilder_2023_ML_Windows_64bit_dlm.sfx.exe',
                        'silent_args': '--mode unattended --accept_eula'
                    }
                ]
            },
            {
                'name': '2022',
                'version': '2022',
                'methods': [
                    {
                        'type': 'exe',
                        'url': 'https://dds.autodesk.com/NetSWDLD/2022/MOBPRO/330EFCEA-0952-3C68-842C-69A9FEB04127/SFX/Autodesk_MB_2022_ML_Windows_64bit_dlm.sfx.exe',
                        'silent_args': '--mode unattended --accept_eula'
                    }
                ]
            }
        ]
    }

    # Affichage des configurations
    for app_config in [maya_config, mobu_config]:
        print(f"\nApplication: {app_config['name']}")
        print(f"Description: {app_config['description']}")
        print(f"Versions multiples: {'Oui' if app_config['has_versions'] else 'Non'}")
        print(f"Nombre de versions: {len(app_config['versions'])}")

        for i, version in enumerate(app_config['versions']):
            print(f"  Version {i+1}: {version['name']} (v{version['version']})")
            for method in version['methods']:
                print(f"    - Type: {method['type']}")
                print(f"    - URL: {method['url'][:60]}...")
                print(f"    - Args silencieux: {method['silent_args']}")
        print()

    print("Interface utilisateur attendue:")
    print("- Menu deroulant Maya avec 4 versions (2025, 2024.3, 2023.3 LTS, 2022.5 LTS)")
    print("- Menu deroulant MotionBuilder avec 4 versions (2025, 2024, 2023, 2022)")
    print("- Version recommandee selectionnee par defaut (2025)")
    print("- Arguments d'installation silencieuse avec --accept_eula")

if __name__ == "__main__":
    test_maya_mobu_versions()