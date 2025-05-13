import subprocess
from PyQt5.QtCore import QThread, pyqtSignal

class CommandWorker(QThread):
    """Thread worker for running commands asynchronously"""
    finished = pyqtSignal(str, str)
    
    def __init__(self, command):
        super().__init__()
        self.command = command
        
    def run(self):
        try:
            result = subprocess.run(self.command, 
                                  capture_output=True, 
                                  text=True, 
                                  shell=True)
            self.finished.emit(result.stdout, result.stderr)
        except Exception as e:
            self.finished.emit("", str(e))