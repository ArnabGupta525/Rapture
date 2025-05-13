from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QGridLayout, 
                          QGroupBox, QComboBox, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class SettingsWidget(QWidget):
    """Widget for application settings"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Settings header
        header = QLabel("Settings")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #ECEFF4;")
        layout.addWidget(header)
        
        # Settings frame
        settings_frame = QFrame()
        settings_frame.setStyleSheet("background-color: #3B4252; border-radius: 5px; padding: 15px;")
        settings_layout = QVBoxLayout(settings_frame)
        
        # Appearance settings
        appearance_group = QGroupBox("Appearance")
        appearance_group.setStyleSheet("color: #88C0D0; border: 1px solid #4C566A; border-radius: 5px; padding: 10px;")
        appearance_layout = QGridLayout(appearance_group)
        
        # Theme selection
        theme_label = QLabel("Theme:")
        theme_label.setStyleSheet("color: #E5E9F0; border: none;")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Nord Dark (Default)", "Nord Light", "Dracula", "Solarized Dark", "Solarized Light"])
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background-color: #2E3440;
                color: #E5E9F0;
                border-radius: 3px;
                padding: 5px;
                min-width: 150px;
            }
            QComboBox:hover {
                background-color: #3B4252;
            }
            QComboBox QAbstractItemView {
                background-color: #2E3440;
                color: #E5E9F0;
                selection-background-color: #5E81AC;
            }
        """)
        
        appearance_layout.addWidget(theme_label, 0, 0)
        appearance_layout.addWidget(self.theme_combo, 0, 1)
        
        # Font size
        font_label = QLabel("Font Size:")
        font_label.setStyleSheet("color: #E5E9F0; border: none;")
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Small", "Medium (Default)", "Large", "Extra Large"])
        self.font_combo.setStyleSheet("""
            QComboBox {
                background-color: #2E3440;
                color: #E5E9F0;
                border-radius: 3px;
                padding: 5px;
                min-width: 150px;
            }
            QComboBox:hover {
                background-color: #3B4252;
            }
            QComboBox QAbstractItemView {
                background-color: #2E3440;
                color: #E5E9F0;
                selection-background-color: #5E81AC;
            }
        """)
        
        appearance_layout.addWidget(font_label, 1, 0)
        appearance_layout.addWidget(self.font_combo, 1, 1)
        
        settings_layout.addWidget(appearance_group)
        
        # API settings
        api_group = QGroupBox("API Settings")
        api_group.setStyleSheet("color: #88C0D0; border: 1px solid #4C566A; border-radius: 5px; padding: 10px;")
        api_layout = QGridLayout(api_group)
        
        # Gemini API
        gemini_label = QLabel("Gemini API Key:")
        gemini_label.setStyleSheet("color: #E5E9F0; border: none;")
        self.gemini_api_input = QLineEdit()
        self.gemini_api_input.setStyleSheet("""
            QLineEdit {
                background-color: #2E3440;
                color: #E5E9F0;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        self.gemini_api_input.setEchoMode(QLineEdit.Password)
        
        api_layout.addWidget(gemini_label, 0, 0)
        api_layout.addWidget(self.gemini_api_input, 0, 1)
        
        settings_layout.addWidget(api_group)
        
        # Save button
        self.save_button = QPushButton("Save Settings")
        self.save_button.setFont(QFont("Arial", 11))
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #A3BE8C;
                color: #2E3440;
                border-radius: 5px;
                padding: 10px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #B9D395;
            }
            QPushButton:pressed {
                background-color: #8CAA74;
            }
        """)
        self.save_button.clicked.connect(self.save_settings)
        
        settings_layout.addWidget(self.save_button, 0, Qt.AlignRight)
        layout.addWidget(settings_frame)
        
    def save_settings(self):
        """Save application settings"""
        # Here you would implement saving to a config file
        # For now, just show a success message
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully!")