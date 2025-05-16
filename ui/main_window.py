import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QTabWidget, QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from ui.widgets.profile_widget import ProfileWidget
from ui.widgets.dev_tools_widget import DeveloperToolsWidget
from ui.widgets.ai_chat_widget import AIChatWidget
from ui.widgets.settings_widget import SettingsWidget, get_theme_stylesheet, get_font_size

class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rapture - Developer's Assistant Tool")
        self.setMinimumSize(1000, 700)
        
        # Initialize variables to store current theme and font size
        self.current_theme = "Nord Dark (Default)"
        self.current_font_size = "Medium (Default)"
        
        self.setup_ui()
        self.load_settings()
        self.apply_theme(self.current_theme)
        self.apply_font_size(self.current_font_size)
        
    def setup_ui(self):
        # Create central widget
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create header
        self.header_frame = QFrame()
        self.header_frame.setMaximumHeight(70)
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # App logo/title
        logo_layout = QHBoxLayout()
        self.app_title = QLabel("Rapture")
        self.app_title.setFont(QFont("Arial", 18, QFont.Bold))
        
        self.app_subtitle = QLabel("Developer's Assistant Tool")
        self.app_subtitle.setFont(QFont("Arial", 10))
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(self.app_title)
        title_layout.addWidget(self.app_subtitle)
        logo_layout.addLayout(title_layout)
        header_layout.addLayout(logo_layout)
        
        # Add spacer
        header_layout.addStretch()
        main_layout.addWidget(self.header_frame)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.profile_tab = ProfileWidget()
        self.dev_tools_tab = DeveloperToolsWidget()
        self.ai_chat_tab = AIChatWidget()
        self.settings_tab = SettingsWidget()
        
        # Connect ProfileWidget's context_updated signal to AIChatWidget's update_command_context method
        self.profile_tab.context_updated.connect(self.ai_chat_tab.update_command_context)
        
        # Initialize AI chat with the current context from ProfileWidget
        initial_context = self.profile_tab.get_command_context()
        self.ai_chat_tab.update_command_context(initial_context)
        
        # Connect settings signals to theme and font size changes
        self.settings_tab.theme_changed.connect(self.apply_theme)
        self.settings_tab.font_size_changed.connect(self.apply_font_size)
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.profile_tab, "System Profile")
        self.tab_widget.addTab(self.dev_tools_tab, "Developer Tools")
        self.tab_widget.addTab(self.ai_chat_tab, "AI Assistant")
        self.tab_widget.addTab(self.settings_tab, "Settings")
        main_layout.addWidget(self.tab_widget)
        
        # Connect widgets to share data
        self.connect_widgets()
        
        # Set central widget
        self.setCentralWidget(central_widget)

    def connect_widgets(self):
        """Connect widgets to share data between them"""
        # Pass system information from profile widget to AI chat widget
        system_info = self.profile_tab.get_system_info_dict()
        self.ai_chat_tab.update_system_context_with_system_info(system_info)
        
        # Add this line to directly connect the profile widget's context_updated signal
        # to the AI chat widget's update_command_context method
        self.profile_tab.context_updated.connect(self.ai_chat_tab.update_command_context)
        # Debug message to confirm connection
        print("Connected widgets and shared system information")
    
    def load_settings(self):
        """Load application settings"""
        try:
            import json
            import os
            
            config_dir = os.path.join(os.path.expanduser("~"), ".rapture")
            config_file = os.path.join(config_dir, "config.json")
            
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    self.current_theme = config_data.get('theme', "Nord Dark (Default)")
                    self.current_font_size = config_data.get('font_size', "Medium (Default)")
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def apply_theme(self, theme_name):
        """Apply the selected theme to the application"""
        self.current_theme = theme_name
        stylesheet = get_theme_stylesheet(theme_name)
        self.setStyleSheet(stylesheet)
        
        # Apply specific theme colors to widgets
        theme_colors = {
            "Nord Dark (Default)": {
                "header_bg": "#3B4252",
                "accent": "#88C0D0",
                "secondary_text": "#D8DEE9"
            },
            "Nord Light": {
                "header_bg": "#E5E9F0",
                "accent": "#5E81AC",
                "secondary_text": "#4C566A"
            },
            "Dracula": {
                "header_bg": "#44475a",
                "accent": "#8be9fd",
                "secondary_text": "#f8f8f2"
            },
            "Solarized Dark": {
                "header_bg": "#073642",
                "accent": "#2aa198",
                "secondary_text": "#eee8d5"
            },
            "Solarized Light": {
                "header_bg": "#eee8d5",
                "accent": "#2aa198",
                "secondary_text": "#073642"
            }
        }
        
        colors = theme_colors.get(theme_name, theme_colors["Nord Dark (Default)"])
        
        # Apply header styles
        self.header_frame.setStyleSheet(f"background-color: {colors['header_bg']};")
        self.app_title.setStyleSheet(f"color: {colors['accent']};")
        self.app_subtitle.setStyleSheet(f"color: {colors['secondary_text']};")
        
        # Notify all widgets of theme change
        for widget in [self.profile_tab, self.dev_tools_tab, self.ai_chat_tab, self.settings_tab]:
            if hasattr(widget, 'update_theme'):
                widget.update_theme(theme_name)
    
    def apply_font_size(self, font_size_name):
        """Apply the selected font size to the application"""
        self.current_font_size = font_size_name
        font_sizes = get_font_size(font_size_name)
        
        # Apply font sizes to main UI elements
        app_font = QApplication.font()
        app_font.setPointSize(font_sizes["normal"])
        QApplication.setFont(app_font)
        
        # Update header fonts
        self.app_title.setFont(QFont("Arial", font_sizes["header"], QFont.Bold))
        self.app_subtitle.setFont(QFont("Arial", font_sizes["small"]))
        
        # Notify all widgets of font size change
        for widget in [self.profile_tab, self.dev_tools_tab, self.ai_chat_tab, self.settings_tab]:
            if hasattr(widget, 'update_font_size'):
                widget.update_font_size(font_size_name)