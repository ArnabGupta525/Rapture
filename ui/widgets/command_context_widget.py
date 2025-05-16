import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, 
                            QComboBox, QPushButton, QFileDialog, QLineEdit)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal

class CommandContextWidget(QWidget):
    """Widget to select where commands should be executed"""
    
    context_changed = pyqtSignal(dict)  # Signal emitted when context is updated
    
    def __init__(self):
        super().__init__()
        self.current_theme = "Nord Dark (Default)"
        self.current_font_size = "Medium (Default)"
        
        # Define execution contexts with validated paths
        self.execution_contexts = {
            "Current Directory": {"path": os.getcwd(), "description": "Execute commands in the directory where the application was launched"},
            "System Level": {"path": "/" if os.path.exists("/") else "C:\\" if os.path.exists("C:\\") else os.getcwd(), 
                           "description": "Execute commands at the system root level (requires appropriate permissions)"},
            "User Home": {"path": os.path.expanduser("~"), "description": "Execute commands in your home directory"},
            "Custom Location": {"path": "", "description": "Execute commands in a custom directory"}
        }
        self.active_context = "Current Directory"
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        self.header = QLabel("Command Execution Context")
        self.header.setFont(QFont("Arial", 12, QFont.Bold))
        self.header.setStyleSheet("color: #88C0D0;")
        layout.addWidget(self.header)
        
        # Description
        self.description = QLabel("Select where commands should be executed in the system.")
        self.description.setStyleSheet("color: #D8DEE9;")
        self.description.setWordWrap(True)
        layout.addWidget(self.description)
        
        # Context selection frame
        self.context_frame = QFrame()
        self.context_frame.setStyleSheet("background-color: #3B4252; border-radius: 5px; padding: 10px;")
        context_layout = QVBoxLayout(self.context_frame)
        
        # Context dropdown
        dropdown_layout = QHBoxLayout()
        self.context_label = QLabel("Execution Context:")
        self.context_label.setStyleSheet("color: #E5E9F0;")
        self.context_dropdown = QComboBox()
        self.context_dropdown.addItems(list(self.execution_contexts.keys()))
        self.context_dropdown.setStyleSheet("""
            QComboBox {
                background-color: #2E3440;
                color: #E5E9F0;
                border-radius: 3px;
                padding: 5px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #3B4252;
                color: #E5E9F0;
                selection-background-color: #4C566A;
            }
        """)
        self.context_dropdown.currentTextChanged.connect(self.on_context_changed)
        
        dropdown_layout.addWidget(self.context_label)
        dropdown_layout.addWidget(self.context_dropdown, 1)
        context_layout.addLayout(dropdown_layout)
        
        # Custom path selection (initially hidden)
        self.custom_path_container = QWidget()  # Container widget for the custom path inputs
        self.custom_path_layout = QHBoxLayout(self.custom_path_container)
        self.custom_path_layout.setContentsMargins(0, 0, 0, 0)
        
        self.path_label = QLabel("Custom Path:")
        self.path_label.setStyleSheet("color: #E5E9F0;")
        self.path_input = QLineEdit()
        self.path_input.setStyleSheet("""
            QLineEdit {
                background-color: #2E3440;
                color: #E5E9F0;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        self.path_input.textChanged.connect(self.on_custom_path_changed)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.setStyleSheet("""
            QPushButton {
                background-color: #5E81AC;
                color: #ECEFF4;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #81A1C1;
            }
        """)
        self.browse_button.clicked.connect(self.browse_directory)
        
        self.custom_path_layout.addWidget(self.path_label)
        self.custom_path_layout.addWidget(self.path_input, 1)
        self.custom_path_layout.addWidget(self.browse_button)
        
        context_layout.addWidget(self.custom_path_container)
        self.custom_path_container.setVisible(False)  # Initially hidden
        
        # Context description
        self.context_description = QLabel(self.execution_contexts["Current Directory"]["description"])
        self.context_description.setStyleSheet("color: #88C0D0; font-style: italic;")
        self.context_description.setWordWrap(True)
        context_layout.addWidget(self.context_description)
        
        # Current path display
        self.path_display_label = QLabel("Active Directory:")
        self.path_display_label.setStyleSheet("color: #E5E9F0; margin-top: 10px;")
        self.path_display = QLabel(self.execution_contexts["Current Directory"]["path"])
        self.path_display.setStyleSheet("color: #A3BE8C; font-weight: bold;")
        self.path_display.setWordWrap(True)
        context_layout.addWidget(self.path_display_label)
        context_layout.addWidget(self.path_display)
        
        layout.addWidget(self.context_frame)
        
    def on_context_changed(self, context_name):
        """Handle context selection change"""
        self.active_context = context_name
        
        # Show/hide custom path input as needed
        self.custom_path_container.setVisible(context_name == "Custom Location")
        
        # Update description and path display
        self.context_description.setText(self.execution_contexts[context_name]["description"])
        
        # Update path display (except for custom path which is handled separately)
        if context_name != "Custom Location":
            self.path_display.setText(self.execution_contexts[context_name]["path"])
            
        # Emit the context changed signal with the new context info
        context_info = {
            "name": context_name,
            "path": self.execution_contexts[context_name]["path"]
        }
        
        # Debug output
        print(f"Context changed to: {context_name} - {context_info['path']}")
        
        self.context_changed.emit(context_info)
        
    def on_custom_path_changed(self, path):
        """Handle custom path text changes"""
        if self.active_context == "Custom Location" and path:
            self.execution_contexts["Custom Location"]["path"] = path
            self.path_display.setText(path)
            
            # Emit context changed signal
            context_info = {
                "name": "Custom Location",
                "path": path
            }
            self.context_changed.emit(context_info)
    
    def browse_directory(self):
        """Open a file dialog to select a custom directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory", os.path.expanduser("~"), 
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if directory:
            self.path_input.setText(directory)
            self.execution_contexts["Custom Location"]["path"] = directory
            self.path_display.setText(directory)
            
            # Emit context changed signal
            context_info = {
                "name": "Custom Location",
                "path": directory
            }
            self.context_changed.emit(context_info)
    
    def get_active_context(self):
        """Return the currently active execution context"""
        context_name = self.active_context
        context_path = self.execution_contexts[context_name]["path"]
        
        # For custom location, get the path from the input field
        if context_name == "Custom Location":
            context_path = self.path_input.text() or context_path
            
        return {
            "name": context_name,
            "path": context_path
        }
    
    def update_theme(self, theme_name):
        """Update the widget's theme to match the application theme"""
        self.current_theme = theme_name
        
        # Get theme colors
        themes = {
            "Nord Dark (Default)": {
                "main_bg": "#2E3440",
                "secondary_bg": "#3B4252",
                "highlight_bg": "#4C566A",
                "accent": "#88C0D0",
                "text": "#ECEFF4",
                "secondary_text": "#D8DEE9",
                "success": "#A3BE8C"
            },
            "Nord Light": {
                "main_bg": "#ECEFF4",
                "secondary_bg": "#E5E9F0",
                "highlight_bg": "#D8DEE9",
                "accent": "#5E81AC",
                "text": "#2E3440",
                "secondary_text": "#4C566A",
                "success": "#A3BE8C"
            },
            "Dracula": {
                "main_bg": "#282a36",
                "secondary_bg": "#44475a",
                "highlight_bg": "#6272a4",
                "accent": "#8be9fd",
                "text": "#f8f8f2",
                "secondary_text": "#f8f8f2",
                "success": "#50fa7b"
            },
            "Solarized Dark": {
                "main_bg": "#002b36",
                "secondary_bg": "#073642",
                "highlight_bg": "#586e75",
                "accent": "#2aa198",
                "text": "#fdf6e3",
                "secondary_text": "#eee8d5",
                "success": "#859900"
            },
            "Solarized Light": {
                "main_bg": "#fdf6e3",
                "secondary_bg": "#eee8d5",
                "highlight_bg": "#93a1a1",
                "accent": "#2aa198",
                "text": "#002b36",
                "secondary_text": "#073642",
                "success": "#859900"
            }
        }
        
        colors = themes.get(theme_name, themes["Nord Dark (Default)"])
        
        # Update header and description styles
        self.header.setStyleSheet(f"color: {colors['accent']};")
        self.description.setStyleSheet(f"color: {colors['secondary_text']};")
        
        # Update context frame style
        self.context_frame.setStyleSheet(f"background-color: {colors['secondary_bg']}; border-radius: 5px; padding: 10px;")
        
        # Update labels
        self.context_label.setStyleSheet(f"color: {colors['text']};")
        self.path_label.setStyleSheet(f"color: {colors['text']};")
        self.path_display_label.setStyleSheet(f"color: {colors['text']}; margin-top: 10px;")
        self.path_display.setStyleSheet(f"color: {colors['success']}; font-weight: bold;")
        self.context_description.setStyleSheet(f"color: {colors['accent']}; font-style: italic;")
        
        # Update input styles
        self.context_dropdown.setStyleSheet(f"""
            QComboBox {{
                background-color: {colors['main_bg']};
                color: {colors['text']};
                border-radius: 3px;
                padding: 5px;
                min-width: 150px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {colors['secondary_bg']};
                color: {colors['text']};
                selection-background-color: {colors['highlight_bg']};
            }}
        """)
        
        self.path_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {colors['main_bg']};
                color: {colors['text']};
                border-radius: 3px;
                padding: 5px;
            }}
        """)
        
        self.browse_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['highlight_bg']};
                color: {colors['text']};
                border-radius: 3px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {colors['accent']};
            }}
        """)
        
    def update_font_size(self, font_size_name):
        """Update the widget's font sizes"""
        self.current_font_size = font_size_name
        
        # Define font sizes for different elements
        font_sizes = {
            "Small": {
                "header": 10,
                "normal": 8,
                "small": 7
            },
            "Medium (Default)": {
                "header": 12,
                "normal": 10,
                "small": 9
            },
            "Large": {
                "header": 14,
                "normal": 12,
                "small": 11
            },
            "Extra Large": {
                "header": 16,
                "normal": 14,
                "small": 12
            }
        }
        
        sizes = font_sizes.get(font_size_name, font_sizes["Medium (Default)"])
        
        # Update fonts
        self.header.setFont(QFont("Arial", sizes["header"], QFont.Bold))
        self.description.setFont(QFont("Arial", sizes["normal"]))
        self.context_label.setFont(QFont("Arial", sizes["normal"]))
        self.path_label.setFont(QFont("Arial", sizes["normal"]))
        self.context_dropdown.setFont(QFont("Arial", sizes["normal"]))
        self.path_input.setFont(QFont("Arial", sizes["normal"]))
        self.browse_button.setFont(QFont("Arial", sizes["normal"]))
        self.context_description.setFont(QFont("Arial", sizes["small"]))
        self.path_display_label.setFont(QFont("Arial", sizes["normal"]))
        self.path_display.setFont(QFont("Arial", sizes["normal"], QFont.Bold))