"""
Firebase Client for VitaPlan
Handles authentication and Firestore operations
"""
import firebase_admin
from firebase_admin import credentials, firestore, auth
from firebase_config import FIREBASE_CONFIG, COLLECTIONS
from datetime import datetime
from typing import Dict, List, Optional
import json
import uuid

class FirebaseClient:
    def __init__(self):
        """Initialize Firebase client"""
        if not firebase_admin._apps:
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate("firebase-service-account.json")
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
        self.collections = COLLECTIONS
    
    def create_user(self, user_data: Dict) -> str:
        """Create a new user in Firestore"""
        try:
            user_id = user_data.get("user_id")
            if not user_id:
                # Generate a new user_id if not provided
                user_id = str(uuid.uuid4())
                user_data["user_id"] = user_id
            
            user_ref = self.db.collection(self.collections["users"]).document(user_id)
            
            user_data["created_at"] = datetime.now()
            user_data["updated_at"] = datetime.now()
            
            user_ref.set(user_data)
            return user_id
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user data from Firestore"""
        try:
            user_doc = self.db.collection(self.collections["users"]).document(user_id).get()
            if user_doc.exists:
                return user_doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_user(self, user_id: str, user_data: Dict) -> bool:
        """Update user data in Firestore"""
        try:
            user_data["updated_at"] = datetime.now()
            self.db.collection(self.collections["users"]).document(user_id).update(user_data)
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def add_conversation(self, user_id: str, agent_name: str, message: str, message_type: str) -> bool:
        """Add conversation to Firestore"""
        try:
            conversation_data = {
                "user_id": user_id,
                "agent_name": agent_name,
                "message": message,
                "message_type": message_type,
                "timestamp": datetime.now()
            }
            
            self.db.collection(self.collections["conversations"]).add(conversation_data)
            return True
        except Exception as e:
            print(f"Error adding conversation: {e}")
            return False
    
    def get_conversations(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user conversations from Firestore"""
        try:
            conversations = (self.db.collection(self.collections["conversations"])
                           .where(filter=firestore.FieldFilter("user_id", "==", user_id))
                           .limit(limit)
                           .stream())
            
            # Convert to list and sort by timestamp
            conv_list = [doc.to_dict() for doc in conversations]
            conv_list.sort(key=lambda x: x.get('timestamp', datetime.min), reverse=True)
            return conv_list
        except Exception as e:
            print(f"Error getting conversations: {e}")
            return []
    
    def save_diet_plan(self, user_id: str, plan_date: str, meal_plan: Dict) -> bool:
        """Save diet plan to Firestore"""
        try:
            diet_plan_data = {
                "user_id": user_id,
                "plan_date": plan_date,
                "meal_plan": meal_plan,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Use plan_date as document ID for easy querying
            doc_id = f"{user_id}_{plan_date}"
            print(f"FIREBASE: Saving diet plan with doc_id: {doc_id}")
            print(f"FIREBASE: Diet plan data: {diet_plan_data}")
            
            self.db.collection(self.collections["diet_plans"]).document(doc_id).set(diet_plan_data)
            
            # Verify the save by immediately reading it back
            saved_doc = self.db.collection(self.collections["diet_plans"]).document(doc_id).get()
            print(f"FIREBASE: Save verification - Document exists: {saved_doc.exists}")
            
            return True
        except Exception as e:
            print(f"Error saving diet plan: {e}")
            return False
    
    def get_diet_plan(self, user_id: str, plan_date: str) -> Optional[Dict]:
        """Get diet plan from Firestore"""
        try:
            doc_id = f"{user_id}_{plan_date}"
            print(f"FIREBASE: Getting diet plan with doc_id: {doc_id}")
            
            doc_ref = self.db.collection(self.collections["diet_plans"]).document(doc_id)
            doc = doc_ref.get()
            
            print(f"FIREBASE: Document exists: {doc.exists}")
            if doc.exists:
                data = doc.to_dict()
                print(f"FIREBASE: Retrieved data: {data}")
                return data
            else:
                print(f"FIREBASE: No document found for {doc_id}")
            return None
        except Exception as e:
            print(f"Error getting diet plan: {e}")
            return None
    
    def save_feedback(self, user_id: str, plan_date: str, feedback: Dict, adherence_score: float) -> bool:
        """Save user feedback to Firestore"""
        try:
            feedback_data = {
                "user_id": user_id,
                "plan_date": plan_date,
                "feedback": feedback,
                "adherence_score": adherence_score,
                "created_at": datetime.now()
            }
            
            self.db.collection(self.collections["feedback"]).document(f"{user_id}_{plan_date}").set(feedback_data)
            return True
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return False
    
    def get_feedback(self, user_id: str, plan_date: str) -> Optional[Dict]:
        """Get user feedback from Firestore"""
        try:
            doc_ref = self.db.collection(self.collections["feedback"]).document(f"{user_id}_{plan_date}")
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting feedback: {e}")
            return None
    
    def get_user_diet_history(self, user_id: str, limit: int = 30) -> List[Dict]:
        """Get user's diet plan history from Firestore"""
        try:
            diet_plans = (self.db.collection(self.collections["diet_plans"])
                         .where(filter=firestore.FieldFilter("user_id", "==", user_id))
                         .order_by("plan_date", direction=firestore.Query.DESCENDING)
                         .limit(limit)
                         .stream())
            
            return [doc.to_dict() for doc in diet_plans]
        except Exception as e:
            print(f"Error getting diet history: {e}")
            return []
    
    def update_diet_feedback(self, user_id: str, plan_date: str, feedback: Dict, adherence_score: float) -> bool:
        """Update diet plan with feedback"""
        try:
            # Update the diet plan document with feedback
            diet_plan_ref = self.db.collection(self.collections["diet_plans"]).document(f"{user_id}_{plan_date}")
            
            # Get the current diet plan
            diet_plan_doc = diet_plan_ref.get()
            if not diet_plan_doc.exists:
                print(f"Diet plan not found for {user_id} on {plan_date}")
                return False
            
            # Update with feedback
            diet_plan_ref.update({
                "feedback": feedback,
                "adherence_score": adherence_score,
                "updated_at": datetime.now()
            })
            
            return True
        except Exception as e:
            print(f"Error updating diet feedback: {e}")
            return False
