from PyQt5.QtCore import QThread, pyqtSignal

class ResponseThread(QThread):
    """Thread for getting responses from the AI"""
    response_received = pyqtSignal(str)
    
    def __init__(self, client, prompt, system_context):
        super().__init__()
        self.client = client
        self.prompt = prompt
        self.system_context = system_context
        self.is_running = True
        
    def run(self):
        """Get response from AI API"""
        try:
            if self.is_running:
                response = self.client.get_response(self.prompt, self.system_context)
                if self.is_running:
                    self.response_received.emit(response)
        except Exception as e:
            if self.is_running:
                self.response_received.emit(f"Error getting response: {str(e)}")
    
    def stop(self):
        """Signal the thread to stop"""
        self.is_running = False