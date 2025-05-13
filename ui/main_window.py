from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QTabWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from ui.widgets.profile_widget import ProfileWidget
from ui.widgets.dev_tools_widget import DeveloperToolsWidget
from ui.widgets.ai_chat_widget import AIChatWidget
from ui.widgets.settings_widget import SettingsWidget

class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DevAssist - Developer's Assistant Tool")
        self.setMinimumSize(1000, 700)
        self.setup_ui()
        
    def setup_ui(self):
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2E3440;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #3B4252;")
        header_frame.setMaximumHeight(70)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # App logo/title
        logo_layout = QHBoxLayout()
        
        app_title = QLabel("DevAssist")
        app_title.setFont(QFont("Arial", 18, QFont.Bold))
        app_title.setStyleSheet("color: #88C0D0;")
        
        app_subtitle = QLabel("Developer's Assistant Tool")
        app_subtitle.setFont(QFont("Arial", 10))
        app_subtitle.setStyleSheet("color: #D8DEE9;")
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(app_title)
        title_layout.addWidget(app_subtitle)
        
        logo_layout.addLayout(title_layout)
        header_layout.addLayout(logo_layout)
        
        # Add spacer
        header_layout.addStretch()
        
        main_layout.addWidget(header_frame)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget {
                background-color: #2E3440;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background-color: #3B4252;
                color: #D8DEE9;
                padding: 8px 20px;
                margin-right: 5px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #4C566A;
                color: #ECEFF4;
            }
            QTabBar::tab:hover:!selected {
                background-color: #434C5E;
            }
        """)
        
        # Create tabs
        self.profile_tab = ProfileWidget()
        self.dev_tools_tab = DeveloperToolsWidget()
        self.ai_chat_tab = AIChatWidget()
        self.settings_tab = SettingsWidget()
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.profile_tab, "System Profile")
        self.tab_widget.addTab(self.dev_tools_tab, "Developer Tools")
        self.tab_widget.addTab(self.ai_chat_tab, "AI Assistant")
        self.tab_widget.addTab(self.settings_tab, "Settings")
        
        main_layout.addWidget(self.tab_widget)
        
        # Set central widget
        self.setCentralWidget(central_widget)