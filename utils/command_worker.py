import subprocess
from PyQt5.QtCore import QThread, pyqtSignal
import os

class CommandWorker(QThread):
    """Thread worker for running commands asynchronously with custom working directory"""
    
    finished = pyqtSignal(str, str)  # Signal emitted when command execution finishes (stdout, stderr)
    
    def __init__(self, command, working_dir=None):
        super().__init__()
        self.command = command
        # Ensure working directory is properly set and validated
        self.working_dir = working_dir if working_dir and os.path.exists(working_dir) else os.getcwd()
        
    def run(self):
        """Run the command in the specified working directory"""
        try:
            # Log the execution details for debugging
            print(f"Executing command: {self.command}")
            print(f"Working directory: {self.working_dir}")
            
            # Use the specified working directory
            result = subprocess.run(
                self.command,
                capture_output=True,
                text=True,
                shell=True,
                cwd=self.working_dir  # This specifies the working directory for the command
            )
            
            # Process the results
            stdout = result.stdout.strip() if result.stdout else ""
            stderr = result.stderr.strip() if result.stderr else ""
            
            # Emit the results
            self.finished.emit(stdout, stderr)
            
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            print(error_msg)
            self.finished.emit("", error_msg)