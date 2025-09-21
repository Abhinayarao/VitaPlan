"""
Smart Daily Interaction Handler
Determines what action to take based on user's daily status and timing
"""

from daily_tracker import DailyTracker
from ai_agents import UserDataCollectionAgent, DietPlanningAgent, FeedbackCollectionAgent
from database import Database
from typing import Dict, Optional
from datetime import date

class SmartDailyHandler:
    """Handles smart daily interactions based on user status and timing"""
    
    def __init__(self, db: Database):
        self.db = db
        self.daily_tracker = DailyTracker(db)
        self.user_agent = UserDataCollectionAgent(db)
        self.diet_agent = DietPlanningAgent(db)
        self.feedback_agent = FeedbackCollectionAgent(db)
    
    def handle_daily_interaction(self, user_id: str, user_input: str, target_date: str = None) -> Dict:
        """Handle daily interaction based on user status and timing"""
        if not target_date:
            target_date = date.today().isoformat()
        
        # Get user's daily status
        daily_status = self.daily_tracker.get_user_daily_status(user_id, target_date)
        
        # Check if user exists
        user_profile = self.db.get_user(user_id)
        if not user_profile:
            # User doesn't exist, collect their information
            return self.user_agent.collect_user_data(user_id, user_input)
        
        # Determine what action to take based on daily status
        if self._should_collect_feedback(daily_status, user_input):
            return self._handle_feedback_collection(user_id, user_input, target_date)
        elif self._should_create_diet_plan(daily_status, user_input):
            return self._handle_diet_plan_creation(user_id, user_input, target_date)
        elif self._should_show_existing_plan(daily_status, user_input):
            return self._handle_existing_plan(user_id, target_date)
        else:
            # Default: create new diet plan
            return self._handle_diet_plan_creation(user_id, user_input, target_date)
    
    def get_smart_greeting(self, user_id: str, target_date: str = None) -> str:
        """Get smart greeting based on daily status"""
        if not target_date:
            target_date = date.today().isoformat()
        
        # Check if user exists
        user_profile = self.db.get_user(user_id)
        if not user_profile:
            return self._generate_ai_greeting("new_user", None, target_date)
        
        # Get daily status
        daily_status = self.daily_tracker.get_user_daily_status(user_id, target_date)
        
        # Generate AI-powered greeting based on daily status
        return self._generate_ai_greeting("existing_user", daily_status, target_date)
    
    def _generate_ai_greeting(self, user_type: str, daily_status: Dict = None, target_date: str = None) -> str:
        """Generate AI-powered greeting message"""
        try:
            if user_type == "new_user":
                prompt = f"""Generate a warm, welcoming greeting for a new user joining VitaPlan, an AI-powered diet planning assistant. 
                The greeting should be friendly, encouraging, and explain that they need to provide their health information to get started.
                Keep it concise and professional."""
            else:
                # Generate greeting based on daily status
                status_info = ""
                if daily_status:
                    if daily_status['is_new_day']:
                        status_info = "It's a new day"
                        if daily_status['has_feedback']:
                            status_info += " and you provided feedback yesterday"
                    elif daily_status['has_diet_plan'] and not daily_status['has_feedback']:
                        status_info = "You have today's diet plan but haven't provided feedback yet"
                    else:
                        status_info = "You're continuing your diet journey"
                
                prompt = f"""Generate a personalized greeting for an existing VitaPlan user. 
                Context: {status_info}
                The greeting should be encouraging, check on their progress, and naturally guide them to the next appropriate action.
                Keep it warm, professional, and motivating."""
            
            return self.agent_manager.gemini_client.generate_text(prompt, max_tokens=100)
            
        except Exception as e:
            print(f"Error generating AI greeting: {e}")
            # Minimal fallback - just return a simple message
            return "Hello! Welcome to VitaPlan."
    
    def generate_daily_status_message(self, user_id: str, daily_status: Dict) -> str:
        """Generate user-friendly daily status message using AI"""
        try:
            # Create a conversational prompt based on the daily status
            status_info = f"""
            User's daily status for {daily_status['date']}:
            - Has diet plan: {daily_status['has_diet_plan']}
            - Has provided feedback: {daily_status['has_feedback']}
            - Is new day: {daily_status['is_new_day']}
            - Days since last interaction: {daily_status['days_since_last_interaction']}
            - Last interaction: {daily_status.get('last_interaction', 'Never')}
            """
            
            prompt = f"""Generate a friendly, conversational daily status update for a user based on this information:
            {status_info}
            
            The message should be:
            - Warm and encouraging
            - Focus on what they've accomplished
            - Suggest next steps naturally
            - Avoid technical jargon
            - Be concise but informative
            
            Examples of tone:
            - "Great job! You have your diet plan ready for today..."
            - "I see you're making progress with your nutrition journey..."
            - "Let's check in on how your day is going..."
            
            Response:"""
            
            return self.user_agent.generate_ai_response(prompt, max_tokens=150)
            
        except Exception as e:
            print(f"Error generating daily status message: {e}")
            # Fallback to simple message
            if daily_status['has_diet_plan'] and not daily_status['has_feedback']:
                return "Great! You have your diet plan ready for today. How is it going so far? I'd love to hear your feedback!"
            elif daily_status['has_diet_plan'] and daily_status['has_feedback']:
                return "Excellent! You're staying on track with both your diet plan and feedback. Keep up the great work!"
            elif not daily_status['has_diet_plan']:
                return "Ready to start your day? I can create a personalized diet plan for you!"
            else:
                return "Let's check in on your nutrition journey today!"
    
    def _should_collect_feedback(self, daily_status: Dict, user_input: str) -> bool:
        """Determine if we should collect feedback"""
        # NEVER automatically collect feedback on page load or initial greeting
        # Only collect feedback when user explicitly asks for it
        
        # Check for explicit feedback-related keywords
        feedback_keywords = ['feedback', 'give feedback', 'provide feedback', 'tell you about', 'how was', 'how did', 'followed', 'didn\'t follow']
        user_input_lower = user_input.lower()
        
        # Only collect feedback if user explicitly mentions it
        has_feedback_keywords = any(keyword in user_input_lower for keyword in feedback_keywords)
        
        return has_feedback_keywords
    
    def _should_create_diet_plan(self, daily_status: Dict, user_input: str) -> bool:
        """Determine if we should create a new diet plan"""
        # Check for diet plan request keywords
        plan_keywords = ['diet plan', 'meal plan', 'food', 'eat', 'breakfast', 'lunch', 'dinner', 'today', 'tomorrow']
        user_input_lower = user_input.lower()
        
        has_plan_keywords = any(keyword in user_input_lower for keyword in plan_keywords)
        
        return (not daily_status['has_diet_plan'] or 
                daily_status['is_new_day'] or 
                has_plan_keywords)
    
    def _should_show_existing_plan(self, daily_status: Dict, user_input: str) -> bool:
        """Determine if we should show existing plan"""
        # Check for plan viewing keywords
        view_keywords = ['show', 'view', 'see', 'my plan', 'today\'s plan', 'current plan']
        user_input_lower = user_input.lower()
        
        has_view_keywords = any(keyword in user_input_lower for keyword in view_keywords)
        
        return (daily_status['has_diet_plan'] and 
                not daily_status['is_new_day'] and 
                has_view_keywords)
    
    def _handle_feedback_collection(self, user_id: str, user_input: str, target_date: str) -> Dict:
        """Handle feedback collection"""
        return self.feedback_agent.collect_feedback(user_id, user_input, target_date)
    
    def _handle_diet_plan_creation(self, user_id: str, user_input: str, target_date: str) -> Dict:
        """Handle diet plan creation"""
        return self.diet_agent.create_diet_plan(user_id, target_date)
    
    def _handle_existing_plan(self, user_id: str, target_date: str) -> Dict:
        """Handle showing existing plan"""
        existing_plan = self.db.get_diet_plan(user_id, target_date)
        if existing_plan:
            response = f"Here's your diet plan for {target_date}:\n\n{self.diet_agent._format_meal_plan(existing_plan['meal_plan'])}"
            self.diet_agent.log_conversation(user_id, response, "agent_response")
            return {
                'status': 'success',
                'message': response,
                'meal_plan': existing_plan['meal_plan']
            }
        else:
            return self._handle_diet_plan_creation(user_id, "", target_date)

