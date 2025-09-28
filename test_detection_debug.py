#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from core.installer.windows_package_detector import get_windows_detector

def test_detection():
    detector = get_windows_detector()

    # Test applications avec problèmes
    test_apps = ["FileZilla", "Blender", "Visual Studio Code", "Chrome", "Firefox"]

    for app in test_apps:
        print(f"\n=== Test pour {app} ===")
        result = detector.debug_search(app)

        print(f"Nom original: {result['original_name']}")
        print(f"Nom nettoyé: {result['cleaned_name']}")
        print(f"Trouvé dans registre: {result['found_in_registry']}")
        print(f"Trouvé dans Program Files: {result['found_in_program_files']}")

        if result['registry_matches']:
            print(f"Correspondances registre: {result['registry_matches']}")

        if result['program_files_matches']:
            print(f"Correspondances Program Files: {result['program_files_matches']}")

        # Test final
        is_installed = detector.is_package_installed_by_name(app)
        print(f"RÉSULTAT FINAL: {'INSTALLÉ' if is_installed else 'NON INSTALLÉ'}")

if __name__ == "__main__":
    test_detection()