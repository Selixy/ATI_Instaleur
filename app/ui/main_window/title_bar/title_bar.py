from PySide6.QtWidgets import QHBoxLayout, QWidget, QPushButton, QLabel, QSizePolicy
from PySide6.QtGui import QIcon, QFontMetrics
from PySide6.QtCore import Qt
from qframelesswindow import TitleBar
import importlib
import os

from utils.resource_manager import get_resource_manager
from config import TITLE_BAR_BUTTONS


class CustomTitleBar(TitleBar):
    """Barre de titre personnalisée avec boutons configurables."""
    
    def __init__(self, parent, buttons_config=None):
        super().__init__(parent)
        
        # Configuration de l'objectName pour le CSS
        self.setObjectName("CustomTitleBar")
        
        # Configuration initiale
        self.hBoxLayout = self.layout()
        self.buttons_config = buttons_config or TITLE_BAR_BUTTONS

        # definition du bouton de fermeture
        self.closeBtn.setObjectName("CloseButton")
        
        # Initialisation des composants (plus de titre)
        self._setup_button_container()
        self._create_buttons()
    
    def _setup_button_container(self):
        """Configure le conteneur des boutons personnalisés."""
        self.buttonWidget = QWidget()
        self.buttonLayout = QHBoxLayout(self.buttonWidget)
        self.buttonLayout.setSpacing(0)  # Supprime l'espace entre tous les widgets
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # Centrage vertical
        
        # Insertion dans le layout principal dès le début
        self.hBoxLayout.insertWidget(0, self.buttonWidget)
        self.hBoxLayout.insertStretch(1)
    
    def _create_buttons(self):
        """Crée les boutons à partir de la configuration."""
        for i, config in enumerate(self.buttons_config):
            button = self._create_single_button(config)
            
            # Traitement spécial pour le premier bouton
            if i == 0:
                button.setProperty("isFirstButton", True)
                # Ajouter les effets glow pour le premier bouton
                self._setup_glow_effects(button, config)
            elif i == 1:
                button.setProperty("isSecondButton", True)  # Pour le CSS
            
            self.buttonLayout.addWidget(button)
            
            # Widget spacer après le premier bouton pour contrôle CSS
            if i == 0 and len(self.buttons_config) > 1:
                spacer = QWidget()
                spacer.setObjectName("firstButtonSpacer")
                # Pas de setFixedWidth() pour laisser le CSS contrôler
                self.buttonLayout.addWidget(spacer)
    
    def _create_single_button(self, config):
        """Crée un bouton individuel basé sur sa configuration."""
        button = QPushButton()
        
        # Configuration du contenu
        self._configure_button_content(button, config)
        
        # Configuration des propriétés et styling
        self._configure_button_properties(button, config)
        
        # Configuration des dimensions
        self._configure_button_dimensions(button)
        
        # Connexion des actions seulement si cliquable
        if config.get("clickable", True) and "action" in config:
            self._connect_action(button, config["action"])
        elif not config.get("clickable", True):
            button.setEnabled(False)  # Désactiver visuellement si pas cliquable
        
        return button
    
    def _configure_button_content(self, button, config):
        """Configure le contenu du bouton (texte, icône, tooltip)."""
        if "text" in config:
            button.setText(config["text"])
        
        if "icon" in config:
            button.setIcon(QIcon(config["icon"]))
        
        if "tooltip" in config:
            button.setToolTip(config["tooltip"])
    
    def _configure_button_properties(self, button, config):
        """Configure les propriétés et l'ID du bouton pour le CSS."""
        # Propriété commune pour tous les boutons de la title bar
        button.setProperty("isTitleBarButton", True)
        
        # Propriété cliquable
        button.setProperty("clickable", config.get("clickable", True))
        
        # ID spécifique si défini
        if "id" in config:
            button.setObjectName(config["id"])
        
        # Tag spécifique si défini (alternative à id)
        if "tag" in config:
            button.setObjectName(config["tag"])
        
        # Propriétés supplémentaires
        if "tags" in config:
            for tag_name, tag_value in config.get("tags", {}).items():
                button.setProperty(tag_name, tag_value)
    
    def _configure_button_dimensions(self, button):
        """Configure les dimensions du bouton."""
        button.setFixedHeight(24)
        self._adjust_button_width(button)
        button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    
    def _adjust_button_width(self, button):
        """Ajuste la largeur du bouton en fonction de son contenu."""
        content_width = 0
        
        # Calcul de la largeur du texte
        if button.text():
            font_metrics = QFontMetrics(button.font())
            content_width += font_metrics.horizontalAdvance(button.text())
        
        # Ajout de la largeur de l'icône
        if button.icon():
            content_width += 24
        
        # Ajout des marges
        content_width += 10
        
        # Application de la largeur finale
        min_width = 30
        final_width = max(content_width, min_width)
        button.setFixedWidth(final_width)
    
    def _setup_glow_effects(self, button, config):
        """Configure les effets glow pour le bouton (changement d'icône au hover)."""
        if "icon" not in config:
            return
        
        original_icon = config["icon"]
        glow_icon = self._get_glow_icon_path(original_icon)
        
        # Stocker les icônes pour les événements
        button._original_icon = QIcon(original_icon)
        button._glow_icon = QIcon(glow_icon)
        
        # Remplacer les événements enter/leave
        original_enter = button.enterEvent
        original_leave = button.leaveEvent
        
        def on_enter(event):
            button.setIcon(button._glow_icon)
            if original_enter:
                original_enter(event)
        
        def on_leave(event):
            button.setIcon(button._original_icon)
            if original_leave:
                original_leave(event)
        
        button.enterEvent = on_enter
        button.leaveEvent = on_leave
    
    def _get_glow_icon_path(self, original_path):
        """Génère le chemin de l'icône glow et vérifie si elle existe."""
        # Séparer le chemin et l'extension
        path_parts = original_path.rsplit('.', 1)
        if len(path_parts) != 2:
            return original_path  # Pas d'extension trouvée, retourner l'original
        
        base_path, extension = path_parts
        
        # Créer le chemin glow
        glow_path = f"{base_path}_glow.{extension}"
        
        # Vérifier si le fichier glow existe
        if os.path.exists(glow_path):
            return glow_path
        else:
            # Fichier glow n'existe pas, retourner l'original
            print(f"Glow icon not found: {glow_path}, using original: {original_path}")
            return original_path
    
    def _connect_action(self, button, action_name):
        """Connecte un bouton à une action définie dans core/actions."""
        try:
            actions_module = importlib.import_module("core.actions.title_bar_menu_action")
            action = getattr(actions_module, action_name)
            button.clicked.connect(action)
        except Exception as e:
            print(f"Error connecting action {action_name}: {e}")
            import traceback
            traceback.print_exc()