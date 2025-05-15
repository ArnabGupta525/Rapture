import platform
import subprocess
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QSplitter, QTreeWidget, QTreeWidgetItem, 
                           QLabel, QFrame, QHBoxLayout, QGroupBox, QLineEdit, QPushButton, 
                           QTextEdit, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from utils.command_worker import CommandWorker

class DeveloperToolsWidget(QWidget):
    """Widget containing developer tools and commands"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.command_workers = []
        self.current_theme = "Nord Dark (Default)"
        self.current_font_size = "Medium (Default)"
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create splitter for tree and command area
        splitter = QSplitter(Qt.Horizontal)
        
        # Create tree widget for commands
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                background-color: #2E3440;
                border: none;
                outline: none;
                color: #E5E9F0;
            }
            QTreeWidget::item {
                padding: 5px;
                border-radius: 2px;
            }
            QTreeWidget::item:selected {
                background-color: #5E81AC;
            }
            QTreeWidget::item:hover {
                background-color: #4C566A;
            }
        """)
        
        # Populate the tree with developer domains
        self.populate_developer_tree()
        
        # Create command execution area
        command_widget = QWidget()
        command_layout = QVBoxLayout(command_widget)
        command_layout.setContentsMargins(20, 20, 20, 20)
        command_layout.setSpacing(15)
        
        # Command header
        self.command_header = QLabel("Select a command from the tree")
        self.command_header.setFont(QFont("Arial", 14, QFont.Bold))
        self.command_header.setStyleSheet("color: #ECEFF4;")
        command_layout.addWidget(self.command_header)
        
        # Command description
        self.command_description = QLabel("")
        self.command_description.setWordWrap(True)
        self.command_description.setStyleSheet("color: #D8DEE9;")
        command_layout.addWidget(self.command_description)
        
        # Command execution frame
        execution_frame = QFrame()
        execution_frame.setStyleSheet("background-color: #3B4252; border-radius: 5px; padding: 15px;")
        execution_layout = QVBoxLayout(execution_frame)
        
        # Command to execute
        command_box = QGroupBox("Command to Execute")
        command_box.setStyleSheet("color: #88C0D0; border: none;")
        command_box_layout = QVBoxLayout(command_box)
        
        self.command_text = QLineEdit()
        self.command_text.setStyleSheet("""
            QLineEdit {
                background-color: #2E3440;
                color: #A3BE8C;
                border-radius: 3px;
                padding: 8px;
                selection-background-color: #5E81AC;
            }
        """)
        self.command_text.setReadOnly(True)
        command_box_layout.addWidget(self.command_text)
        
        execution_layout.addWidget(command_box)
        
        # Command buttons
        buttons_layout = QHBoxLayout()
        
        self.execute_button = QPushButton("Execute Command")
        self.execute_button.setFont(QFont("Arial", 11))
        self.execute_button.setCursor(Qt.PointingHandCursor)
        self.execute_button.setStyleSheet("""
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
        self.execute_button.clicked.connect(self.execute_command)
        
        self.terminal_button = QPushButton("Open in Terminal")
        self.terminal_button.setFont(QFont("Arial", 11))
        self.terminal_button.setCursor(Qt.PointingHandCursor)
        self.terminal_button.setStyleSheet("""
            QPushButton {
                background-color: #5E81AC;
                color: white;
                border-radius: 5px;
                padding: 10px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #81A1C1;
            }
            QPushButton:pressed {
                background-color: #4C566A;
            }
        """)
        self.terminal_button.clicked.connect(self.open_in_terminal)
        
        buttons_layout.addWidget(self.execute_button)
        buttons_layout.addWidget(self.terminal_button)
        execution_layout.addLayout(buttons_layout)
        
        # Result output
        result_box = QGroupBox("Command Output")
        result_box.setStyleSheet("color: #88C0D0; border: none;")
        result_box_layout = QVBoxLayout(result_box)
        
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setFont(QFont("Consolas", 10))
        self.result_output.setStyleSheet("""
            QTextEdit {
                background-color: #2E3440;
                color: #D8DEE9;
                border-radius: 3px;
                selection-background-color: #5E81AC;
            }
        """)
        self.result_output.setMinimumHeight(200)
        result_box_layout.addWidget(self.result_output)
        
        execution_layout.addWidget(result_box)
        command_layout.addWidget(execution_frame)
        
        # Add widgets to splitter
        splitter.addWidget(self.tree_widget)
        splitter.addWidget(command_widget)
        splitter.setSizes([200, 600])  # Set initial sizes
        
        layout.addWidget(splitter)
        
        # Connect tree item selection signal
        self.tree_widget.itemSelectionChanged.connect(self.on_tree_selection_changed)
        
        # Initially disable the buttons
        self.execute_button.setEnabled(False)
        self.terminal_button.setEnabled(False)
        
    def populate_developer_tree(self):
        """Populate the tree with developer domains and commands"""
        # Load commands from a JSON structure
        self.dev_commands = {
            "Web Development": {
                "Node.js": [
                    {"name": "Install Node.js", 
                     "command": self._get_os_specific_command("node -v"),
                     "description": "Check if Node.js is installed or install it if not available."},
                    {"name": "Create React App", 
                     "command": "npx create-react-app my-app",
                     "description": "Create a new React application with the name 'my-app'."},
                    {"name": "Install Express", 
                     "command": "npm install express",
                     "description": "Install Express.js framework for Node.js."},
                    {"name": "Check NPM Version", 
                     "command": "npm -v",
                     "description": "Display the version of NPM package manager."}
                ],
                "Python Web": [
                    {"name": "Install Django", 
                     "command": "pip install django",
                     "description": "Install Django web framework for Python."},
                    {"name": "Install Flask", 
                     "command": "pip install flask",
                     "description": "Install Flask micro web framework for Python."},
                    {"name": "Create Django Project", 
                     "command": "django-admin startproject myproject",
                     "description": "Create a new Django project named 'myproject'."}
                ],
                "PHP": [
                    {"name": "Check PHP Version", 
                     "command": self._get_os_specific_command("php -v"),
                     "description": "Check the installed PHP version."},
                    {"name": "Install Composer", 
                     "command": self._get_os_specific_command("composer --version"),
                     "description": "Check if Composer is installed or install it if not available."},
                    {"name": "Create Laravel Project", 
                     "command": "composer create-project laravel/laravel my-project",
                     "description": "Create a new Laravel project using Composer."}
                ]
            },
            "Mobile Development": {
                "React Native": [
                    {"name": "Install React Native CLI", 
                     "command": "npm install -g react-native-cli",
                     "description": "Install React Native command line interface globally."},
                    {"name": "Create React Native App", 
                     "command": "npx react-native init MyApp",
                     "description": "Initialize a new React Native project named 'MyApp'."},
                    {"name": "Install Expo CLI", 
                     "command": "npm install -g expo-cli",
                     "description": "Install Expo CLI globally for React Native development."},
                    {"name": "Create Expo App", 
                     "command": "npx create-expo-app my-expo-app",
                     "description": "Create a new Expo project named 'my-expo-app'."}
                ],
                "Flutter": [
                    {"name": "Check Flutter", 
                     "command": self._get_os_specific_command("flutter --version"),
                     "description": "Check if Flutter is installed and display its version."},
                    {"name": "Create Flutter App", 
                     "command": "flutter create my_flutter_app",
                     "description": "Create a new Flutter project named 'my_flutter_app'."},
                    {"name": "Flutter Doctor", 
                     "command": "flutter doctor",
                     "description": "Check if Flutter development environment is set up correctly."}
                ],
                "Android": [
                    {"name": "Check Android SDK", 
                     "command": self._get_os_specific_command("adb --version"),
                     "description": "Check if Android Debug Bridge (ADB) is installed."},
                    {"name": "List Android Devices", 
                     "command": "adb devices",
                     "description": "List all connected Android devices."},
                    {"name": "Open Android Emulator", 
                     "command": self._get_os_specific_command("emulator -list-avds"),
                     "description": "List available Android emulators."}
                ]
            },
            "Data Science": {
                "Python Data": [
                    {"name": "Install NumPy", 
                     "command": "pip install numpy",
                     "description": "Install NumPy library for numerical computing."},
                    {"name": "Install Pandas", 
                     "command": "pip install pandas",
                     "description": "Install Pandas library for data manipulation and analysis."},
                    {"name": "Install Matplotlib", 
                     "command": "pip install matplotlib",
                     "description": "Install Matplotlib library for creating visualizations."},
                    {"name": "Install Scikit-learn", 
                     "command": "pip install scikit-learn",
                     "description": "Install Scikit-learn library for machine learning."}
                ],
                "R": [
                    {"name": "Check R Version", 
                     "command": self._get_os_specific_command("R --version"),
                     "description": "Check if R is installed and display its version."},
                    {"name": "Install RStudio", 
                     "command": self._get_os_specific_command("rstudio --version"),
                     "description": "Check if RStudio is installed."}
                ],
                "Jupyter": [
                    {"name": "Install Jupyter", 
                     "command": "pip install jupyter",
                     "description": "Install Jupyter Notebook for interactive computing."},
                    {"name": "Start Jupyter Notebook", 
                     "command": "jupyter notebook",
                     "description": "Start Jupyter Notebook server."}
                ]
            },
            "DevOps": {
                "Docker": [
                    {"name": "Check Docker Version", 
                     "command": self._get_os_specific_command("docker --version"),
                     "description": "Check if Docker is installed and display its version."},
                    {"name": "Docker PS", 
                     "command": "docker ps",
                     "description": "List all running Docker containers."},
                    {"name": "Docker Images", 
                     "command": "docker images",
                     "description": "List all Docker images."}
                ],
                "Git": [
                    {"name": "Check Git Version", 
                     "command": "git --version",
                     "description": "Check if Git is installed and display its version."},
                    {"name": "Git Init", 
                     "command": "git init",
                     "description": "Initialize a new Git repository in the current directory."},
                    {"name": "Git Status", 
                     "command": "git status",
                     "description": "Show the working tree status."}
                ],
                "Cloud": [
                    {"name": "Check AWS CLI", 
                     "command": self._get_os_specific_command("aws --version"),
                     "description": "Check if AWS CLI is installed and display its version."},
                    {"name": "Check Azure CLI", 
                     "command": self._get_os_specific_command("az --version"),
                     "description": "Check if Azure CLI is installed and display its version."},
                    {"name": "Check GCloud CLI", 
                     "command": self._get_os_specific_command("gcloud --version"),
                     "description": "Check if Google Cloud CLI is installed and display its version."}
                ]
            },
            "Database": {
                "SQL": [
                    {"name": "Check MySQL", 
                     "command": self._get_os_specific_command("mysql --version"),
                     "description": "Check if MySQL is installed and display its version."},
                    {"name": "Check PostgreSQL", 
                     "command": self._get_os_specific_command("psql --version"),
                     "description": "Check if PostgreSQL is installed and display its version."},
                    {"name": "Check SQLite", 
                     "command": self._get_os_specific_command("sqlite3 --version"),
                     "description": "Check if SQLite is installed and display its version."}
                ],
                "NoSQL": [
                    {"name": "Check MongoDB", 
                     "command": self._get_os_specific_command("mongo --version"),
                     "description": "Check if MongoDB is installed and display its version."},
                    {"name": "Check Redis", 
                     "command": self._get_os_specific_command("redis-cli --version"),
                     "description": "Check if Redis CLI is installed and display its version."}
                ]
            },
            "Troubleshooting": {
                "Common Errors": [
                    {"name": "Fix Python Module Not Found", 
                     "command": "pip install --upgrade pip && pip list",
                     "description": "Upgrade pip and list installed packages to help diagnose module not found errors."},
                    {"name": "Fix Node.js Package Not Found", 
                     "command": "npm cache clean --force && npm list -g --depth=0",
                     "description": "Clean npm cache and list globally installed packages."},
                    {"name": "Fix Port Already in Use", 
                     "command": self._get_port_check_command(),
                     "description": "Check which processes are using common ports (3000, 8000, 8080)."},
                    {"name": "Fix Git Authentication", 
                     "command": "git config --list",
                     "description": "List Git configuration to debug authentication issues."}
                ],
                "System": [
                    {"name": "Check Disk Space", 
                     "command": self._get_disk_space_command(),
                     "description": "Check available disk space on the system."},
                    {"name": "Check Memory Usage", 
                     "command": self._get_memory_check_command(),
                     "description": "Check current memory usage on the system."},
                    {"name": "List Running Processes", 
                     "command": self._get_process_list_command(),
                     "description": "List all running processes on the system."},
                    {"name": "Network Connectivity", 
                     "command": "ping -c 4 google.com" if platform.system() != "Windows" else "ping -n 4 google.com",
                     "description": "Test network connectivity by pinging Google.com."}
                ]
            }
        }
                
        # Add commands to tree widget
        for domain, categories in self.dev_commands.items():
            domain_item = QTreeWidgetItem([domain])
            domain_item.setFont(0, QFont("Arial", 11, QFont.Bold))
            self.tree_widget.addTopLevelItem(domain_item)
            
            for category, commands in categories.items():
                category_item = QTreeWidgetItem([category])
                category_item.setFont(0, QFont("Arial", 10))
                domain_item.addChild(category_item)
                
                for cmd in commands:
                    command_item = QTreeWidgetItem([cmd["name"]])
                    command_item.setData(0, Qt.UserRole, cmd)
                    command_item.setFont(0, QFont("Arial", 9))
                    category_item.addChild(command_item)
            
            domain_item.setExpanded(True)


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
        
        # Apply styles to tree widget
        self.tree_widget.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {colors["main_bg"]};
                border: none;
                outline: none;
                color: {colors["text"]};
            }}
            QTreeWidget::item {{
                padding: 5px;
                border-radius: 2px;
            }}
            QTreeWidget::item:selected {{
                background-color: {colors["highlight_bg"]};
            }}
            QTreeWidget::item:hover {{
                background-color: {colors["secondary_bg"]};
            }}
        """)
        
        # Apply styles to command header and description
        self.command_header.setStyleSheet(f"color: {colors['text']};")
        self.command_description.setStyleSheet(f"color: {colors['secondary_text']};")
        
        # Apply styles to execution frame
        execution_frame = self.findChild(QFrame)
        if execution_frame:
            execution_frame.setStyleSheet(f"background-color: {colors['secondary_bg']}; border-radius: 5px; padding: 15px;")
        
        # Apply styles to command input
        self.command_text.setStyleSheet(f"""
            QLineEdit {{
                background-color: {colors['main_bg']};
                color: {colors['success']};
                border-radius: 3px;
                padding: 8px;
                selection-background-color: {colors['highlight_bg']};
            }}
        """)
        
        # Apply styles to buttons
        self.execute_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['success']};
                color: {colors['main_bg']};
                border-radius: 5px;
                padding: 10px;
                min-width: 150px;
            }}
            QPushButton:hover {{
                background-color: {colors['accent']};
            }}
        """)
        
        self.terminal_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['accent']};
                color: {colors['main_bg']};
                border-radius: 5px;
                padding: 10px;
                min-width: 150px;
            }}
            QPushButton:hover {{
                background-color: {colors['highlight_bg']};
            }}
        """)
        
        # Apply styles to result output
        self.result_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: {colors['main_bg']};
                color: {colors['text']};
                border-radius: 3px;
                selection-background-color: {colors['highlight_bg']};
            }}
        """)




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
        self.command_header.setFont(QFont("Arial", sizes["header"], QFont.Bold))
        
        # Update description font
        self.command_description.setFont(QFont("Arial", sizes["normal"]))
        
        # Update tree widget fonts
        for i in range(self.tree_widget.topLevelItemCount()):
            domain_item = self.tree_widget.topLevelItem(i)
            domain_item.setFont(0, QFont("Arial", sizes["subheader"], QFont.Bold))
            
            for j in range(domain_item.childCount()):
                category_item = domain_item.child(j)
                category_item.setFont(0, QFont("Arial", sizes["normal"]))
                
                for k in range(category_item.childCount()):
                    command_item = category_item.child(k)
                    command_item.setFont(0, QFont("Arial", sizes["small"]))
        
        # Update command input font
        self.command_text.setFont(QFont("Consolas", sizes["normal"]))
        
        # Update buttons fonts
        self.execute_button.setFont(QFont("Arial", sizes["normal"]))
        self.terminal_button.setFont(QFont("Arial", sizes["normal"]))
        
        # Update result output font
        self.result_output.setFont(QFont("Consolas", sizes["small"]))




            
    def _get_os_specific_command(self, cmd):
        """Return OS-specific version of commands"""
        if platform.system() == "Windows":
            if cmd == "node -v":
                return "where node || echo Node.js is not installed. Please download from https://nodejs.org/"
            elif cmd == "php -v":
                return "where php || echo PHP is not installed."
            elif cmd == "composer --version":
                return "where composer || echo Composer is not installed."
            elif cmd == "flutter --version":
                return "where flutter || echo Flutter is not installed."
            elif cmd == "adb --version":
                return "where adb || echo Android Debug Bridge (ADB) is not installed."
            elif cmd == "emulator -list-avds":
                return "where emulator && emulator -list-avds || echo Android Emulator is not installed."
            elif cmd == "R --version":
                return "where R || echo R is not installed."
            elif cmd == "rstudio --version":
                return "where rstudio || echo RStudio is not installed."
            elif cmd == "docker --version":
                return "where docker || echo Docker is not installed."
            elif cmd == "aws --version":
                return "where aws || echo AWS CLI is not installed."
            elif cmd == "az --version":
                return "where az || echo Azure CLI is not installed."
            elif cmd == "gcloud --version":
                return "where gcloud || echo Google Cloud CLI is not installed."
            elif cmd == "mysql --version":
                return "where mysql || echo MySQL is not installed."
            elif cmd == "psql --version":
                return "where psql || echo PostgreSQL is not installed."
            elif cmd == "sqlite3 --version":
                return "where sqlite3 || echo SQLite is not installed."
            elif cmd == "mongo --version":
                return "where mongo || echo MongoDB is not installed."
            elif cmd == "redis-cli --version":
                return "where redis-cli || echo Redis CLI is not installed."
        else:  # Unix-like OS (macOS, Linux)
            if cmd == "node -v":
                return "which node && node -v || echo 'Node.js is not installed. Please install using package manager.'"
            elif cmd == "php -v":
                return "which php && php -v || echo 'PHP is not installed.'"
            elif cmd == "composer --version":
                return "which composer && composer --version || echo 'Composer is not installed.'"
            elif cmd == "flutter --version":
                return "which flutter && flutter --version || echo 'Flutter is not installed.'"
            elif cmd == "adb --version":
                return "which adb && adb --version || echo 'Android Debug Bridge (ADB) is not installed.'"
            elif cmd == "emulator -list-avds":
                return "which emulator && emulator -list-avds || echo 'Android Emulator is not installed.'"
            elif cmd == "R --version":
                return "which R && R --version || echo 'R is not installed.'"
            elif cmd == "rstudio --version":
                return "which rstudio && rstudio --version || echo 'RStudio is not installed.'"
            elif cmd == "docker --version":
                return "which docker && docker --version || echo 'Docker is not installed.'"
            elif cmd == "aws --version":
                return "which aws && aws --version || echo 'AWS CLI is not installed.'"
            elif cmd == "az --version":
                return "which az && az --version || echo 'Azure CLI is not installed.'"
            elif cmd == "gcloud --version":
                return "which gcloud && gcloud --version || echo 'Google Cloud CLI is not installed.'"
            elif cmd == "mysql --version":
                return "which mysql && mysql --version || echo 'MySQL is not installed.'"
            elif cmd == "psql --version":
                return "which psql && psql --version || echo 'PostgreSQL is not installed.'"
            elif cmd == "sqlite3 --version":
                return "which sqlite3 && sqlite3 --version || echo 'SQLite is not installed.'"
            elif cmd == "mongo --version":
                return "which mongo && mongo --version || echo 'MongoDB is not installed.'"
            elif cmd == "redis-cli --version":
                return "which redis-cli && redis-cli --version || echo 'Redis CLI is not installed.'"
            
        return cmd
    
    def _get_port_check_command(self):
        """Return OS-specific command to check ports"""
        if platform.system() == "Windows":
            return "netstat -ano | findstr :3000 && netstat -ano | findstr :8000 && netstat -ano | findstr :8080"
        elif platform.system() == "Darwin":  # macOS
            return "lsof -i :3000,8000,8080"
        else:  # Linux
            return "netstat -tulpn | grep -E ':(3000|8000|8080)'"
    
    def _get_disk_space_command(self):
        """Return OS-specific command to check disk space"""
        if platform.system() == "Windows":
            return "wmic logicaldisk get deviceid, freespace, size, volumename"
        else:  # Unix-like
            return "df -h"
    
    def _get_memory_check_command(self):
        """Return OS-specific command to check memory usage"""
        if platform.system() == "Windows":
            return "wmic OS get FreePhysicalMemory, TotalVisibleMemorySize /Value"
        elif platform.system() == "Darwin":  # macOS
            return "top -l 1 -s 0 | grep PhysMem"
        else:  # Linux
            return "free -h"
    
    def _get_process_list_command(self):
        """Return OS-specific command to list processes"""
        if platform.system() == "Windows":
            return "tasklist"
        elif platform.system() == "Darwin":  # macOS
            return "ps -ax"
        else:  # Linux
            return "ps aux"
        
    def on_tree_selection_changed(self):
        items = self.tree_widget.selectedItems()
        if items:
            item = items[0]
            # Check if item is a command (leaf node)
            if item.childCount() == 0:
                command_data = item.data(0, Qt.UserRole)
                if command_data:
                    self.command_header.setText(command_data["name"])
                    self.command_description.setText(command_data["description"])
                    self.command_text.setText(command_data["command"])
                    self.execute_button.setEnabled(True)
                    self.terminal_button.setEnabled(True)
                else:
                    self.command_header.setText("Select a command")
                    self.command_description.setText("")
                    self.command_text.setText("")
                    self.execute_button.setEnabled(False)
                    self.terminal_button.setEnabled(False)
            else:
                self.command_header.setText(f"{item.text(0)} Category")
                self.command_description.setText("Select a specific command to execute")
                self.command_text.setText("")
                self.execute_button.setEnabled(False)
                self.terminal_button.setEnabled(False)
        else:
            self.command_header.setText("Select a command from the tree")
            self.command_description.setText("")
            self.command_text.setText("")
            self.execute_button.setEnabled(False)
            self.terminal_button.setEnabled(False)

    def execute_command(self):
        command = self.command_text.text()
        if not command:
            self.result_output.setText("No command selected!")
            return
        
        # Clear previous output
        self.result_output.clear()
        self.result_output.append(f"Executing: {command}\n")
        self.result_output.append("Please wait...\n\n")
        
        # Create worker thread for command execution
        worker = CommandWorker(command)
        self.command_workers.append(worker)  # Keep a reference
        worker.finished.connect(self.handle_command_result)
        worker.start()

    
    def handle_command_result(self, stdout, stderr):
        """Handle the result of command execution"""
        if stdout:
            self.result_output.append("Output:\n")
            self.result_output.append(stdout)
        
        if stderr:
            self.result_output.append("\nErrors:\n")
            self.result_output.append(stderr)
            
        self.result_output.append("\nCommand execution completed.")

    def open_in_terminal(self):
        """Open the selected command in a terminal"""
        command = self.command_text.text()
        if not command:
            return
        
        # Open terminal based on OS
        try:
            if platform.system() == "Windows":
                subprocess.Popen(f'start cmd.exe /K "{command}"', shell=True)
            elif platform.system() == "Darwin":  # macOS
                applescript = f'tell application "Terminal" to do script "{command}"'
                subprocess.Popen(["osascript", "-e", applescript])
            else:
                # Linux
                # Try to detect the terminal
                terminals = ["gnome-terminal", "konsole", "xterm"]
                for term in terminals:
                    try:
                        subprocess.Popen([term, "-e", f"bash -c '{command}; read -p \"Press Enter to exit...\"'"])
                        break
                    except FileNotFoundError:
                        continue
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open terminal: {str(e)}")