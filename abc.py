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