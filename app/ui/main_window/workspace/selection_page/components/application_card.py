# selection_page/components/application_card.py
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QFrame
from PySide6.QtCore import Qt, Signal

class ApplicationCard(QFrame):
    """Widget carte pour une application."""
    toggled = Signal(str, bool)  # Signal émis quand la case est cochée/décochée
    
    def __init__(self, application):
        super().__init__()
        self.application = application
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface de la carte."""
        self.setFrameStyle(QFrame.Box)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # Checkbox et nom de l'application
        header_layout = QHBoxLayout()
        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(self.on_toggled)
        header_layout.addWidget(self.checkbox)
        
        name_label = QLabel(self.application.name)
        name_label.setProperty("class", "AppNameLabel")  # Classe CSS pour le style
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Description
        desc_label = QLabel(self.application.description)
        desc_label.setWordWrap(True)
        desc_label.setProperty("class", "AppDescLabel")  # Classe CSS pour le style
        layout.addWidget(desc_label)
        
        # Catégorie
        category_label = QLabel(f"Catégorie: {self.application.category}")
        category_label.setProperty("class", "AppCategoryLabel")  # Classe CSS pour le style
        layout.addWidget(category_label)
        
        # Méthodes d'installation disponibles
        methods_text = ", ".join([method.type for method in self.application.methods])
        methods_label = QLabel(f"Installation: {methods_text}")
        methods_label.setProperty("class", "AppMethodsLabel")  # Classe CSS pour le style
        layout.addWidget(methods_label)
    
    def on_toggled(self, state):
        """Gestionnaire du changement d'état de la checkbox."""
        is_checked = state == Qt.Checked
        self.toggled.emit(self.application.name, is_checked)
    
    def is_selected(self):
        """Retourne True si l'application est sélectionnée."""
        return self.checkbox.isChecked()
    
    def set_selected(self, selected):
        """Définit l'état de sélection de l'application."""
        # Bloquer temporairement les signaux pour éviter la récursion infinie
        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(selected)
        self.checkbox.blockSignals(False)
        
        # Émettre manuellement le signal toggled pour informer les parents
        self.toggled.emit(self.application.name, selected)