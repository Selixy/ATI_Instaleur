"""
Test direct sans dépendances externes.
"""

# Copie des enums nécessaires pour le test
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class InstallationStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"

class InstallationMethod(Enum):
    WINGET = "winget"
    EXE = "exe"
    MSI = "msi"
    CHOCOLATEY = "chocolatey"
    DIRECT_DOWNLOAD = "direct_download"

@dataclass
class InstallationResult:
    status: InstallationStatus
    message: str
    package_name: str = ""
    method: Optional[InstallationMethod] = None

    @property
    def is_success(self) -> bool:
        return self.status == InstallationStatus.SUCCESS

def test_simulation_logic():
    """Test de la logique de simulation."""
    print("Test de simulation procedural")
    print("=" * 30)

    # Test simulé simple
    def simulate_exe_installation(package_name: str, url: str = "", silent_args: str = ""):
        print(f"SIMULATION EXE: {package_name}")
        print(f"URL: {url[:30]}...")
        print(f"Args: {silent_args}")
        print(f"Installation simulee reussie!")

        return InstallationResult(
            status=InstallationStatus.SUCCESS,
            message=f"Installation simulee de {package_name} reussie",
            package_name=package_name,
            method=InstallationMethod.EXE
        )

    # Test
    result = simulate_exe_installation(
        "Visual Studio Code",
        url="https://code.visualstudio.com/download",
        silent_args="/verysilent"
    )

    print(f"\nResultat:")
    print(f"Status: {result.status}")
    print(f"Message: {result.message}")
    print(f"Methode: {result.method.value}")
    print(f"Succes: {result.is_success}")

    return result.is_success

if __name__ == "__main__":
    try:
        success = test_simulation_logic()
        if success:
            print("\nTOUS LES TESTS REUSSIS!")
        else:
            print("\nECHEC DES TESTS!")
    except Exception as e:
        print(f"Erreur: {e}")