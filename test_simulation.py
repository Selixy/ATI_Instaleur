"""
Script de test pour le mode simulation.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.installer.main_installer import MainInstaller
from app.core.installer.hook.status import InstallationMethod

def test_simulation_mode():
    """Test du mode simulation."""
    print("🧪 Test du mode simulation")
    print("=" * 50)

    # Créer un installateur en mode simulation
    installer = MainInstaller(simulation_mode=True)

    print(f"\n✅ Mode simulation activé: {installer.is_simulation_enabled()}")
    print(f"📋 Installateurs disponibles: {len(installer.installers)}")

    # Test de compatibilité système
    print("\n🔍 Test de compatibilité système:")
    compatibility = installer.check_system_compatibility()
    for method, result in compatibility.items():
        status = "✅" if result.is_success else "❌"
        print(f"{status} {method.value}: {result.message}")

    # Test d'installation simple
    print("\n🎯 Test d'installation simple:")
    result = installer.install_single_package(
        "Visual Studio Code",
        preferred_method=InstallationMethod.EXE,
        url="https://code.visualstudio.com/download",
        silent_args="/verysilent"
    )

    print(f"\n📊 Résultat:")
    print(f"   Status: {result.status}")
    print(f"   Message: {result.message}")
    print(f"   Méthode: {result.method.value}")

    # Test d'installation multiple
    print("\n🎯 Test d'installation multiple:")
    packages_to_test = [
        "Visual Studio Code",
        "Git",
        "Blender"
    ]

    results = installer.install_packages(
        packages_to_test,
        preferred_method=InstallationMethod.EXE
    )

    print(f"\n📊 Résultats multiples:")
    for package, result in results.items():
        status = "✅" if result.is_success else "❌"
        print(f"{status} {package}: {result.message}")

    # Statistiques
    stats = installer.get_installation_stats()
    print(f"\n📈 Statistiques:")
    print(f"   Total: {stats['total_packages']}")
    print(f"   Succès: {stats['counts']['successful']}")
    print(f"   Échecs: {stats['counts']['failed']}")
    print(f"   Taux de succès: {stats['success_rate']:.1f}%")

def test_real_mode():
    """Test du mode réel (sans simulation)."""
    print("\n🔧 Test du mode réel")
    print("=" * 50)

    # Créer un installateur en mode réel
    installer = MainInstaller(simulation_mode=False)

    print(f"✅ Mode simulation activé: {installer.is_simulation_enabled()}")
    print(f"📋 Installateurs disponibles: {len(installer.installers)}")

    # Test de compatibilité
    print("\n🔍 Test de compatibilité système (mode réel):")
    compatibility = installer.check_system_compatibility()
    for method, result in compatibility.items():
        status = "✅" if result.is_success else "❌"
        print(f"{status} {method.value}: {result.message}")

def test_mode_switching():
    """Test du changement de mode."""
    print("\n🔄 Test du changement de mode")
    print("=" * 50)

    installer = MainInstaller(simulation_mode=False)

    print(f"Mode initial: {'Simulation' if installer.is_simulation_enabled() else 'Réel'}")

    # Activer simulation
    installer.enable_simulation_mode()
    print(f"Après activation: {'Simulation' if installer.is_simulation_enabled() else 'Réel'}")

    # Désactiver simulation
    installer.disable_simulation_mode()
    print(f"Après désactivation: {'Simulation' if installer.is_simulation_enabled() else 'Réel'}")

if __name__ == "__main__":
    try:
        test_simulation_mode()
        test_real_mode()
        test_mode_switching()

        print("\n🎉 Tous les tests terminés avec succès!")

    except Exception as e:
        print(f"\n❌ Erreur pendant les tests: {e}")
        import traceback
        traceback.print_exc()