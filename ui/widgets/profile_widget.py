import platform
import sys
import psutil
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QGridLayout, QScrollArea
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class ProfileWidget(QWidget):
    """Widget to display system information"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Profile header
        header = QLabel("System Profile")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #ECEFF4;")
        layout.addWidget(header)
        
        # System information widget
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #3B4252; border-radius: 5px; padding: 15px;")
        info_layout = QGridLayout(info_frame)
        
        # Get system information
        self.system_info = self.get_system_info()
        
        # Display system information in a grid
        row = 0
        for category, items in self.system_info.items():
            # Category header
            category_label = QLabel(category)
            category_label.setFont(QFont("Arial", 12, QFont.Bold))
            category_label.setStyleSheet("color: #88C0D0;")
            info_layout.addWidget(category_label, row, 0, 1, 2)
            row += 1
            
            # Category items
            for key, value in items.items():
                key_label = QLabel(f"{key}:")
                key_label.setStyleSheet("color: #E5E9F0;")
                value_label = QLabel(str(value))
                value_label.setStyleSheet("color: #A3BE8C;")
                value_label.setWordWrap(True)
                
                info_layout.addWidget(key_label, row, 0)
                info_layout.addWidget(value_label, row, 1)
                row += 1
                
            # Add spacing between categories
            spacer = QLabel("")
            info_layout.addWidget(spacer, row, 0)
            row += 1
        
        # Create a scroll area for the system info
        scroll_area = QScrollArea()
        scroll_area.setWidget(info_frame)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        layout.addWidget(scroll_area)
        
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