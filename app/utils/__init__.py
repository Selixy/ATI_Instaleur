"""
Module utilitaires pour ATI_Instaleur.
"""

from .admin_elevation import (
    is_admin,
    request_admin_elevation,
    ensure_admin_privileges,
    get_admin_status_message,
    run_as_admin,
    AdminContext
)

__all__ = [
    'is_admin',
    'request_admin_elevation',
    'ensure_admin_privileges',
    'get_admin_status_message',
    'run_as_admin',
    'AdminContext'
]
