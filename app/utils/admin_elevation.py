"""
Module pour gérer l'élévation administrateur sous Windows.
Module: utils.admin_elevation
"""

import sys
import os
import ctypes
import subprocess
import time
from pathlib import Path
from typing import Optional


def is_admin() -> bool:
    """
    Vérifie si le processus actuel a les privilèges administrateur.

    Returns:
        bool: True si administrateur, False sinon
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def request_admin_elevation() -> bool:
    """
    Teste si on peut obtenir l'élévation administrateur via UAC.
    NE REDÉMARRE PAS l'application.

    Returns:
        bool: True si on peut obtenir les privilèges, False sinon
    """
    if is_admin():
        return True

    try:
        # Tester l'élévation avec un processus simple (cmd /c echo)
        # Cela déclenchera UAC sans redémarrer l'application
        result = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            "cmd",
            "/c echo Elevation test > nul",
            None,
            0  # SW_HIDE - cacher la fenêtre
        )

        # Si ShellExecuteW réussit (result > 32), l'utilisateur a accepté UAC
        if result > 32:
            return True
        else:
            return False  # Élévation refusée

    except Exception as e:
        print(f"Erreur lors de la demande d'élévation: {e}")
        return False


def ensure_admin_privileges() -> bool:
    """
    S'assure que l'application a les privilèges administrateur.
    Demande l'élévation si nécessaire.

    Returns:
        bool: True si privilèges obtenus, False sinon
    """
    if is_admin():
        return True

    return request_admin_elevation()


def get_admin_status_message() -> str:
    """
    Retourne un message sur le statut administrateur.

    Returns:
        str: Message de statut
    """
    if is_admin():
        return "✅ Privilèges administrateur actifs"
    else:
        return "⚠️ Privilèges administrateur requis pour l'installation"


def run_as_admin(command: list, cwd: Optional[str] = None, show_window: bool = False) -> subprocess.CompletedProcess:
    """
    Exécute une commande avec les privilèges administrateur via UAC et attend la fin.

    Args:
        command: Commande à exécuter (liste d'arguments)
        cwd: Répertoire de travail (optionnel)
        show_window: Si True, affiche la fenêtre (défaut: False pour installation silencieuse)

    Returns:
        subprocess.CompletedProcess: Résultat de la commande
    """
    try:
        # Si on est déjà admin, utiliser subprocess.run directement
        if is_admin():
            return subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if not show_window else 0
            )

        # Sinon, créer un script PowerShell en ligne pour gérer l'élévation et attendre
        executable = command[0]
        args = command[1:] if len(command) > 1 else []

        # Construire la commande PowerShell directement (sans fichier temporaire)
        # Échapper les guillemets et antislashs pour PowerShell
        exe_escaped = executable.replace("'", "''").replace("\\", "\\\\")
        args_list = ','.join(f"'{arg.replace('\'', '\'\'')}'" for arg in args) if args else ''

        ps_command = f"$process = Start-Process -FilePath '{exe_escaped}' -ArgumentList {args_list} -Verb RunAs -PassThru -WindowStyle {'Normal' if show_window else 'Hidden'} -Wait; exit $process.ExitCode"

        # Exécuter le script PowerShell directement
        result = subprocess.run(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_command],
            cwd=cwd,
            capture_output=True,
            text=True
        )

        return result

    except Exception as e:
        print(f"Erreur lors de l'exécution: {e}")
        return subprocess.CompletedProcess(
            args=command,
            returncode=-1,
            stdout="",
            stderr=str(e)
        )


class AdminContext:
    """
    Gestionnaire de contexte pour maintenir les privilèges administrateur.
    """

    def __init__(self):
        self.was_admin = is_admin()
        self.elevation_requested = False

    def __enter__(self):
        if not self.was_admin:
            self.elevation_requested = ensure_admin_privileges()
            if not self.elevation_requested:
                raise PermissionError("Impossible d'obtenir les privilèges administrateur")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Rien à faire de spécial à la sortie
        # Les privilèges restent actifs pour toute la durée du processus
        pass

    def is_elevated(self) -> bool:
        """Vérifie si les privilèges ont été obtenus."""
        return is_admin()