import platform
import sys
import psutil
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QGridLayout, QScrollArea
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
import json
import os

# Import the CommandContextWidget
from ui.widgets.command_context_widget import CommandContextWidget

class ProfileWidget(QWidget):
    """Enhanced widget to display system information with command execution context selection"""
    
    context_updated = pyqtSignal(dict)  # Signal emitted when command context is updated
    
    def __init__(self):
        super().__init__()
        self.current_theme = "Nord Dark (Default)"
        self.current_font_size = "Medium (Default)"
        self.setup_ui()

    def get_system_info_dict(self):
        """Returns the system information as a dictionary for easy sharing with other components"""
        return self.system_info
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Profile header
        self.header = QLabel("System Profile")
        self.header.setFont(QFont("Arial", 16, QFont.Bold))
        self.header.setStyleSheet("color: #ECEFF4;")
        layout.addWidget(self.header)
        
        # Command Context Widget - New Addition
        self.command_context_widget = CommandContextWidget()
        # Connect the internal signal to our forwarding signal
        self.command_context_widget.context_changed.connect(self.forward_context_change)
        layout.addWidget(self.command_context_widget)
        
        # System information widget
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet("background-color: #3B4252; border-radius: 5px; padding: 15px;")
        self.info_layout = QGridLayout(self.info_frame)
        
        # Get system information
        self.system_info = self.get_system_info()
        
        # Display system information in a grid
        self.populate_system_info()
        
        # Create a scroll area for the system info
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.info_frame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        layout.addWidget(self.scroll_area)
    
    def forward_context_change(self, context_info):
        """Forward the command context change signal"""
        # Log for debugging
        print(f"ProfileWidget forwarding context update: {context_info['name']} - {context_info['path']}")
        # Forward the signal to listeners (like MainWindow and AIChatWidget)
        self.context_updated.emit(context_info)
    
    def get_command_context(self):
        """Get the current command execution context"""
        return self.command_context_widget.get_active_context()
    
    def populate_system_info(self):
        """Populate the grid with system information"""
        # Clear existing items
        while self.info_layout.count():
            item = self.info_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
        # Display system information in a grid
        row = 0
        for category, items in self.system_info.items():
            # Category header
            category_label = QLabel(category)
            category_label.setFont(QFont("Arial", 12, QFont.Bold))
            category_label.setStyleSheet("color: #88C0D0;")
            self.info_layout.addWidget(category_label, row, 0, 1, 2)
            row += 1
            
            # Category items
            for key, value in items.items():
                key_label = QLabel(f"{key}:")
                key_label.setStyleSheet("color: #E5E9F0;")
                value_label = QLabel(str(value))
                value_label.setStyleSheet("color: #A3BE8C;")
                value_label.setWordWrap(True)
                
                self.info_layout.addWidget(key_label, row, 0)
                self.info_layout.addWidget(value_label, row, 1)
                row += 1
                
            # Add spacing between categories
            spacer = QLabel("")
            self.info_layout.addWidget(spacer, row, 0)
            row += 1
        
    def get_system_info(self):
        """Gather detailed system information"""
        system_info = {
            "System": {
                "OS": f"{platform.system()} {platform.release()}",
                "Version": platform.version(),
                "Architecture": platform.machine(),
                "Processor": platform.processor(),
                "Computer Name": platform.node()
            },
            "Hardware": {
                "CPU Cores": psutil.cpu_count(logical=False),
                "CPU Threads": psutil.cpu_count(logical=True),
                "RAM": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
                "RAM Available": f"{round(psutil.virtual_memory().available / (1024**3), 2)} GB",
            },
            "Python Environment": {
                "Python Version": platform.python_version(),
                "Python Implementation": platform.python_implementation(),
                "Python Path": sys.executable
            }
        }
        
        # Add disk information
        disk_info = {}
        for disk in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(disk.mountpoint)
                disk_info[f"Disk {disk.device}"] = f"{round(usage.total / (1024**3), 2)} GB (Used: {usage.percent}%)"
            except:
                pass
                
        if disk_info:
            system_info["Storage"] = disk_info
            
        # Network information
        try:
            network_info = {}
            network_interfaces = psutil.net_if_addrs()
            for interface, addresses in network_interfaces.items():
                for address in addresses:
                    if address.family == 2:  # IPv4
                        network_info[interface] = address.address
                        
            if network_info:
                system_info["Network"] = network_info
        except:
            pass
            
        return system_info
    
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
        
        # Apply styles to header
        self.header.setStyleSheet(f"color: {colors['text']};")
        
        # Apply styles to info frame
        self.info_frame.setStyleSheet(f"background-color: {colors['secondary_bg']}; border-radius: 5px; padding: 15px;")
        
        # Apply styles to scroll area
        self.scroll_area.setStyleSheet(f"background-color: {colors['main_bg']}; border: none;")
        
        # Update command context widget theme
        self.command_context_widget.update_theme(theme_name)
        
        # Refresh system info display to apply new styles
        self.populate_system_info()
        
        # Update category headers and values
        for row in range(self.info_layout.rowCount()):
            widget_item = self.info_layout.itemAtPosition(row, 0)
            if widget_item and widget_item.widget():
                widget = widget_item.widget()
                if isinstance(widget, QLabel):
                    text = widget.text()
                    if text in self.system_info:
                        # This is a category header
                        widget.setStyleSheet(f"color: {colors['accent']};")
                    else:
                        # This is a key label
                        widget.setStyleSheet(f"color: {colors['text']};")
            
            value_item = self.info_layout.itemAtPosition(row, 1)
            if value_item and value_item.widget():
                value_widget = value_item.widget()
                if isinstance(value_widget, QLabel):
                    value_widget.setStyleSheet(f"color: {colors['success']};")
    
    def update_font_size(self, font_size_name):
        """Update the widget's font sizes"""
        self.current_font_size = font_size_name
        
        # Define font sizes for different elements
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
        
        sizes = font_sizes.get(font_size_name, font_sizes["Medium (Default)"])
        
        # Update header font
        self.header.setFont(QFont("Arial", sizes["header"], QFont.Bold))
        
        # Update command context widget font sizes
        self.command_context_widget.update_font_size(font_size_name)
        
        # Refresh system info display to apply new font sizes
        self.populate_system_info()
        
        # Update fonts in grid items
        for row in range(self.info_layout.rowCount()):
            widget_item = self.info_layout.itemAtPosition(row, 0)
            if widget_item and widget_item.widget():
                widget = widget_item.widget()
                if isinstance(widget, QLabel):
                    text = widget.text()
                    if text in self.system_info:
                        # This is a category header
                        widget.setFont(QFont("Arial", sizes["subheader"], QFont.Bold))
                    else:
                        # This is a key label
                        widget.setFont(QFont("Arial", sizes["normal"]))
            
            value_item = self.info_layout.itemAtPosition(row, 1)
            if value_item and value_item.widget():
                value_widget = value_item.widget()
                if isinstance(value_widget, QLabel):
                    value_widget.setFont(QFont("Arial", sizes["normal"]))