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


def simulate_installation_by_method(method: InstallationMethod, package_name: str, **kwargs) -> InstallationResult:
    """
    Simule l'installation selon la méthode spécifiée.

    Args:
        method: Méthode d'installation
        package_name: Nom du package
        **kwargs: Arguments supplémentaires

    Returns:
        InstallationResult: Résultat simulé
    """
    # Délai aléatoire pour simuler la variabilité
    time.sleep(random.uniform(0.1, 0.3))

    simulation_functions = {
        InstallationMethod.EXE: simulate_exe_installation,
        InstallationMethod.MSI: simulate_msi_installation
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
            message=f"Erreur lors de la simulation {method.value}: {e}",
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