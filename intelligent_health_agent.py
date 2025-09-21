"""
Intelligent Health Data Collection Agent
Uses AI to intelligently collect comprehensive health information
"""

from base_agent import AIAgent
from database import Database
from typing import Dict, List, Optional
import json

class IntelligentHealthAgent(AIAgent):
    """AI Agent for intelligent health data collection"""
    
    def __init__(self, db: Database):
        super().__init__("IntelligentHealthAgent", db)
    
    def collect_comprehensive_health_data(self, user_id: str, user_input: str) -> Dict:
        """Intelligently collect comprehensive health information using AI"""
        try:
            # Create AI prompt for comprehensive health data collection
            prompt = f"""You are an expert health assistant collecting comprehensive health information. 
            The user said: "{user_input}"
            
            Please respond in a conversational way to collect their:
            - Name
            - Age
            - Gender
            - Height (in cm or feet/inches)
            - Weight (in kg or lbs)
            - Health conditions (diabetes, cardiac issues, hypertension, thyroid, etc.)
            - Allergies
            - Dietary preferences (vegetarian, vegan, gluten-free, etc.)
            - Activity level (sedentary, light, moderate, active, very active)
            - Health goals (weight loss, weight gain, muscle building, maintenance, etc.)
            
            IMPORTANT: 
            - Only ask about PCOD/PCOS if the user is female
            - Ask for height and weight to calculate BMI
            - Be conversational and ask follow-up questions naturally
            - If they provide complete information, acknowledge it and say you'll create a personalized diet plan
            
            Response:"""
            
            # Generate AI response
            ai_response = self.generate_ai_response(prompt, 300)
            
            # Try to extract structured data from user input
            user_data = self._extract_comprehensive_health_data(user_input)
            
            
            if user_data and all(key in user_data for key in ['name', 'age', 'gender']):
                # Calculate BMI if height and weight are provided
                bmi = self._calculate_bmi(user_data.get('height'), user_data.get('weight'))
                
                # Ensure age is a valid integer
                try:
                    age = int(user_data['age']) if user_data['age'] is not None else 30
                except (ValueError, TypeError):
                    age = 30
                
                # Save user data
                success = self.db.create_user(
                    user_id=user_id,
                    name=user_data['name'],
                    age=age,
                    gender=user_data['gender'],
                    height=user_data.get('height'),
                    weight=user_data.get('weight'),
                    bmi=bmi,
                    health_conditions=user_data.get('health_conditions', []),
                    allergies=user_data.get('allergies', []),
                    dietary_preferences=user_data.get('dietary_preferences', [])
                )
                
                if success:
                    # Check if we have complete information
                    has_height_weight = user_data.get('height') and user_data.get('weight')
                    
                    if has_height_weight:
                        # Complete information - acknowledge and offer to create diet plan
                        response_prompt = f"""The user provided complete health information:
                        Name: {user_data['name']}
                        Age: {age}
                        Gender: {user_data['gender']}
                        Height: {user_data.get('height')} cm
                        Weight: {user_data.get('weight')} kg
                        BMI: {bmi}
                        Health conditions: {', '.join(user_data.get('health_conditions', [])) if user_data.get('health_conditions') else 'None'}
                        Allergies: {', '.join(user_data.get('allergies', [])) if user_data.get('allergies') else 'None'}
                        Dietary preferences: {', '.join(user_data.get('dietary_preferences', [])) if user_data.get('dietary_preferences') else 'None'}
                        
                        Respond in a friendly, professional way acknowledging their complete health profile and offering to create a personalized diet plan based on their BMI, health conditions, and dietary preferences.
                        
                        Response:"""
                    else:
                        # Missing height/weight - ask for them specifically
                        response_prompt = f"""The user provided partial health information:
                        Name: {user_data['name']}
                        Age: {age}
                        Gender: {user_data['gender']}
                        Health conditions: {', '.join(user_data.get('health_conditions', [])) if user_data.get('health_conditions') else 'None'}
                        Allergies: {', '.join(user_data.get('allergies', [])) if user_data.get('allergies') else 'None'}
                        Dietary preferences: {', '.join(user_data.get('dietary_preferences', [])) if user_data.get('dietary_preferences') else 'None'}
                        
                        Respond in a friendly, professional way acknowledging their information but explaining that you need their height and weight to calculate BMI and create a personalized diet plan. Ask them to provide their height (in cm or feet/inches) and weight (in kg or lbs).
                        
                        Response:"""
                    
                    ai_response = self.generate_ai_response(response_prompt, 200)
            
            self.log_conversation(user_id, ai_response, "agent_response")
            
            return {
                'status': 'success',
                'message': ai_response,
                'user_data': user_data if 'user_data' in locals() else None
            }
            
        except Exception as e:
            error_prompt = f"""I encountered an error while processing your health information: {str(e)}. 
            Please try again with your health details, and I'll help you create a personalized diet plan.
            
            Response:"""
            
            ai_response = self.generate_ai_response(error_prompt, 150)
            self.log_conversation(user_id, ai_response, "agent_response")
            
            return {
                'status': 'error',
                'message': ai_response
            }
    
    def _extract_comprehensive_health_data(self, user_input: str) -> Optional[Dict]:
        """Extract comprehensive health data from user input using AI"""
        try:
            # Create AI prompt for comprehensive data extraction
            prompt = f"""Extract comprehensive health information from this text: "{user_input}"
            
            Return a JSON object with:
            - name: (string)
            - age: (number)
            - gender: (string)
            - height: (number in cm, convert from feet/inches if needed - e.g., 5'10" = 178, 6'2" = 188)
            - weight: (number in kg, convert from lbs if needed - e.g., 150 lbs = 68, 200 lbs = 91)
            - health_conditions: (array of strings)
            - allergies: (array of strings)
            - dietary_preferences: (array of strings like "vegetarian", "vegan", "gluten-free")
            - activity_level: (string like "sedentary", "light", "moderate", "active", "very active")
            - health_goals: (array of strings like "weight loss", "weight gain", "muscle building", "maintenance")
            
            IMPORTANT: Extract numeric values for height and weight. Convert units:
            - Height: feet'inches" to cm (1 foot = 30.48 cm, 1 inch = 2.54 cm)
            - Weight: lbs to kg (1 lb = 0.453592 kg)
            - If already in cm/kg, use as is
            
            If information is missing, use null. Only return valid JSON.
            
            JSON:"""
            
            ai_response = self.generate_ai_response(prompt, 200)
            
            # Try to parse JSON from AI response
            if '{' in ai_response and '}' in ai_response:
                json_start = ai_response.find('{')
                json_end = ai_response.rfind('}') + 1
                json_str = ai_response[json_start:json_end]
                return json.loads(json_str)
            
            return None
            
        except Exception as e:
            print(f"Data extraction error: {e}")
            return None
    
    def _calculate_bmi(self, height: float, weight: float) -> Optional[float]:
        """Calculate BMI from height and weight"""
        try:
            if height and weight and height > 0 and weight > 0:
                # BMI = weight(kg) / height(m)^2
                height_m = height / 100  # Convert cm to meters
                bmi = weight / (height_m ** 2)
                return round(bmi, 1)
            return None
        except (TypeError, ValueError, ZeroDivisionError):
            return None
    
    def get_bmi_category(self, bmi: float) -> str:
        """Get BMI category"""
        if bmi < 18.5:
            return "underweight"
        elif bmi < 25:
            return "normal weight"
        elif bmi < 30:
            return "overweight"
        else:
            return "obese"
