from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, 
                          QTextEdit, QPushButton, QLineEdit, QMessageBox, QScrollArea)
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import Qt, pyqtSignal

from services.gemini_client import GeminiAPIClient
from utils.response_thread import ResponseThread
from utils.command_worker import CommandWorker
import os
import json
import re

class EnhancedGeminiAPIClient(GeminiAPIClient):
    """Enhanced Gemini API Client with issue detection and solution recommendation"""
    
    def __init__(self, api_key=""):
        super().__init__(api_key)
        
    def detect_command_intent(self, response_text):
        """Detect if the AI is suggesting a command to run"""
        # Look for patterns like "Run: command" or "Execute: command" or ```command```
        command_patterns = [
            r"```(?:bash|shell|cmd|powershell)?\s*(.*?)```",  # Code blocks with shell commands
            r"Run:\s*`?(.*?)`?(?:\n|$)",  # "Run: command"
            r"Execute:\s*`?(.*?)`?(?:\n|$)",  # "Execute: command"
            r"Command:\s*`?(.*?)`?(?:\n|$)",  # "Command: command"
            r"Try running:\s*`?(.*?)`?(?:\n|$)",  # "Try running: command"
            r"You can run:\s*`?(.*?)`?(?:\n|$)"  # "You can run: command"
        ]
        
        suggested_commands = []
        
        for pattern in command_patterns:
            matches = re.findall(pattern, response_text, re.MULTILINE | re.DOTALL)
            for match in matches:
                cmd = match.strip()
                if cmd and len(cmd) < 500:  # Reasonable command length limit
                    suggested_commands.append(cmd)
        
        return suggested_commands


class AIChatWidget(QWidget):
    """Widget for the Gemini AI chat assistant with command execution capabilities"""
    
    command_suggested = pyqtSignal(str)  # Signal emitted when AI suggests a command
    
    def __init__(self):
        super().__init__()
        self.current_theme = "Nord Dark (Default)"
        self.current_font_size = "Medium (Default)"
        
        self.system_info = {}
        self.setup_ui()
        self.current_command_context = {
          "name": "Current Directory",
          "path": os.getcwd()
        }
        self.command_workers = []  # Add a list to track command workers
        self.response_thread = None  # Initialize response thread to None
        # Rest of initialization remains the same
        
        # Initialize with saved API key or empty string
        saved_key = self.load_api_key()
        self.gemini_client = EnhancedGeminiAPIClient(api_key=saved_key)
        
        # If we have a saved key, show it masked in the input field
        if saved_key:
            self.api_key_input.setText("*" * 10)  # Mask the actual key
            self.chat_display.append("<span style='color:#A3BE8C;'><b>System:</b></span> API key loaded from settings.")
        
        self.system_context = """You are DevAssist AI, an expert in software development, 
        troubleshooting, and technical assistance. 
        Help users solve programming errors, installation issues, 
        and provide guidance on development tools and technologies.
        
        When you identify a problem that requires executing a command to fix or diagnose,
        format your suggestion clearly as follows:
        
        "I recommend running this command to fix the issue:
        ```bash
        [the command to run]
        ```"
    
        Important guidelines:
        1. Provide clear but concise explanations of what a command does.
        2. When analyzing command output, focus only on what's important.
        3. After analyzing the output of an executed command, DO NOT suggest additional commands 
           unless explicitly asked by the user.
        4. Keep your responses focused and brief - no more than 3-4 paragraphs.
        5. Don't overexplain or provide additional information unless requested.
        
        Be direct and to the point while remaining helpful."""
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Chat header
        self.header = QLabel("DevAssist AI")
        self.header.setFont(QFont("Arial", 16, QFont.Bold))
        self.header.setStyleSheet("color: #ECEFF4;")
        layout.addWidget(self.header)
        
        # Description
        self.description = QLabel(
            "Get help with development issues, troubleshooting, and technical questions. "
            "DevAssist can recommend and execute commands to solve problems."
        )
        self.description.setWordWrap(True)
        self.description.setStyleSheet("color: #D8DEE9;")
        layout.addWidget(self.description)
        
        # Chat area
        self.chat_frame = QFrame()
        self.chat_frame.setStyleSheet("background-color: #3B4252; border-radius: 5px;")
        chat_layout = QVBoxLayout(self.chat_frame)
        
        # Chat display with scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #2E3440;
                border-radius: 3px;
            }
        """)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Arial", 10))
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #2E3440;
                color: #E5E9F0;
                border-radius: 3px;
                padding: 10px;
                selection-background-color: #5E81AC;
            }
        """)
        self.chat_display.setMinimumHeight(300)
        
        # Set the chat display as the widget for the scroll area
        self.scroll_area.setWidget(self.chat_display)
        chat_layout.addWidget(self.scroll_area)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.chat_input = QTextEdit()
        self.chat_input.setFont(QFont("Arial", 10))
        self.chat_input.setStyleSheet("""
            QTextEdit {
                background-color: #2E3440;
                color: #E5E9F0;
                border-radius: 3px;
                padding: 10px;
                selection-background-color: #5E81AC;
            }
        """)
        self.chat_input.setMaximumHeight(100)
        self.chat_input.setPlaceholderText("Type your question here...")
        
        self.send_button = QPushButton("Send")
        self.send_button.setFont(QFont("Arial", 11))
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #88C0D0;
                color: #2E3440;
                border-radius: 5px;
                padding: 10px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #8FBCBB;
            }
            QPushButton:pressed {
                background-color: #81A1C1;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(self.send_button)
        chat_layout.addLayout(input_layout)
        
        # Command execution area
        self.command_frame = QFrame()
        self.command_frame.setStyleSheet("background-color: #3B4252; border-radius: 5px; margin-top: 10px;")
        self.command_frame.setVisible(False)  # Initially hidden
        command_layout = QVBoxLayout(self.command_frame)
        
        # Command label
        self.command_label = QLabel("DevAssist suggests running this command:")
        self.command_label.setStyleSheet("color: #88C0D0;")
        command_layout.addWidget(self.command_label)
        
        # Command display
        self.command_display = QLineEdit()
        self.command_display.setReadOnly(True)
        self.command_display.setFont(QFont("Consolas", 10))
        self.command_display.setStyleSheet("""
            QLineEdit {
                background-color: #2E3440;
                color: #A3BE8C;
                border-radius: 3px;
                padding: 8px;
                selection-background-color: #5E81AC;
            }
        """)
        command_layout.addWidget(self.command_display)
        
        # Command buttons
        command_buttons_layout = QHBoxLayout()
        
        self.execute_command_button = QPushButton("Execute Command")
        self.execute_command_button.setFont(QFont("Arial", 11))
        self.execute_command_button.setCursor(Qt.PointingHandCursor)
        self.execute_command_button.setStyleSheet("""
            QPushButton {
                background-color: #A3BE8C;
                color: #2E3440;
                border-radius: 5px;
                padding: 8px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #B9D395;
            }
            QPushButton:pressed {
                background-color: #8CAA74;
            }
        """)
        self.execute_command_button.clicked.connect(self.execute_suggested_command)
        
        self.dismiss_command_button = QPushButton("Dismiss")
        self.dismiss_command_button.setFont(QFont("Arial", 11))
        self.dismiss_command_button.setCursor(Qt.PointingHandCursor)
        self.dismiss_command_button.setStyleSheet("""
            QPushButton {
                background-color: #4C566A;
                color: #E5E9F0;
                border-radius: 5px;
                padding: 8px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
            QPushButton:pressed {
                background-color: #81A1C1;
            }
        """)
        self.dismiss_command_button.clicked.connect(self.dismiss_command)
        
        command_buttons_layout.addWidget(self.execute_command_button)
        command_buttons_layout.addWidget(self.dismiss_command_button)
        command_layout.addLayout(command_buttons_layout)
        
        # Command output
        self.command_output = QTextEdit()
        self.command_output.setReadOnly(True)
        self.command_output.setFont(QFont("Consolas", 9))
        self.command_output.setStyleSheet("""
            QTextEdit {
                background-color: #2E3440;
                color: #D8DEE9;
                border-radius: 3px;
                padding: 8px;
                selection-background-color: #5E81AC;
                max-height: 200px;
            }
        """)
        self.command_output.setVisible(False)  # Initially hidden
        self.command_output.setMaximumHeight(200)
        command_layout.addWidget(self.command_output)
        
        chat_layout.addWidget(self.command_frame)
        
        # API key setup
        api_layout = QHBoxLayout()
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setFont(QFont("Arial", 10))
        self.api_key_input.setStyleSheet("""
            QLineEdit {
                background-color: #2E3440;
                color: #E5E9F0;
                border-radius: 3px;
                padding: 8px;
                selection-background-color: #5E81AC;
            }
        """)
        self.api_key_input.setPlaceholderText("Enter Gemini API Key...")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        
        self.save_api_button = QPushButton("Save API Key")
        self.save_api_button.setFont(QFont("Arial", 11))
        self.save_api_button.setCursor(Qt.PointingHandCursor)
        self.save_api_button.setStyleSheet("""
            QPushButton {
                background-color: #A3BE8C;
                color: #2E3440;
                border-radius: 5px;
                padding: 8px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #B9D395;
            }
            QPushButton:pressed {
                background-color: #8CAA74;
            }
        """)
        self.save_api_button.clicked.connect(self.save_api_key)
        
        api_layout.addWidget(self.api_key_input)
        api_layout.addWidget(self.save_api_button)
        chat_layout.addLayout(api_layout)
        
        layout.addWidget(self.chat_frame)
        
        # Add a welcome message
        self.chat_display.append("<span style='color:#88C0D0;'>DevAssist AI:</span> Welcome to DevAssist! I'm here to help with your development questions and troubleshooting issues. I can suggest and execute commands to fix problems. How can I assist you today?")

        pass



    # Add this function to AIChatWidget class in AIChatWidget.py
    def update_system_context_with_system_info(self, system_info):
       """Updates the system context with system information"""
       # Create a simplified version of the system info for the context
       self.system_info = system_info
       simplified_info = {
          "os": system_info["System"]["OS"],
          "architecture": system_info["System"]["Architecture"],
          "cpu_cores": system_info["Hardware"]["CPU Cores"],
          "ram": system_info["Hardware"]["RAM"],
          "python_version": system_info["Python Environment"]["Python Version"]
        }
    
        # Add storage info if available
       if "Storage" in system_info:
          simplified_info["storage"] = list(system_info["Storage"].items())[0][1]
    
        # Format the system info as a string for the context
       system_info_str = json.dumps(simplified_info, indent=2)
    
       # Update the system context to include system information
       self.system_context = f"""You are DevAssist AI, an expert in software development, 
          troubleshooting, and technical assistance. 
          Help users solve programming errors, installation issues, 
          and provide guidance on development tools and technologies.
        
          You have access to the following system information about the user's computer.
          Use this information to provide tailored commands and solutions specific to their system:
        
          {system_info_str}
        
          When you identify a problem that requires executing a command to fix or diagnose,
          format your suggestion clearly as follows:
        
          "I recommend running this command to fix the issue:
          ```bash
          [the command to run]
          ```"
    
          Important guidelines:
          1. Provide clear but concise explanations of what a command does.
          2. When analyzing command output, focus only on what's important.
          3. After analyzing the output of an executed command, DO NOT suggest additional commands 
             unless explicitly asked by the user.
          4. Keep your responses focused and brief - no more than 3-4 paragraphs.
          5. Don't overexplain or provide additional information unless requested.
          6. Always consider the user's specific operating system ({simplified_info["os"]}) when 
             suggesting commands or solutions.
          
          Be direct and to the point while remaining helpful."""

       


        
    def send_message(self):
        """Send user message to the AI assistant"""
        user_message = self.chat_input.toPlainText().strip()
        if not user_message:
            return
            
        # Hide the command frame if it's visible
        self.command_frame.setVisible(False)
        self.command_output.setVisible(False)
        
        # Display user message
        self.chat_display.append(f"<span style='color:#EBCB8B;'><b>You:</b></span> {user_message}")
        self.chat_input.clear()
        
        # Get AI response
        if not self.gemini_client.api_key:
            self.chat_display.append("<span style='color:#BF616A;'><b>System:</b></span> Please enter a Gemini API key to use the AI chat feature.")
            return
            
        self.chat_display.append("<span style='color:#88C0D0;'><b>DevAssist AI:</b></span> <i>Thinking...</i>")
        # Stop any existing thread before creating a new one
        if self.response_thread is not None and self.response_thread.isRunning():
            self.response_thread.stop()
            self.response_thread.wait()
        
        # Create response thread
        self.response_thread = ResponseThread(self.gemini_client, user_message, self.system_context)
        self.response_thread.response_received.connect(self.handle_response)
        self.response_thread.start()
        
    def handle_response(self, response):
        """Handle the AI response"""
        # Remove the "thinking" message
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()  # Delete the newline
        
        # Truncate response if it's too long to prevent UI glitches
        max_response_length = 2000  # Adjust this value based on your UI needs
        truncated_response = response
        if len(response) > max_response_length:
            # Find the last period before the max length to make a clean cutoff
            last_period = response[:max_response_length].rfind('.')
            if last_period > max_response_length // 2:  # Make sure we have a substantial amount of text
                truncated_response = response[:last_period + 1] + " [Response truncated for display...]"
            else:
                truncated_response = response[:max_response_length] + "... [Response truncated for display...]"
        
        # Add the actual response
        self.chat_display.append(f"<span style='color:#88C0D0;'><b>DevAssist AI:</b></span> {truncated_response}")
        
        # Check if the response contains command suggestions
        suggested_commands = self.gemini_client.detect_command_intent(response)
        if suggested_commands:
            # Use the first suggested command
            self.show_command_suggestion(suggested_commands[0])
        
        # Scroll to the bottom after adding content
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def show_command_suggestion(self, command):
        """Show the command suggestion UI"""
        self.command_display.setText(command)
        self.command_frame.setVisible(True)
        self.command_output.clear()
        self.command_output.setVisible(False)
        
        # Also emit the signal for any listeners
        self.command_suggested.emit(command)
    
    def dismiss_command(self):
        """Hide the command suggestion UI"""
        self.command_frame.setVisible(False)
        self.command_output.setVisible(False)
    
    # Update this method in the AIChatWidget class (in services/chat_widgets.py)

    def execute_suggested_command(self):
       """Execute the suggested command after confirmation"""
       command = self.command_display.text()
    
       # Ensure we have a valid working directory
       working_dir = self.current_command_context['path']
       context_name = self.current_command_context['name']
    
       # Make sure the directory exists
       if not os.path.exists(working_dir):
           self.command_output.setVisible(True)
           self.command_output.clear()
           self.command_output.append(f"Error: The directory '{working_dir}' does not exist.")
           return
    
       # Ask for confirmation
       reply = QMessageBox.question(
           self, 
           "Execute Command",
           f"Are you sure you want to execute this command?\n\n{command}\n\nIn directory: {working_dir}",
           QMessageBox.Yes | QMessageBox.No,
           QMessageBox.No
       )
    
       if reply == QMessageBox.Yes:
           # Show the output area
           self.command_output.setVisible(True)
           self.command_output.clear()
           self.command_output.append(f"Executing: {command}")
           self.command_output.append(f"Working directory: {working_dir}")
           self.command_output.append(f"Context: {context_name}\n")
           self.command_output.append("Please wait...\n\n")
        
           # Create worker thread for command execution
           # Make sure we're passing the current context path explicitly
           worker = CommandWorker(command, working_dir=working_dir)
           self.command_workers.append(worker)  # Keep a reference
           worker.finished.connect(self.handle_command_result)
           worker.start()
    
    def handle_command_result(self, stdout, stderr):
         """Handle the result of command execution"""
         if stdout:
           self.command_output.append("Output:\n")
           self.command_output.append(stdout)
    
         if stderr:
           self.command_output.append("\nErrors:\n")
           self.command_output.append(stderr)
        
         self.command_output.append("\nCommand execution completed.")
    
         # Send the result to the AI
         output_text = ""
         if stdout:
            output_text += f"Command output:\n{stdout}\n"
         if stderr:
            output_text += f"Command errors:\n{stderr}\n"
        
         if output_text:
            # Truncate output if it's too long
           max_output_length = 1500  # Adjust as needed
           if len(output_text) > max_output_length:
            output_text = output_text[:max_output_length] + "... [Output truncated for analysis]"
        
            # Automatically send the result to the AI for analysis, but be more specific
           result_message = f"""Here's the result of executing the command '{self.command_display.text()}':\n\n{output_text}\n\n
           Please provide a brief analysis of this output only. Do not suggest additional commands unless I specifically ask for them."""
        
           self.chat_display.append(f"<span style='color:#EBCB8B;'><b>You:</b></span> Command executed. Please analyze the results.")
        
           # Create response thread for analysis
           if self.response_thread is not None and self.response_thread.isRunning():
              self.response_thread.stop()
              self.response_thread.wait()
            
           self.chat_display.append("<span style='color:#88C0D0;'><b>DevAssist AI:</b></span> <i>Analyzing results...</i>")
           self.response_thread = ResponseThread(self.gemini_client, result_message, self.system_context)
           self.response_thread.response_received.connect(self.handle_response)
           self.response_thread.start()
        
         # Automatically hide the command frame after execution
         self.command_frame.setVisible(False)
    
    def get_config_file_path(self):
        """Get the path to the configuration file"""
        config_dir = os.path.join(os.path.expanduser("~"), ".devassist")
        # Create directory if it doesn't exist
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        return os.path.join(config_dir, "config.json")
    
    def save_api_key(self):
        """Save the Gemini API key"""
        api_key = self.api_key_input.text().strip()
        if api_key and api_key != "*" * 10:  # Only save if it's not the masked placeholder
            # Save to the client
            self.gemini_client.api_key = api_key
            
            # Save to config file
            config_file = self.get_config_file_path()
            config_data = {}
            
            # Load existing config if it exists
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    config_data = {}
            
            # Update with new API key
            config_data['gemini_api_key'] = api_key
            
            # Save back to file
            try:
                with open(config_file, 'w') as f:
                    json.dump(config_data, f)
                self.chat_display.append("<span style='color:#A3BE8C;'><b>System:</b></span> API key saved successfully.")
            except Exception as e:
                self.chat_display.append(f"<span style='color:#BF616A;'><b>System:</b></span> Error saving API key: {str(e)}")
        else:
            self.chat_display.append("<span style='color:#BF616A;'><b>System:</b></span> Please enter a valid API key.")
    
    def load_api_key(self):
        """Load the Gemini API key from config file"""
        config_file = self.get_config_file_path()
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    return config_data.get('gemini_api_key', '')
            except (json.JSONDecodeError, FileNotFoundError):
                return ''
        return ''
    

    def execute_command(self, command):
       """Execute a command with the current command context"""
       # Create a command worker with the current context path
       self.command_worker = CommandWorker(command, self.current_command_context['path'])
       # Connect signals
       self.command_worker.finished.connect(self.on_command_finished)
       # Start the worker
       self.command_worker.start()

    def on_command_finished(self, stdout, stderr):
        """Handle command execution completion"""
        # Process results...
        pass


    def update_command_context(self, context_info):
      """Update the command execution context"""
      # Store the context information
      self.current_command_context = context_info
    
      # Log the context update for debugging
      print(f"AI Chat Command Context updated to: {context_info['name']} - {context_info['path']}")


      # Add a visual indication in the chat
      self.chat_display.append(f"<span style='color:#A3BE8C;'><b>System:</b></span> Command execution context changed to: {context_info['name']} - {context_info['path']}")


      # Update the command worker if it exists
      if hasattr(self, 'command_worker'):
          self.command_worker.working_dir = context_info['path']
    
      # Update the system context to include this information
      if hasattr(self, 'system_context') and self.system_context:
          # Add or update context information in the system context
          context_info_str = f"""
          Commands should be executed in the following context:
          - Context: {context_info['name']}
          - Directory: {context_info['path']}
          """
      
          # Check if we already have context info in the system context
          if "Commands should be executed in the following context:" in self.system_context:
              # Replace the existing context info
              pattern = r"Commands should be executed in the following context:.*?(?=\n\n|\Z)"
              self.system_context = re.sub(pattern, context_info_str.strip(), self.system_context, flags=re.DOTALL)
          else:
              # Add the context info to the end of the system context
              self.system_context += "\n\n" + context_info_str
            
      # Update UI to reflect the current context
      if hasattr(self, 'command_frame') and self.command_frame.isVisible():
          # If there's already a command being shown, update its context message
          if hasattr(self, 'command_label'):
              self.command_label.setText(f"DevAssist suggests running this command in {context_info['name']}:")
    
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
                "warning": "#D08770",
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
        
        colors = themes.get(theme_name, themes["Nord Dark (Default)"])
        
        # Apply styles to header and description
        self.header.setStyleSheet(f"color: {colors['text']};")
        self.description.setStyleSheet(f"color: {colors['secondary_text']};")
        
        # Apply styles to chat frame
        self.chat_frame.setStyleSheet(f"background-color: {colors['secondary_bg']}; border-radius: 5px;")
        
        # Apply styles to scroll area
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {colors['main_bg']};
                border-radius: 3px;
            }}
        """)
        
        # Apply styles to chat display
        self.chat_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {colors['main_bg']};
                color: {colors['text']};
                border-radius: 3px;
                padding: 10px;
                selection-background-color: {colors['highlight_bg']};
            }}
        """)
        
        # Apply styles to chat input
        self.chat_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {colors['main_bg']};
                color: {colors['text']};
                border-radius: 3px;
                padding: 10px;
                selection-background-color: {colors['highlight_bg']};
            }}
        """)
        
        # Apply styles to send button
        self.send_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['accent']};
                color: {colors['main_bg']};
                border-radius: 5px;
                padding: 10px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {colors['highlight_bg']};
            }}
            QPushButton:pressed {{
                background-color: {colors['secondary_bg']};
            }}
        """)
        
        # Apply styles to command frame
        self.command_frame.setStyleSheet(f"background-color: {colors['secondary_bg']}; border-radius: 5px; margin-top: 10px;")
        
        # Apply styles to command label
        self.command_label.setStyleSheet(f"color: {colors['accent']};")
        
        # Apply styles to command display
        self.command_display.setStyleSheet(f"""
            QLineEdit {{
                background-color: {colors['main_bg']};
                color: {colors['success']};
                border-radius: 3px;
                padding: 8px;
                selection-background-color: {colors['highlight_bg']};
            }}
        """)
        
        # Apply styles to command buttons
        self.execute_command_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['success']};
                color: {colors['main_bg']};
                border-radius: 5px;
                padding: 8px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {colors['accent']};
            }}
            QPushButton:pressed {{
                background-color: {colors['highlight_bg']};
            }}
        """)
        
        self.dismiss_command_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['highlight_bg']};
                color: {colors['text']};
                border-radius: 5px;
                padding: 8px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {colors['accent']};
            }}
            QPushButton:pressed {{
                background-color: {colors['secondary_bg']};
            }}
        """)
        
        # Apply styles to command output
        self.command_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: {colors['main_bg']};
                color: {colors['text']};
                border-radius: 3px;
                padding: 8px;
                selection-background-color: {colors['highlight_bg']};
            }}
        """)
        
        # Apply styles to API key input
        self.api_key_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {colors['main_bg']};
                color: {colors['text']};
                border-radius: 3px;
                padding: 8px;
                selection-background-color: {colors['highlight_bg']};
            }}
        """)
        
        # Apply styles to save API button
        self.save_api_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['success']};
                color: {colors['main_bg']};
                border-radius: 5px;
                padding: 8px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {colors['accent']};
            }}
            QPushButton:pressed {{
                background-color: {colors['highlight_bg']};
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
        self.header.setFont(QFont("Arial", sizes["header"], QFont.Bold))
        
        # Update description font
        self.description.setFont(QFont("Arial", sizes["normal"]))
        
        # Update chat display font
        self.chat_display.setFont(QFont("Arial", sizes["normal"]))
        
        # Update chat input font
        self.chat_input.setFont(QFont("Arial", sizes["normal"]))
        
        # Update send button font
        self.send_button.setFont(QFont("Arial", sizes["normal"]))
        
        # Update API key input font
        self.api_key_input.setFont(QFont("Arial", sizes["normal"]))
        
        # Update save API button font
        self.save_api_button.setFont(QFont("Arial", sizes["normal"]))
    
    def closeEvent(self, event):
        """Called when the widget is closed"""
        # Make sure thread is properly stopped
        if self.response_thread is not None and self.response_thread.isRunning():
            self.response_thread.stop()
            self.response_thread.wait()
        super().closeEvent(event)