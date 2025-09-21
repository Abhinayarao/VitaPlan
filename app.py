from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import uuid
import json
from datetime import datetime, date, timedelta
from ai_agents import AIAgentManager
from smart_daily_handler import SmartDailyHandler
from hybrid_database import HybridDatabase
from firebase_auth import FirebaseAuth

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Configure session to persist across browser sessions
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Sessions last 7 days

# Configure CORS to allow credentials (for session cookies)
CORS(app, supports_credentials=True)

# Initialize the AI-powered agent manager with Firebase-only database
db = HybridDatabase(use_firebase=True)
agent_manager = AIAgentManager(db)
smart_handler = SmartDailyHandler(db)
firebase_auth = FirebaseAuth()

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('index.html')

@app.route('/api/test-firebase', methods=['GET'])
def test_firebase():
    """Test Firebase connection"""
    try:
        user_id = "test_user"
        plan_date = "2025-01-01"
        test_meal_plan = {"breakfast": ["Test breakfast"], "lunch": ["Test lunch"]}
        
        # Test save
        save_result = db.save_diet_plan(user_id, plan_date, test_meal_plan)
        
        # Test retrieve
        retrieved_plan = db.get_diet_plan(user_id, plan_date)
        
        return jsonify({
            'status': 'success',
            'save_result': save_result,
            'retrieved_plan': retrieved_plan is not None,
            'plan_data': retrieved_plan
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/api/signup', methods=['POST'])
def signup():
    """Handle user signup"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        full_name = data.get('fullName', '').strip()
        
        if not email or not password or not full_name:
            return jsonify({
                'status': 'error',
                'message': 'Please provide email, password, and full name.'
            })
        
        # Create user with Firebase Auth
        result = firebase_auth.signup(email, password, {'name': full_name})
        
        if result['success']:
            # Store user session and make it permanent
            session['user_id'] = result['user_id']
            session['email'] = email
            session['user_name'] = full_name
            session.permanent = True  # Make session persist across browser sessions
            
            return jsonify({
                'status': 'success',
                'message': result['message'],
                'user': {'name': full_name, 'email': email}
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result['message']
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Signup failed: {str(e)}'
        })

@app.route('/api/login', methods=['POST'])
def login():
    """Handle user login"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({
                'status': 'error',
                'message': 'Please provide email and password.'
            })
        
        # Login with Firebase Auth
        result = firebase_auth.login(email, password)
        
        if result['success']:
            # Store user session and make it permanent
            session['user_id'] = result['user_id']
            session['email'] = email
            session.permanent = True  # Make session persist across browser sessions
            
            # Get user details from database
            user = db.get_user(result['user_id'])
            if user:
                session['user_name'] = user.get('name', 'User')
                return jsonify({
                    'status': 'success',
                    'message': result['message'],
                    'user': {'name': user.get('name', 'User'), 'email': email}
                })
            else:
                return jsonify({
                    'status': 'success',
                    'message': result['message'],
                    'user': {'name': 'User', 'email': email}
                })
        else:
            return jsonify({
                'status': 'error',
                'message': result['message']
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Login failed: {str(e)}'
        })

@app.route('/api/logout', methods=['POST'])
def logout():
    """Handle user logout"""
    try:
        result = firebase_auth.logout()
        session.clear()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Logout failed: {str(e)}'
        })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({
                'status': 'error',
                'message': 'Please login first to interact with the bot.'
            })
        
        data = request.get_json()
        message = data.get('message', '').strip()
        message_type = data.get('type', 'auto')
        
        if not message:
            return jsonify({
                'status': 'error',
                'message': 'Please enter a message.'
            })
        
        user_id = session['user_id']
        
        # Handle special message types directly
        if message_type == 'diet_plan_confirmation':
            response = agent_manager.process_message(user_id, message, message_type)
        elif message_type == 'diet_plan_modification':
            response = agent_manager.process_message(user_id, message, message_type)
        elif message_type == 'diet_plan_alternative':
            response = agent_manager.process_message(user_id, message, message_type)
        else:
            # Process the message through the smart daily handler
            response = smart_handler.handle_daily_interaction(user_id, message)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        })

@app.route('/api/history')
def get_history():
    """Get conversation history"""
    try:
        if 'user_id' not in session:
            return jsonify({'history': []})
        
        user_id = session['user_id']
        history = agent_manager.get_conversation_history(user_id)
        
        return jsonify({'history': history})
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error retrieving history: {str(e)}'
        })

@app.route('/api/user-data', methods=['POST'])
def submit_user_data():
    """Submit user data directly"""
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({
                'status': 'error',
                'message': 'Please login first.'
            })
        
        data = request.get_json()
        user_id = session['user_id']
        
        # Convert form data to JSON string for the agent
        user_data_json = json.dumps(data)
        
        response = agent_manager.process_message(user_id, user_data_json, 'user_data')
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error submitting user data: {str(e)}'
        })

@app.route('/api/diet-plan', methods=['GET'])
def get_diet_plan():
    """Get diet plan for today - fetch existing or generate new"""
    try:
        if 'user_id' not in session:
            return jsonify({
                'status': 'error',
                'message': 'Please login first.'
            })
        
        user_id = session['user_id']
        today = date.today().isoformat()
        
        # Debug: Print what we're looking for
        print(f"Get Today's Diet Plan - User: {user_id}, Date: {today}")
        
        # First check if there's already a confirmed plan for today
        existing_plan = db.get_diet_plan(user_id, today)
        print(f"Existing plan found: {existing_plan is not None}")
        
        if existing_plan:
            print(f"Returning existing plan for {today}")
            # Return the existing confirmed plan
            meal_plan = existing_plan.get('meal_plan', {})
            response = f"Here's your confirmed meal plan for today:\n\n{agent_manager.diet_agent._format_meal_plan(meal_plan)}"
            
            return jsonify({
                'status': 'existing',
                'message': response,
                'meal_plan': meal_plan,
                'requires_confirmation': False
            })
        
        # No existing plan - generate a new one
        print(f"No existing plan found, generating new one for {today}")
        response = agent_manager.process_message(user_id, '', 'diet_plan')
        
        # Debug: Print the response to see what's being returned
        print(f"Diet plan API response: {response}")
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error getting diet plan: {str(e)}'
        })

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback on diet plan"""
    try:
        data = request.get_json()
        feedback_text = data.get('feedback', '').strip()
        
        if not feedback_text:
            return jsonify({
                'status': 'error',
                'message': 'Please provide feedback.'
            })
        
        if 'user_id' not in session:
            return jsonify({
                'status': 'error',
                'message': 'Please login first.'
            })
        
        user_id = session['user_id']
        response = agent_manager.process_message(user_id, feedback_text, 'feedback')
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error submitting feedback: {str(e)}'
        })

@app.route('/api/summary')
def get_summary():
    """Get feedback summary"""
    try:
        if 'user_id' not in session:
            return jsonify({
                'status': 'error',
                'message': 'Please login first.'
            })
        
        user_id = session['user_id']
        days = request.args.get('days', 7, type=int)
        response = agent_manager.feedback_agent.get_feedback_summary(user_id, days)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error getting summary: {str(e)}'
        })

@app.route('/api/user-details')
def get_user_details():
    """Get user details"""
    try:
        if 'user_id' not in session:
            return jsonify({
                'status': 'error',
                'message': 'Please login first.'
            })
        
        user_id = session['user_id']
        user_data = agent_manager.db.get_user(user_id)
        
        if not user_data:
            return jsonify({
                'status': 'error',
                'message': 'User profile not found. Please provide your information first.'
            })
        
        # Generate user-friendly AI response
        user_friendly_message = agent_manager.generate_user_details_message(user_data)
        
        return jsonify({
            'status': 'success',
            'message': user_friendly_message,
            'user_data': user_data  # Keep raw data for debugging if needed
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error getting user details: {str(e)}'
        })

@app.route('/api/daily-status')
def get_daily_status():
    """Get user's daily status"""
    try:
        if 'user_id' not in session:
            return jsonify({
                'status': 'error',
                'message': 'Please login first.'
            })
        
        user_id = session['user_id']
        daily_status = smart_handler.daily_tracker.get_user_daily_status(user_id)
        
        # Generate user-friendly AI response
        user_friendly_message = smart_handler.generate_daily_status_message(user_id, daily_status)
        
        return jsonify({
            'status': 'success',
            'message': user_friendly_message,
            'daily_status': daily_status  # Keep raw data for debugging if needed
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error getting daily status: {str(e)}'
        })

@app.route('/api/calendar-data', methods=['GET'])
def get_calendar_data():
    """Get meal plans for calendar view"""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Please login first'})
    
    try:
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        
        if not start_date or not end_date:
            return jsonify({'status': 'error', 'message': 'Start and end dates are required'})
        
        # Get meal plans for the date range
        meal_plans = {}
        current_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        user_id = session['user_id']
        print(f"Calendar data request for user {user_id} from {start_date} to {end_date}")
        
        while current_date <= end_date_obj:
            date_str = current_date.isoformat()
            plan = db.get_diet_plan(user_id, date_str)
            if plan:
                meal_plans[date_str] = True
                print(f"Found plan for {date_str}")
            current_date += timedelta(days=1)
        
        print(f"Calendar data response: {meal_plans}")
        
        return jsonify({
            'status': 'success',
            'meal_plans': meal_plans
        })
    except Exception as e:
        print(f"Error getting calendar data: {e}")
        return jsonify({'status': 'error', 'message': f'Error getting calendar data: {str(e)}'})

@app.route('/api/meal-plan/<date>', methods=['GET'])
def get_meal_plan_for_date(date):
    """Get meal plan for a specific date"""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Please login first'})
    
    try:
        plan = db.get_diet_plan(session['user_id'], date)
        if plan:
            return jsonify({
                'status': 'success',
                'meal_plan': plan['meal_plan']
            })
        else:
            return jsonify({'status': 'error', 'message': 'No meal plan found for this date'})
    except Exception as e:
        print(f"Error getting meal plan for date {date}: {e}")
        return jsonify({'status': 'error', 'message': f'Error getting meal plan: {str(e)}'})

@app.route('/api/generate-plan-for-date', methods=['POST'])
def generate_plan_for_date():
    """Generate meal plan for a specific future date with feedback integration"""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Please login first'})
    
    try:
        data = request.get_json()
        target_date = data.get('date')
        
        if not target_date:
            return jsonify({'status': 'error', 'message': 'Date is required'})
        
        # Check if date is in the future
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        today = date.today()
        
        if target_date_obj <= today:
            return jsonify({'status': 'error', 'message': 'Can only generate plans for future dates'})
        
        # Get user profile
        user_profile = db.get_user(session['user_id'])
        if not user_profile:
            return jsonify({'status': 'error', 'message': 'User profile not found'})
        
        # Get previous day's feedback for learning
        previous_date = target_date_obj - timedelta(days=1)
        previous_plan = db.get_diet_plan(session['user_id'], previous_date.isoformat())
        previous_feedback = previous_plan.get('feedback') if previous_plan else None
        
        # Generate AI diet plan with feedback integration
        meal_plan = agent_manager.diet_agent.gemini_client.generate_diet_plan(user_profile, previous_feedback)
        
        # Don't save yet - show for confirmation/modification first
        response = agent_manager.diet_agent._format_meal_plan(meal_plan)
        confirmation_message = response + "\n\n" + agent_manager.diet_agent._get_confirmation_message()
        
        agent_manager.diet_agent.log_conversation(session['user_id'], confirmation_message, "agent_response")
        
        return jsonify({
            'status': 'pending_confirmation',
            'message': confirmation_message,
            'meal_plan': meal_plan,
            'plan_date': target_date,
            'requires_confirmation': True
        })
        
    except Exception as e:
        print(f"Error generating plan for date {target_date}: {e}")
        return jsonify({'status': 'error', 'message': f'Error generating plan: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
