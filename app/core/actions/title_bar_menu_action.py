# app/core/actions/title_bar_menu_action.py



def on_custom_path_click():
    """Action exécutée quand on clique sur le bouton de configuration du chemin personnalisé."""
    from ui.dialogs.custom_path_dialog import CustomInstallPathDialog
    from PySide6.QtWidgets import QApplication

    # Récupérer la fenêtre principale comme parent
    main_window = None
    for widget in QApplication.allWidgets():
        if hasattr(widget, 'setWindowTitle') and 'ATI Instaleur' in str(widget.windowTitle()):
            main_window = widget
            break

    # Créer et afficher la boîte de dialogue
    dialog = CustomInstallPathDialog(main_window)
    dialog.exec()

