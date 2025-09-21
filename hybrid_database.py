"""
Firebase-Only Database Class
Uses Firebase Firestore as the only database
"""
from firebase_client import FirebaseClient
from typing import Dict, List, Optional
import os

class HybridDatabase:
    def __init__(self, use_firebase: bool = True):
        """Initialize Firebase-only database"""
        if not use_firebase:
            raise ValueError("Firebase-only mode: use_firebase must be True")
        
        if not self._check_firebase_config():
            raise ValueError("Firebase configuration missing. Please check your setup.")
        
        try:
            self.firebase = FirebaseClient()
            print("🔥 Using Firebase Firestore as database")
        except Exception as e:
            raise ValueError(f"Firebase initialization failed: {e}. Please check your service account file.")
    
    def _check_firebase_config(self) -> bool:
        """Check if Firebase is properly configured"""
        required_files = ["firebase-service-account.json"]
        required_env_vars = ["FIREBASE_PROJECT_ID"]
        
        # Check for service account file
        if not os.path.exists("firebase-service-account.json"):
            print("⚠️ Firebase service account file not found")
            return False
        
        # Check for environment variables
        for var in required_env_vars:
            if not os.getenv(var):
                print(f"⚠️ Firebase environment variable {var} not set")
                return False
        
        return True
    
    def create_user(self, user_id: str, name: str, age: int, gender: str, 
                   height: float = None, weight: float = None, bmi: float = None,
                   health_conditions: List[str] = None, allergies: List[str] = None, 
                   dietary_preferences: List[str] = None) -> bool:
        """Create a new user in Firebase"""
        user_data = {
            "user_id": user_id,
            "name": name,
            "age": age,
            "gender": gender,
            "height": height,
            "weight": weight,
            "bmi": bmi,
            "health_conditions": health_conditions or [],
            "allergies": allergies or [],
            "dietary_preferences": dietary_preferences or []
        }
        
        try:
            result = self.firebase.create_user(user_data)
            return result is not None
        except Exception as e:
            print(f"Firebase error: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID from Firebase"""
        try:
            return self.firebase.get_user(user_id)
        except Exception as e:
            print(f"Firebase error: {e}")
            return None
    
    def add_conversation(self, user_id: str, agent_name: str, message: str, message_type: str) -> bool:
        """Add conversation entry to Firebase"""
        try:
            return self.firebase.add_conversation(user_id, agent_name, message, message_type)
        except Exception as e:
            print(f"Firebase error: {e}")
            return False
    
    def get_conversations(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user conversations from Firebase"""
        try:
            return self.firebase.get_conversations(user_id, limit)
        except Exception as e:
            print(f"Firebase error: {e}")
            return []
    
    def save_diet_plan(self, user_id: str, plan_date: str, meal_plan: Dict) -> bool:
        """Save diet plan to Firebase"""
        try:
            return self.firebase.save_diet_plan(user_id, plan_date, meal_plan)
        except Exception as e:
            print(f"Firebase error: {e}")
            return False
    
    def get_diet_plan(self, user_id: str, plan_date: str) -> Optional[Dict]:
        """Get diet plan from Firebase"""
        try:
            return self.firebase.get_diet_plan(user_id, plan_date)
        except Exception as e:
            print(f"Firebase error: {e}")
            return None
    
    def save_feedback(self, user_id: str, plan_date: str, feedback: Dict, adherence_score: float) -> bool:
        """Save user feedback to Firebase"""
        try:
            return self.firebase.save_feedback(user_id, plan_date, feedback, adherence_score)
        except Exception as e:
            print(f"Firebase error: {e}")
            return False
    
    def get_feedback(self, user_id: str, plan_date: str) -> Optional[Dict]:
        """Get user feedback from Firebase"""
        try:
            return self.firebase.get_feedback(user_id, plan_date)
        except Exception as e:
            print(f"Firebase error: {e}")
            return None
    
    def get_user_diet_history(self, user_id: str, limit: int = 30) -> List[Dict]:
        """Get user's diet plan history from Firebase"""
        try:
            return self.firebase.get_user_diet_history(user_id, limit)
        except Exception as e:
            print(f"Firebase error: {e}")
            return []
    
    def update_diet_feedback(self, user_id: str, plan_date: str, feedback: Dict, adherence_score: float) -> bool:
        """Update diet plan with feedback"""
        try:
            return self.firebase.update_diet_feedback(user_id, plan_date, feedback, adherence_score)
        except Exception as e:
            print(f"Firebase error: {e}")
            return False
