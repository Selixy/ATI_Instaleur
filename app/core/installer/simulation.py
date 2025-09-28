"""
Module de simulation d'installation procédural.
Simule les différentes méthodes d'installation sans les exécuter réellement.
Module: core.installer.simulation
"""

import time
import random
from typing import Dict, Any, Optional
from .hook.status import InstallationResult, InstallationStatus, InstallationMethod


def simulate_exe_installation(package_name: str, url: str = "", silent_args: str = "", **kwargs) -> InstallationResult:
    """
    Simule l'installation d'un package EXE.

    Args:
        package_name: Nom du package
        url: URL de téléchargement
        silent_args: Arguments silencieux
        **kwargs: Arguments supplémentaires

    Returns:
        InstallationResult: Résultat simulé
    """
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


def simulate_msi_installation(package_name: str, url: str = "", silent_args: str = "", **kwargs) -> InstallationResult:
    """
    Simule l'installation d'un package MSI.

    Args:
        package_name: Nom du package
        url: URL de téléchargement
        silent_args: Arguments silencieux
        **kwargs: Arguments supplémentaires

    Returns:
        InstallationResult: Résultat simulé
    """
    print(f"SIMULATION MSI: {package_name}")

    # Simulation téléchargement
    file_size = random.randint(30, 200)  # MB
    print(f"Telechargement MSI depuis {url[:50]}...")
    print(f"Taille: {file_size} MB")

    # Simulation progression téléchargement
    for progress in range(0, 101, 25):
        time.sleep(0.1)
        print(f"Telechargement: {progress}%")

    print(f"Execution: msiexec /i {package_name}.msi {silent_args}")
    time.sleep(0.3)
    print(f"Configuration composants...")
    time.sleep(0.2)
    print(f"Ecriture registre...")
    time.sleep(0.2)
    print(f"Installation simulee de {package_name} terminee!")

    return InstallationResult(
        status=InstallationStatus.SUCCESS,
        message=f"Installation simulée MSI de {package_name} réussie",
        package_name=package_name,
        method=InstallationMethod.MSI
    )


def simulate_winget_installation(package_name: str, package: str = "", **kwargs) -> InstallationResult:
    """
    Simule l'installation d'un package Winget.

    Args:
        package_name: Nom du package
        package: ID du package winget
        **kwargs: Arguments supplémentaires

    Returns:
        InstallationResult: Résultat simulé
    """
    print(f"SIMULATION WINGET: {package_name}")

    package_id = package or package_name
    print(f"Recherche du package: {package_id}")
    time.sleep(0.2)
    print(f"Package trouve: {package_id}")
    print(f"Execution: winget install {package_id}")

    # Simulation progression
    for progress in range(0, 101, 33):
        time.sleep(0.15)
        print(f"Installation: {progress}%")

    print(f"Installation simulee de {package_name} terminee!")

    return InstallationResult(
        status=InstallationStatus.SUCCESS,
        message=f"Installation simulée Winget de {package_name} réussie",
        package_name=package_name,
        method=InstallationMethod.WINGET
    )


def simulate_chocolatey_installation(package_name: str, package: str = "", **kwargs) -> InstallationResult:
    """
    Simule l'installation d'un package Chocolatey.

    Args:
        package_name: Nom du package
        package: ID du package chocolatey
        **kwargs: Arguments supplémentaires

    Returns:
        InstallationResult: Résultat simulé
    """
    print(f"SIMULATION CHOCOLATEY: {package_name}")

    package_id = package or package_name
    print(f"Recherche sur chocolatey.org: {package_id}")
    time.sleep(0.2)
    print(f"Package trouve dans le repository")
    print(f"Execution: choco install {package_id} -y")

    # Simulation téléchargement dépendances
    deps = random.randint(0, 3)
    if deps > 0:
        print(f"Telechargement de {deps} dependance(s)...")
        time.sleep(0.3)

    # Simulation progression
    for progress in range(0, 101, 25):
        time.sleep(0.1)
        print(f"Installation: {progress}%")

    print(f"Installation simulee de {package_name} terminee!")

    return InstallationResult(
        status=InstallationStatus.SUCCESS,
        message=f"Installation simulée Chocolatey de {package_name} réussie",
        package_name=package_name,
        method=InstallationMethod.CHOCOLATEY
    )


def simulate_direct_download_installation(package_name: str, url: str = "", **kwargs) -> InstallationResult:
    """
    Simule l'installation par téléchargement direct.

    Args:
        package_name: Nom du package
        url: URL de téléchargement
        **kwargs: Arguments supplémentaires

    Returns:
        InstallationResult: Résultat simulé
    """
    print(f"SIMULATION DIRECT DOWNLOAD: {package_name}")

    print(f"Acces au site: {url[:50]}...")
    time.sleep(0.3)
    print(f"Detection de l'installeur...")
    time.sleep(0.2)

    # Simulation téléchargement
    file_size = random.randint(100, 1000)  # MB
    print(f"Telechargement: {file_size} MB")

    # Simulation progression téléchargement
    for progress in range(0, 101, 20):
        time.sleep(0.1)
        print(f"Telechargement: {progress}%")

    print(f"Lancement de l'installation...")
    time.sleep(0.4)
    print(f"Installation simulee de {package_name} terminee!")

    return InstallationResult(
        status=InstallationStatus.SUCCESS,
        message=f"Installation simulée par téléchargement direct de {package_name} réussie",
        package_name=package_name,
        method=InstallationMethod.DIRECT_DOWNLOAD
    )


def simulate_installation_by_method(method: InstallationMethod, package_name: str, **kwargs) -> InstallationResult:
    """
    Simule l'installation selon la méthode spécifiée.

    Args:
        method: Méthode d'installation
        package_name: Nom du package
        **kwargs: Arguments pour l'installation

    Returns:
        InstallationResult: Résultat simulé
    """
    # Délai aléatoire pour simuler la variabilité
    time.sleep(random.uniform(0.1, 0.3))

    simulation_functions = {
        InstallationMethod.EXE: simulate_exe_installation,
        InstallationMethod.MSI: simulate_msi_installation,
        InstallationMethod.WINGET: simulate_winget_installation,
        InstallationMethod.CHOCOLATEY: simulate_chocolatey_installation,
        InstallationMethod.DIRECT_DOWNLOAD: simulate_direct_download_installation
    }

    simulation_func = simulation_functions.get(method)

    if not simulation_func:
        return InstallationResult(
            status=InstallationStatus.FAILED,
            message=f"Méthode de simulation inconnue: {method.value}",
            package_name=package_name,
            method=method
        )

    try:
        return simulation_func(package_name, **kwargs)
    except Exception as e:
        return InstallationResult(
            status=InstallationStatus.FAILED,
            message=f"Erreur pendant la simulation {method.value}: {e}",
            package_name=package_name,
            method=method
        )


def simulate_availability_check(method: InstallationMethod) -> InstallationResult:
    """
    Simule la vérification de disponibilité d'une méthode.

    Args:
        method: Méthode à vérifier

    Returns:
        InstallationResult: Résultat de disponibilité simulé
    """
    print(f"Verification simulee de {method.value}...")
    time.sleep(0.1)

    # Simulation: toutes les méthodes sont disponibles
    return InstallationResult(
        status=InstallationStatus.SUCCESS,
        message=f"Méthode {method.value} disponible (simulation)",
        package_name="",
        method=method
    )


def enable_simulation_mode():
    """Active le mode simulation pour tous les installeurs."""
    print("MODE SIMULATION ACTIVE")
    print("Aucune installation reelle ne sera effectuee")
    print("Toutes les installations seront simulees")


def disable_simulation_mode():
    """Désactive le mode simulation."""
    print("MODE SIMULATION DESACTIVE")
    print("Les installations seront reelles")