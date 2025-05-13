from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, 
                          QTextEdit, QPushButton, QLineEdit)
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import Qt

from services.gemini_client import GeminiAPIClient
from utils.response_thread import ResponseThread
import os
import json

class AIChatWidget(QWidget):
    """Widget for the Gemini AI chat assistant"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.response_thread = None
        
        # Initialize with saved API key or empty string
        saved_key = self.load_api_key()
        self.gemini_client = GeminiAPIClient(api_key=saved_key)
        
        # If we have a saved key, show it masked in the input field
        if saved_key:
            self.api_key_input.setText("*" * 10)  # Mask the actual key
            self.chat_display.append("<span style='color:#A3BE8C;'><b>System:</b></span> API key loaded from settings.")
        
        self.system_context = """You are DevAssist's AI helper, an expert in software development, 
        troubleshooting, and technical assistance. 
        Help users solve programming errors, installation issues, 
        and provide guidance on development tools and technologies."""
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Chat header
        header = QLabel("DevAssist AI Chat")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #ECEFF4;")
        layout.addWidget(header)
        
        # Description
        description = QLabel(
            "Get help with development issues, troubleshooting, and technical questions. "
            "The AI assistant is powered by Google's Gemini API."
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #D8DEE9;")
        layout.addWidget(description)
        
        # Chat area
        chat_frame = QFrame()
        chat_frame.setStyleSheet("background-color: #3B4252; border-radius: 5px;")
        chat_layout = QVBoxLayout(chat_frame)
        
        # Chat display
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
        chat_layout.addWidget(self.chat_display)
        
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
        
        layout.addWidget(chat_frame)
        
        # Add a welcome message
        self.chat_display.append("<span style='color:#88C0D0;'>DevAssist AI:</span> Welcome to DevAssist! I'm here to help with your development questions and troubleshooting issues. How can I assist you today?")
        
    def send_message(self):
        """Send user message to the AI assistant"""
        user_message = self.chat_input.toPlainText().strip()
        if not user_message:
            return
            
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
        
        # Add the actual response
        self.chat_display.append(f"<span style='color:#88C0D0;'><b>DevAssist AI:</b></span> {response}")
    
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
    

    def closeEvent(self, event):
        """Called when the widget is closed"""
        # Make sure thread is properly stopped
        if self.response_thread is not None and self.response_thread.isRunning():
            self.response_thread.stop()
            self.response_thread.wait()
        super().closeEvent(event)