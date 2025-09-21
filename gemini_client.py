"""
Google Gemini AI Client for Diet Planning
Uses Gemini Pro for all AI responses - FREE and reliable!
"""

from google import genai
from typing import Dict, List, Optional
import json
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "AIzaS")
        if not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in environment variables")

        # Create the Gemini client
        self.client = genai.Client(api_key=self.api_key)

        # Default model
        self.model_name = "gemini-1.5-flash"

    def generate_text(self, prompt: str, max_tokens: int = 300) -> str:
        """
        Generate text using Google Gemini
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "max_output_tokens": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40
                }
            )
            return response.text.strip()
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            raise Exception(f"AI service temporarily unavailable: {str(e)}")
    
    def generate_diet_plan(self, user_profile: Dict, previous_feedback: Optional[Dict] = None) -> Dict:
        """
        Generate a personalized diet plan using Gemini
        """
        try:
            # Create a detailed prompt for diet planning
            prompt = self._create_diet_prompt(user_profile, previous_feedback)
            
            # Generate the diet plan
            ai_response = self.generate_text(prompt, max_tokens=500)
            
            # Parse the response into structured format
            meal_plan = self._parse_diet_plan(ai_response)
            
            return meal_plan
            
        except Exception as e:
            print(f"Error generating diet plan: {e}")
            # Raise exception instead of returning hardcoded fallback
            raise Exception(f"Failed to generate AI diet plan: {str(e)}")
    
    def modify_diet_plan(self, original_plan: Dict, unavailable_items: List[str], available_items: List[str] = None) -> Dict:
        """
        Modify an existing diet plan based on available/unavailable items using AI
        """
        try:
            # Create a detailed prompt for diet plan modification
            prompt = self._create_modification_prompt(original_plan, unavailable_items, available_items)
            
            # Debug: Print the modification prompt
            print(f"Modification prompt: {prompt}")
            
            # Generate the modified diet plan
            ai_response = self.generate_text(prompt, max_tokens=600)
            
            # Debug: Print the AI response
            print(f"Modification AI response: {ai_response}")
            
            # Parse the response into structured format
            modified_plan = self._parse_diet_plan(ai_response)
            
            return modified_plan
            
        except Exception as e:
            print(f"Error modifying diet plan: {e}")
            raise Exception(f"Failed to modify AI diet plan: {str(e)}")
    
    def _create_modification_prompt(self, original_plan: Dict, unavailable_items: List[str], available_items: List[str] = None) -> str:
        """Create AI prompt for diet plan modification"""
        
        # Format original plan for the prompt
        original_text = ""
        for meal_type, items in original_plan.items():
            if items and meal_type != 'notes':
                original_text += f"{meal_type.upper()}:\n"
                for item in items:
                    original_text += f"  - {item}\n"
                original_text += "\n"
        
        if original_plan.get('notes'):
            original_text += "NOTES:\n"
            for note in original_plan['notes']:
                original_text += f"  - {note}\n"
        
        unavailable_text = ", ".join(unavailable_items) if unavailable_items else "None"
        available_text = ", ".join(available_items) if available_items else "None"
        
        prompt = f"""You are an expert nutritionist. I need you to modify an existing diet plan based on ingredient availability.

ORIGINAL DIET PLAN:
{original_text}

CRITICAL REQUIREMENTS:
- UNAVAILABLE ITEMS (DO NOT USE): {unavailable_text}
- AVAILABLE ITEMS (YOU CAN USE): {available_text}

STRICT MODIFICATION RULES:
1. ABSOLUTELY DO NOT include any of the unavailable items in the new meal plan
2. If the original plan contains unavailable items, replace them completely with available alternatives
3. Use only available items or common substitutes
4. Maintain the same nutritional balance and meal structure
5. Keep the same meal types (breakfast, lunch, dinner, snacks)
6. Provide specific, practical alternatives that are easy to prepare
7. Update notes if needed

IMPORTANT: Double-check that NO unavailable items appear in your modified plan!

You MUST create a completely NEW meal plan that replaces any unavailable items. Do not return the same plan.

Format your response EXACTLY like this:

BREAKFAST:
- [specific meal with portions]

LUNCH:
- [specific meal with portions]

DINNER:
- [specific meal with portions]

SNACKS:
- [specific snack with portions]

NOTES:
- [any relevant notes]

Modified Meal Plan:"""
        
        return prompt
    
    def _create_diet_prompt(self, user_profile: Dict, previous_feedback: Optional[Dict] = None) -> str:
        """Create a detailed prompt for diet planning"""
        name = user_profile.get('name', 'User')
        age = user_profile.get('age', 30)
        gender = user_profile.get('gender', 'unknown')
        health_conditions = user_profile.get('health_conditions', [])
        allergies = user_profile.get('allergies', [])
        dietary_preferences = user_profile.get('dietary_preferences', [])
        
        # Get additional body metrics
        height = user_profile.get('height')
        weight = user_profile.get('weight')
        bmi = user_profile.get('bmi')
        weight_goal = user_profile.get('weight_goal')
        
        # Add variety and randomization to the prompt
        import random
        variety_instructions = [
            "Create a diverse and varied meal plan with different food combinations.",
            "Use a wide variety of ingredients and cooking methods for maximum nutritional diversity.",
            "Include different types of proteins, grains, and vegetables for a balanced approach.",
            "Vary the meal styles and preparation methods to keep the diet interesting.",
            "Create a unique meal combination that differs from typical diet plans."
        ]
        
        variety_instruction = random.choice(variety_instructions)
        
        # Add current time for additional variety
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        prompt = f"""You are an expert nutritionist and dietitian. Create a personalized diet plan for {name}, a {age}-year-old {gender}.

PLAN GENERATION TIME: {current_time}

Health Information:
- Health conditions: {', '.join(health_conditions) if health_conditions else 'None'}
- Allergies: {', '.join(allergies) if allergies else 'None'}
- Dietary preferences: {', '.join(dietary_preferences) if dietary_preferences else 'None'}

Body Metrics:
- Height: {height if height else 'Not provided'} cm
- Weight: {weight if weight else 'Not provided'} kg
- BMI: {bmi if bmi else 'Not calculated'}
- Weight Goal: {weight_goal.replace('_', ' ').title() if weight_goal else 'Not specified'}

Previous feedback: {previous_feedback.get('feedback_text', 'None') if previous_feedback else 'None'}

VARIETY REQUIREMENT: {variety_instruction}

IMPORTANT DIETARY RESTRICTIONS:
- If the user is vegetarian, DO NOT include any meat, poultry, or fish
- If the user is vegan, DO NOT include any animal products
- If the user is gluten-free, avoid wheat, barley, rye
- Always respect their dietary preferences and restrictions

BMI-BASED RECOMMENDATIONS:
- If BMI < 18.5 (underweight): Focus on nutrient-dense, calorie-rich foods
- If BMI 18.5-24.9 (normal): Maintain balanced nutrition
- If BMI 25-29.9 (overweight): Focus on portion control and weight management
- If BMI ≥ 30 (obese): Focus on calorie deficit and weight loss

WEIGHT GOAL-BASED RECOMMENDATIONS:
- Weight Loss: Create a calorie deficit with nutrient-dense, low-calorie foods, high protein, fiber-rich meals
- Weight Gain: Include calorie-dense, nutrient-rich foods, healthy fats, protein-rich snacks
- Maintain Weight: Focus on balanced macronutrients, portion control, regular meal timing
- Muscle Gain: High protein intake, complex carbohydrates, healthy fats, post-workout nutrition
- General Health: Emphasize whole foods, variety, balanced nutrition, hydration

        Please create a detailed meal plan with ONE specific meal for each category:
        1. BREAKFAST: One specific meal with detailed ingredients and exact portions
        2. LUNCH: One specific meal with detailed ingredients and exact portions  
        3. DINNER: One specific meal with detailed ingredients and exact portions
        4. SNACKS: One specific snack suggestion with portions
        5. NOTES: Important nutrition tips and recommendations
        
        VARIETY AND CREATIVITY REQUIREMENTS:
        - Use different ingredients and combinations each time
        - Vary cooking methods (grilled, baked, steamed, raw, etc.)
        - Include diverse protein sources (chicken, fish, beans, tofu, etc.)
        - Mix different types of grains and vegetables
        - Create unique flavor profiles and seasoning combinations
        - Avoid repetitive meal patterns
        
        Be specific about:
        - Exact foods and ingredients
        - Precise portions (e.g., "1 cup of brown rice", "150g grilled chicken breast")
        - Cooking methods
        - Timing suggestions
        
        Make each meal complete and balanced for the user's specific needs.
        IMPORTANT: Create a UNIQUE meal plan that differs from standard diet recommendations.
        
        IMPORTANT: Format your response EXACTLY as follows (use this exact format):
        
        BREAKFAST:
        - [one specific breakfast meal with detailed ingredients and portions]
        
        LUNCH:
        - [one specific lunch meal with detailed ingredients and portions]
        
        DINNER:
        - [one specific dinner meal with detailed ingredients and portions]
        
        SNACKS:
        - [one specific snack with portions]
        
        NOTES:
        - [important tip 1]
        - [important tip 2]
        
        Do NOT use JSON format. Use the exact format above with section headers and bullet points.
        Consider their health conditions, allergies, and dietary preferences in your recommendations. Be specific about foods, portions, and cooking methods."""
        
        return prompt
    
    def _parse_diet_plan(self, ai_response: str) -> Dict:
        """Parse AI response into structured meal plan"""
        try:
            meal_plan = {
                'breakfast': [],
                'lunch': [],
                'dinner': [],
                'snacks': [],
                'notes': []
            }
            
            lines = ai_response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                line_upper = line.upper()
                if line_upper.startswith('BREAKFAST'):
                    current_section = 'breakfast'
                elif line_upper.startswith('LUNCH'):
                    current_section = 'lunch'
                elif line_upper.startswith('DINNER'):
                    current_section = 'dinner'
                elif line_upper.startswith('SNACKS'):
                    current_section = 'snacks'
                elif line_upper.startswith('NOTES'):
                    current_section = 'notes'
                elif current_section and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    # Remove bullet points
                    clean_line = line[1:].strip()
                    if clean_line:
                        meal_plan[current_section].append(clean_line)
                elif current_section and line and not any(section in line_upper for section in ['BREAKFAST', 'LUNCH', 'DINNER', 'SNACKS', 'NOTES']):
                    meal_plan[current_section].append(line)
            
            return meal_plan
            
        except Exception as e:
            print(f"Error parsing diet plan: {e}")
            raise Exception(f"Failed to parse AI response: {str(e)}")
    
    
    def analyze_feedback(self, feedback_text: str) -> Dict:
        """
        Analyze user feedback using Gemini AI
        """
        try:
            prompt = f"""Analyze this user feedback on their diet plan and provide insights:

User feedback: "{feedback_text}"

Please analyze:
1. Adherence score (0-1, where 1 is perfect adherence)
2. Positive aspects mentioned
3. Negative aspects mentioned
4. Overall sentiment (positive/negative/neutral)
5. Suggestions for improvement

Respond in JSON format:
{{
    "adherence_score": 0.7,
    "positive_aspects": ["liked breakfast", "easy to follow"],
    "negative_aspects": ["portions too large"],
    "sentiment": "positive",
    "suggestions": ["reduce portion sizes", "add more variety"]
}}"""
            
            ai_response = self.generate_text(prompt, max_tokens=200)
            
            # Try to parse JSON response
            try:
                if '{' in ai_response and '}' in ai_response:
                    json_start = ai_response.find('{')
                    json_end = ai_response.rfind('}') + 1
                    json_str = ai_response[json_start:json_end]
                    analysis = json.loads(json_str)
                    return analysis
            except:
                pass
            
            # If JSON parsing failed, raise an error
            raise Exception("Failed to parse AI feedback analysis")
            
        except Exception as e:
            print(f"Error analyzing feedback: {e}")
            raise Exception(f"AI feedback analysis failed: {str(e)}")
