"""
Test minimal du module simulation sans dépendances.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Import direct du module simulation
from app.core.installer import simulation
from app.core.installer.hook.status import InstallationMethod, InstallationStatus

def test_procedural_simulation():
    """Test des fonctions procédurales de simulation."""
    print("Test du module simulation procedural")
    print("=" * 40)

    # Test EXE
    print("\nTest EXE:")
    result = simulation.simulate_exe_installation(
        "Visual Studio Code",
        url="https://code.visualstudio.com/download",
        silent_args="/verysilent"
    )
    print(f"Status: {result.status}")
    print(f"Succès: {result.is_success}")

    # Test MSI
    print("\nTest MSI:")
    result = simulation.simulate_msi_installation(
        "TortoiseGit",
        url="https://download.tortoisegit.org/tgit/TortoiseGit-64bit.msi",
        silent_args="/quiet"
    )
    print(f"Status: {result.status}")
    print(f"Succès: {result.is_success}")

    # Test Winget
    print("\nTest Winget:")
    result = simulation.simulate_winget_installation(
        "PowerToys",
        package="Microsoft.PowerToys"
    )
    print(f"Status: {result.status}")
    print(f"Succès: {result.is_success}")

    # Test Chocolatey
    print("\nTest Chocolatey:")
    result = simulation.simulate_chocolatey_installation(
        "Git",
        package="git"
    )
    print(f"Status: {result.status}")
    print(f"Succès: {result.is_success}")

    # Test Direct Download
    print("\nTest Direct Download:")
    result = simulation.simulate_direct_download_installation(
        "Blender",
        url="https://download.blender.org/release/blender.msi"
    )
    print(f"Status: {result.status}")
    print(f"Succès: {result.is_success}")

    # Test par méthode
    print("\nTest par méthode:")
    result = simulation.simulate_installation_by_method(
        InstallationMethod.EXE,
        "OBS Studio",
        url="https://obsproject.com/download",
        silent_args="/S"
    )
    print(f"Status: {result.status}")
    print(f"Succès: {result.is_success}")

    # Test de vérification
    print("\nTest vérification disponibilité:")
    result = simulation.simulate_availability_check(InstallationMethod.WINGET)
    print(f"Status: {result.status}")
    print(f"Succès: {result.is_success}")

    print("\nTous les tests de simulation procedural reussis!")

if __name__ == "__main__":
    try:
        test_procedural_simulation()
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()