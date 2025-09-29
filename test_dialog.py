#!/usr/bin/env python3
"""Test simple de la boîte de dialogue."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QLabel, QMessageBox

class TestDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Dialog")
        self.setModal(True)
        self.resize(400, 200)

        layout = QVBoxLayout(self)

        label = QLabel("Test de dialogue simple")
        layout.addWidget(label)

        self.test_button = QPushButton("Test Bouton")
        self.test_button.clicked.connect(self.test_click)
        layout.addWidget(self.test_button)

        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

    def test_click(self):
        QMessageBox.information(self, "Test", "Bouton cliqué avec succès!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = TestDialog()
    dialog.show()
    sys.exit(app.exec())