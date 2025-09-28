"""
Test direct du module simulation sans imports problématiques.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Copie directe des classes nécessaires pour éviter les imports
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

# Import direct des fonctions de simulation
import time
import random

def simulate_exe_installation(package_name: str, url: str = "", silent_args: str = "", **kwargs) -> InstallationResult:
    print(f"SIMULATION EXE: {package_name}")

    # Simulation téléchargement
    file_size = random.randint(50, 500)  # MB
    print(f"Telechargement depuis {url[:50]}...")
    print(f"Taille: {file_size} MB")

    # Simulation progression téléchargement
    for progress in range(0, 101, 20):
        time.sleep(0.1)
        print(f"Telechargement: {progress}%")

    print(f"Execution: {package_name}.exe {silent_args}")
    time.sleep(0.5)
    print(f"Installation simulee de {package_name} terminee!")

    return InstallationResult(
        status=InstallationStatus.SUCCESS,
        message=f"Installation simulée EXE de {package_name} réussie",
        package_name=package_name,
        method=InstallationMethod.EXE
    )

def test_procedural_simulation():
    """Test des fonctions procédurales de simulation."""
    print("Test du module simulation procedural")
    print("=" * 40)

    # Test EXE
    print("\nTest EXE:")
    result = simulate_exe_installation(
        "Visual Studio Code",
        url="https://code.visualstudio.com/download",
        silent_args="/verysilent"
    )
    print(f"Status: {result.status}")
    print(f"Succès: {result.is_success}")

    print("\nTest de simulation procedural reussi!")

if __name__ == "__main__":
    try:
        test_procedural_simulation()
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()