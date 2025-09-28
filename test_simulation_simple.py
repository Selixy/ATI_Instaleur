"""
Test simple du module simulation.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.core.installer.hook.status import InstallationMethod
    from app.core.installer import simulation

    def test_simulation_functions():
        """Test des fonctions de simulation."""
        print("🧪 Test des fonctions de simulation")
        print("=" * 50)

        # Test simulation EXE
        print("\n📥 Test EXE:")
        result = simulation.simulate_exe_installation(
            "Visual Studio Code",
            url="https://code.visualstudio.com/download",
            silent_args="/verysilent"
        )
        print(f"Status: {result.status}")
        print(f"Message: {result.message}")

        # Test simulation MSI
        print("\n📦 Test MSI:")
        result = simulation.simulate_msi_installation(
            "TortoiseGit",
            url="https://download.tortoisegit.org/tgit/TortoiseGit-64bit.msi",
            silent_args="/quiet"
        )
        print(f"Status: {result.status}")
        print(f"Message: {result.message}")

        # Test simulation Winget
        print("\n🏪 Test Winget:")
        result = simulation.simulate_winget_installation(
            "PowerToys",
            package="Microsoft.PowerToys"
        )
        print(f"Status: {result.status}")
        print(f"Message: {result.message}")

        # Test simulation Chocolatey
        print("\n🍫 Test Chocolatey:")
        result = simulation.simulate_chocolatey_installation(
            "Git",
            package="git"
        )
        print(f"Status: {result.status}")
        print(f"Message: {result.message}")

        # Test simulation par méthode
        print("\n🎯 Test par méthode:")
        result = simulation.simulate_installation_by_method(
            InstallationMethod.EXE,
            "Blender",
            url="https://download.blender.org/release/blender.msi",
            silent_args="/quiet"
        )
        print(f"Status: {result.status}")
        print(f"Message: {result.message}")

        print("\n✅ Tous les tests de simulation terminés!")

    if __name__ == "__main__":
        test_simulation_functions()

except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()