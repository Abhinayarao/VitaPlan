"""
Firebase Authentication for VitaPlan
Handles user login, signup, and session management
"""
import pyrebase
from firebase_config import FIREBASE_CONFIG
from flask import session
import json
from typing import Dict, Optional

class FirebaseAuth:
    def __init__(self):
        """Initialize Firebase Auth"""
        self.config = FIREBASE_CONFIG
        self.firebase = pyrebase.initialize_app(self.config)
        self.auth = self.firebase.auth()
    
    def signup(self, email: str, password: str, user_data: Dict) -> Dict:
        """Create new user account"""
        try:
            # Create user with email and password
            user = self.auth.create_user_with_email_and_password(email, password)
            
            # Update user profile with additional data
            user_info = {
                "name": user_data.get("name", ""),
                "age": user_data.get("age", 0),
                "gender": user_data.get("gender", ""),
                "height": user_data.get("height", 0),
                "weight": user_data.get("weight", 0),
                "bmi": user_data.get("bmi", 0),
                "health_conditions": user_data.get("health_conditions", []),
                "allergies": user_data.get("allergies", []),
                "dietary_preferences": user_data.get("dietary_preferences", [])
            }
            
            return {
                "success": True,
                "user_id": user["localId"],
                "user_info": user_info,
                "message": "Account created successfully!"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create account. Please try again."
            }
    
    def login(self, email: str, password: str) -> Dict:
        """Login user with email and password"""
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            
            return {
                "success": True,
                "user_id": user["localId"],
                "email": user["email"],
                "message": "Login successful!"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Login failed. Please check your credentials."
            }
    
    def logout(self) -> Dict:
        """Logout current user"""
        try:
            session.clear()
            return {
                "success": True,
                "message": "Logged out successfully!"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Logout failed."
            }
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current logged-in user"""
        try:
            if 'user_id' in session:
                return {
                    "user_id": session['user_id'],
                    "email": session.get('email', ''),
                    "is_authenticated": True
                }
            return None
        except Exception as e:
            print(f"Error getting current user: {e}")
            return None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return 'user_id' in session and session['user_id'] is not None
