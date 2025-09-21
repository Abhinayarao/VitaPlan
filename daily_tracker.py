"""
Daily Tracking System for VitaPlan
Handles daily interactions, feedback collection, and progress tracking
"""

from database import Database
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import json

class DailyTracker:
    """Handles daily tracking and feedback collection"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_user_daily_status(self, user_id: str, target_date: str = None) -> Dict:
        """Get user's daily status for a specific date"""
        if not target_date:
            target_date = date.today().isoformat()
        
        # Check if user has a diet plan for this date
        diet_plan = self.db.get_diet_plan(user_id, target_date)
        
        # Check if user has provided feedback for this date
        feedback = self._get_daily_feedback(user_id, target_date)
        
        # Get user's last interaction date
        last_interaction = self._get_last_interaction_date(user_id)
        
        return {
            'date': target_date,
            'has_diet_plan': diet_plan is not None,
            'has_feedback': feedback is not None,
            'last_interaction': last_interaction,
            'diet_plan': diet_plan,
            'feedback': feedback,
            'is_new_day': self._is_new_day(user_id, target_date),
            'days_since_last_interaction': self._days_since_last_interaction(user_id, target_date)
        }
    
    def should_collect_feedback(self, user_id: str, target_date: str = None) -> bool:
        """Determine if we should collect feedback for a specific date"""
        if not target_date:
            target_date = date.today().isoformat()
        
        status = self.get_user_daily_status(user_id, target_date)
        
        # Collect feedback if:
        # 1. User has a diet plan for this date
        # 2. User hasn't provided feedback yet
        # 3. It's the end of the day (after 6 PM) or next day
        return (status['has_diet_plan'] and 
                not status['has_feedback'] and 
                self._should_prompt_for_feedback(target_date))
    
    def should_create_new_plan(self, user_id: str, target_date: str = None) -> bool:
        """Determine if we should create a new diet plan for a specific date"""
        if not target_date:
            target_date = date.today().isoformat()
        
        status = self.get_user_daily_status(user_id, target_date)
        
        # Create new plan if:
        # 1. User doesn't have a plan for this date
        # 2. It's a new day
        return not status['has_diet_plan'] or status['is_new_day']
    
    def get_feedback_prompt(self, user_id: str, target_date: str = None) -> str:
        """Generate appropriate feedback prompt based on timing"""
        if not target_date:
            target_date = date.today().isoformat()
        
        status = self.get_user_daily_status(user_id, target_date)
        days_since = status['days_since_last_interaction']
        
        if days_since == 0:
            return "How did you follow today's diet plan? Please share your feedback so I can improve tomorrow's recommendations."
        elif days_since == 1:
            return "I noticed you haven't provided feedback for yesterday's diet plan. How did it go? This helps me create better recommendations for you."
        else:
            return f"It's been {days_since} days since we last connected. How have you been following your diet plans? I'd love to hear your feedback to improve my recommendations."
    
    def get_greeting_message(self, user_id: str, target_date: str = None) -> str:
        """Generate appropriate greeting based on daily status"""
        if not target_date:
            target_date = date.today().isoformat()
        
        status = self.get_user_daily_status(user_id, target_date)
        days_since = status['days_since_last_interaction']
        
        if days_since == 0:
            if status['has_diet_plan'] and not status['has_feedback']:
                return "Welcome back! I see you have today's diet plan. How is it going so far?"
            elif status['has_diet_plan'] and status['has_feedback']:
                return "Great to see you again! I have your feedback from today. Would you like me to create tomorrow's plan based on your feedback?"
            else:
                return "Welcome back! Let me create today's personalized diet plan for you."
        elif days_since == 1:
            return "Welcome back! I missed you yesterday. Let me check how you're doing and create today's diet plan."
        else:
            return f"Welcome back! It's been {days_since} days since we last connected. Let me create a fresh diet plan for you today."
    
    def _get_daily_feedback(self, user_id: str, target_date: str) -> Optional[Dict]:
        """Get feedback for a specific date"""
        try:
            return self.db.get_feedback(user_id, target_date)
        except Exception as e:
            print(f"Error getting daily feedback: {e}")
            return None
    
    def _get_last_interaction_date(self, user_id: str) -> Optional[str]:
        """Get the last interaction date for a user"""
        try:
            # Get conversations from Firebase and find the latest one
            conversations = self.db.get_conversations(user_id, limit=1)
            if conversations:
                # Get the timestamp from the latest conversation
                latest_conversation = conversations[0]
                if 'timestamp' in latest_conversation:
                    # Convert timestamp to date string
                    timestamp = latest_conversation['timestamp']
                    if hasattr(timestamp, 'date'):
                        return timestamp.date().isoformat()
                    elif isinstance(timestamp, str):
                        # Parse the timestamp string and extract date
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            return dt.date().isoformat()
                        except:
                            return None
            return None
        except Exception as e:
            print(f"Error getting last interaction date: {e}")
            return None
    
    def _is_new_day(self, user_id: str, target_date: str) -> bool:
        """Check if this is a new day for the user"""
        try:
            # Check if there's already a diet plan for this date
            existing_plan = self.db.get_diet_plan(user_id, target_date)
            if existing_plan:
                return False  # Not a new day if plan already exists
            
            # Check last interaction date
            last_interaction = self._get_last_interaction_date(user_id)
            if not last_interaction:
                return True  # New user
            
            last_date = datetime.strptime(last_interaction, '%Y-%m-%d').date()
            target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
            
            return target_date_obj > last_date
        except Exception as e:
            print(f"Error checking if new day: {e}")
            return False  # Default to not new day to avoid creating duplicate plans
    
    def _days_since_last_interaction(self, user_id: str, target_date: str) -> int:
        """Calculate days since last interaction"""
        last_interaction = self._get_last_interaction_date(user_id)
        if not last_interaction:
            return 999  # Large number for new users
        
        last_date = datetime.strptime(last_interaction, '%Y-%m-%d').date()
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        return (target_date_obj - last_date).days
    
    def _should_prompt_for_feedback(self, target_date: str) -> bool:
        """Determine if we should prompt for feedback based on timing"""
        try:
            target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
            today = date.today()
            
            # Only prompt for feedback if it's a new day (next day)
            # This prevents immediate feedback requests
            if target_date_obj > today:
                return True
            
            # For same day or past days, don't prompt immediately
            # Let user naturally provide feedback
            return False
        except:
            return False  # Default to not prompting for feedback

