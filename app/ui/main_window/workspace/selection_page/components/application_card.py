# selection_page/components/application_card.py
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QFrame, QComboBox
from PySide6.QtCore import Qt, Signal

class ApplicationCard(QFrame):
    """Widget carte pour une application."""
    toggled = Signal(str, bool)  # Signal émis quand la case est cochée/décochée
    version_changed = Signal(str, str)  # Signal émis quand la version change (app_name, version)

    def __init__(self, application):
        super().__init__()
        self.application = application
        self.selected_version = None
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
        if self.application.has_versions:
            # Afficher les versions disponibles
            methods_text = f"{len(self.application.versions)} versions disponibles"
        else:
            methods_text = ", ".join([method.type for method in self.application.methods])

        methods_label = QLabel(f"Installation: {methods_text}")
        methods_label.setProperty("class", "AppMethodsLabel")  # Classe CSS pour le style
        layout.addWidget(methods_label)

        # Menu déroulant des versions (si applicable)
        if self.application.has_versions and self.application.versions:
            version_layout = QHBoxLayout()
            version_label = QLabel("Version:")
            version_label.setProperty("class", "VersionLabel")
            version_layout.addWidget(version_label)

            self.version_combo = QComboBox()
            self.version_combo.setProperty("class", "VersionCombo")

            # Ajouter les versions au combo
            for version in self.application.versions:
                self.version_combo.addItem(version.name, version.version)

            # Sélectionner la version par défaut basée sur default_version_index
            if self.application.versions:
                default_version = self.application.get_default_version()
                if default_version:
                    self.selected_version = default_version
                    # Trouver l'index de cette version dans la liste
                    default_index = 0
                    for i, version in enumerate(self.application.versions):
                        if version.version == default_version.version:
                            default_index = i
                            break
                    self.version_combo.setCurrentIndex(default_index)
                else:
                    # Fallback sur la première version
                    self.selected_version = self.application.versions[0]
                    self.version_combo.setCurrentIndex(0)

            self.version_combo.currentTextChanged.connect(self.on_version_changed)
            version_layout.addWidget(self.version_combo)
            version_layout.addStretch()
            layout.addLayout(version_layout)
    
    def on_toggled(self, state):
        """Gestionnaire du changement d'état de la checkbox."""
        is_checked = state == Qt.Checked
        self.toggled.emit(self.application.name, is_checked)
    
    def is_selected(self):
        """Retourne True si l'application est sélectionnée."""
        return self.checkbox.isChecked()
    
    def on_version_changed(self, version_text):
        """Gestionnaire du changement de version."""
        # Trouver la version correspondante
        for version in self.application.versions:
            if version.name == version_text:
                self.selected_version = version
                break

        # Émettre le signal de changement de version
        if self.selected_version:
            self.version_changed.emit(self.application.name, self.selected_version.version)

    def get_selected_version(self):
        """Retourne la version sélectionnée."""
        if self.application.has_versions:
            return self.selected_version
        return None

    def get_methods_for_installation(self):
        """Retourne les méthodes d'installation pour la version sélectionnée ou l'application."""
        if self.application.has_versions and self.selected_version:
            return self.selected_version.methods
        return self.application.methods

    def set_selected(self, selected):
        """Définit l'état de sélection de l'application."""
        # Bloquer temporairement les signaux pour éviter la récursion infinie
        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(selected)
        self.checkbox.blockSignals(False)

        # Émettre manuellement le signal toggled pour informer les parents
        self.toggled.emit(self.application.name, selected)