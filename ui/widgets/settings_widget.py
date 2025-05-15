import json
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QGridLayout, 
                          QGroupBox, QComboBox, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal

class SettingsWidget(QWidget):
    """Widget for application settings"""
    
    # Define signals for theme and font size changes
    theme_changed = pyqtSignal(str)
    font_size_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_settings()
        
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
    
    def get_config_file_path(self):
        """Get the path to the configuration file"""
        config_dir = os.path.join(os.path.expanduser("~"), ".rapture")
        # Create directory if it doesn't exist
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        return os.path.join(config_dir, "config.json")
    
    def load_settings(self):
        """Load application settings"""
        config_file = self.get_config_file_path()
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    
                    # Set theme
                    theme = config_data.get('theme', 'Nord Dark (Default)')
                    index = self.theme_combo.findText(theme)
                    if index >= 0:
                        self.theme_combo.setCurrentIndex(index)
                    
                    # Set font size
                    font_size = config_data.get('font_size', 'Medium (Default)')
                    index = self.font_combo.findText(font_size)
                    if index >= 0:
                        self.font_combo.setCurrentIndex(index)
                    
                    # Set API key
                    api_key = config_data.get('gemini_api_key', '')
                    if api_key:
                        self.gemini_api_input.setText('*' * 10)  # Mask the actual key
                        
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save application settings"""
        config_file = self.get_config_file_path()
        config_data = {}
        
        # Load existing config if it exists
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                config_data = {}
        
        # Get current settings
        theme = self.theme_combo.currentText()
        font_size = self.font_combo.currentText()
        api_key = self.gemini_api_input.text()
        
        # Update config data
        config_data['theme'] = theme
        config_data['font_size'] = font_size
        
        # Only update API key if it's not the masked placeholder
        if api_key and api_key != '*' * 10:
            config_data['gemini_api_key'] = api_key
        
        # Save to file
        try:
            with open(config_file, 'w') as f:
                json.dump(config_data, f)
            QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully!")
            
            # Emit signals for theme and font size changes
            self.theme_changed.emit(theme)
            self.font_size_changed.emit(font_size)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

    

def get_theme_stylesheet(theme_name):
        """Get the stylesheet for the specified theme"""
        stylesheets = {
            "Nord Dark (Default)": {
                "main_bg": "#2E3440",
                "secondary_bg": "#3B4252",
                "highlight_bg": "#4C566A",
                "accent": "#88C0D0",
                "text": "#ECEFF4",
                "secondary_text": "#D8DEE9",
                "success": "#A3BE8C",
                "warning": "#EBCB8B",
                "error": "#BF616A"
            },
            "Nord Light": {
                "main_bg": "#ECEFF4",
                "secondary_bg": "#E5E9F0",
                "highlight_bg": "#D8DEE9",
                "accent": "#5E81AC",
                "text": "#2E3440",
                "secondary_text": "#4C566A",
                "success": "#A3BE8C",
                "warning": "#EBCB8B",
                "error": "#BF616A"
            },
            "Dracula": {
                "main_bg": "#282a36",
                "secondary_bg": "#44475a",
                "highlight_bg": "#6272a4",
                "accent": "#8be9fd",
                "text": "#f8f8f2",
                "secondary_text": "#f8f8f2",
                "success": "#50fa7b",
                "warning": "#ffb86c",
                "error": "#ff5555"
            },
            "Solarized Dark": {
                "main_bg": "#002b36",
                "secondary_bg": "#073642",
                "highlight_bg": "#586e75",
                "accent": "#2aa198",
                "text": "#fdf6e3",
                "secondary_text": "#eee8d5",
                "success": "#859900",
                "warning": "#b58900",
                "error": "#dc322f"
            },
            "Solarized Light": {
                "main_bg": "#fdf6e3",
                "secondary_bg": "#eee8d5",
                "highlight_bg": "#93a1a1",
                "accent": "#2aa198",
                "text": "#002b36",
                "secondary_text": "#073642",
                "success": "#859900",
                "warning": "#b58900",
                "error": "#dc322f"
            }
        }
        
        # Get colors for the selected theme, fallback to Nord Dark
        colors = stylesheets.get(theme_name, stylesheets["Nord Dark (Default)"])
        
        # Create stylesheet
        return f"""
            QMainWindow, QWidget, QDialog {{
                background-color: {colors["main_bg"]};
                color: {colors["text"]};
            }}
            
            QFrame, QGroupBox {{
                background-color: {colors["secondary_bg"]};
                color: {colors["text"]};
            }}
            
            QLabel {{
                color: {colors["text"]};
                border: none;
            }}
            
            QTabWidget::pane {{
                border: none;
            }}
            
            QTabBar::tab {{
                background-color: {colors["secondary_bg"]};
                color: {colors["secondary_text"]};
                padding: 8px 20px;
                margin-right: 5px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {colors["highlight_bg"]};
                color: {colors["text"]};
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {colors["highlight_bg"]};
                opacity: 0.7;
            }}
            
            QPushButton {{
                background-color: {colors["accent"]};
                color: {colors["main_bg"]};
                border-radius: 5px;
                padding: 10px;
            }}
            
            QPushButton:hover {{
                background-color: {colors["highlight_bg"]};
            }}
            
            QLineEdit, QTextEdit, QComboBox {{
                background-color: {colors["main_bg"]};
                color: {colors["text"]};
                border-radius: 3px;
                padding: 5px;
                selection-background-color: {colors["highlight_bg"]};
            }}
            
            QTreeWidget {{
                background-color: {colors["main_bg"]};
                color: {colors["text"]};
                border: none;
            }}
            
            QTreeWidget::item:selected {{
                background-color: {colors["highlight_bg"]};
            }}
            
            QTreeWidget::item:hover {{
                background-color: {colors["secondary_bg"]};
            }}
        """


def get_font_size(font_size_name):
        """Get the font size based on the selected option"""
        font_sizes = {
            "Small": {
                "header": 14,
                "subheader": 12,
                "normal": 9,
                "small": 8
            },
            "Medium (Default)": {
                "header": 16,
                "subheader": 14,
                "normal": 10,
                "small": 9
            },
            "Large": {
                "header": 18,
                "subheader": 16,
                "normal": 12,
                "small": 10
            },
            "Extra Large": {
                "header": 20,
                "subheader": 18,
                "normal": 14,
                "small": 12
            }
        }
        
        return font_sizes.get(font_size_name, font_sizes["Medium (Default)"])