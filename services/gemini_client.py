import os
import requests

class GeminiAPIClient:
    """Simple client for Google's Gemini API"""
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
    def get_response(self, prompt, system_context=None):
        if not self.api_key:
            return "No API key provided. Please add your Gemini API key in the settings."
            
        headers = {
            "Content-Type": "application/json"
        }
        
        # Building the request payload according to Gemini API requirements
        data = {
            "contents": [],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024
            }
        }
        
        # Add system instruction if provided
        if system_context:
            data["systemInstruction"] = {
                "parts": [{"text": system_context}]
            }
        
        # Add user message
        data["contents"].append({
            "role": "user",
            "parts": [{"text": prompt}]
        })
            
        try:
            url = f"{self.base_url}?key={self.api_key}"
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            if "candidates" in result and result["candidates"]:
                text_parts = []
                for part in result["candidates"][0]["content"]["parts"]:
                    if "text" in part:
                        text_parts.append(part["text"])
                return "\n".join(text_parts)
            else:
                return "No response generated. Please try again."
                
        except requests.exceptions.RequestException as e:
            return f"API error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"