"""
Base AI Agent class
"""

from database import Database
from gemini_client import GeminiClient
from typing import Dict

class AIAgent:
    """Base class for AI-powered agents"""
    def __init__(self, name: str, db: Database):
        self.name = name
        self.db = db
        self.gemini_client = GeminiClient()
    
    def log_conversation(self, user_id: str, message: str, message_type: str):
        """Log conversation to database"""
        self.db.add_conversation(user_id, self.name, message, message_type)
    
    def generate_ai_response(self, prompt: str, max_tokens: int = 300) -> str:
        """Generate AI response using Google Gemini Pro"""
        try:
            response = self.gemini_client.generate_text(prompt, max_tokens)
            return response
        except Exception as e:
            print(f"AI generation error: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."



