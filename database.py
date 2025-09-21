import sqlite3
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

class Database:
    def __init__(self, db_path: str = "vitaplan.db"):
        self.db_path = db_path
        self.init_database()
    
    def _get_connection(self, timeout: int = 30):
        """Get database connection with timeout and retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                conn = sqlite3.connect(self.db_path, timeout=timeout)
                conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode for better concurrency
                return conn
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                    continue
                raise e
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                height REAL,  -- Height in cm
                weight REAL,  -- Weight in kg
                bmi REAL,  -- Calculated BMI
                health_conditions TEXT,  -- JSON string of health conditions
                allergies TEXT,  -- JSON string of allergies
                dietary_preferences TEXT,  -- JSON string of dietary preferences
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                message TEXT NOT NULL,
                message_type TEXT NOT NULL,  -- 'user_input', 'agent_response', 'system'
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Diet plans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diet_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                plan_date DATE NOT NULL,
                meal_plan TEXT NOT NULL,  -- JSON string of meal plan
                feedback TEXT,  -- JSON string of user feedback
                adherence_score REAL,  -- 0-1 score based on feedback
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, user_id: str, name: str, age: int, gender: str, 
                   height: float = None, weight: float = None, bmi: float = None,
                   health_conditions: List[str] = None, allergies: List[str] = None, 
                   dietary_preferences: List[str] = None) -> bool:
        """Create a new user or update existing user"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                # Update existing user
                cursor.execute('''
                    UPDATE users 
                    SET name = ?, age = ?, gender = ?, height = ?, weight = ?, bmi = ?, 
                        health_conditions = ?, allergies = ?, dietary_preferences = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (name, age, gender, height, weight, bmi,
                      json.dumps(health_conditions or []),
                      json.dumps(allergies or []),
                      json.dumps(dietary_preferences or []),
                      user_id))
            else:
                # Create new user
                cursor.execute('''
                    INSERT INTO users (user_id, name, age, gender, height, weight, bmi, health_conditions, allergies, dietary_preferences)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, name, age, gender, height, weight, bmi,
                      json.dumps(health_conditions or []),
                      json.dumps(allergies or []),
                      json.dumps(dietary_preferences or [])))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating/updating user: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user information"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM users WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'user_id': result[1],
                'name': result[2],
                'age': result[3],
                'gender': result[4],
                'height': result[5],
                'weight': result[6],
                'bmi': result[7],
                'health_conditions': json.loads(result[8] or '[]'),
                'allergies': json.loads(result[9] or '[]'),
                'dietary_preferences': json.loads(result[10] or '[]'),
                'created_at': result[11],
                'updated_at': result[12]
            }
        return None
    
    def add_conversation(self, user_id: str, agent_name: str, message: str, message_type: str) -> bool:
        """Add a conversation entry"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversations (user_id, agent_name, message, message_type)
                VALUES (?, ?, ?, ?)
            ''', (user_id, agent_name, message, message_type))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding conversation: {e}")
            return False
    
    def get_conversations(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM conversations 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'id': result[0],
            'user_id': result[1],
            'agent_name': result[2],
            'message': result[3],
            'message_type': result[4],
            'timestamp': result[5]
        } for result in results]
    
    def save_diet_plan(self, user_id: str, plan_date: str, meal_plan: Dict) -> bool:
        """Save a diet plan"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO diet_plans (user_id, plan_date, meal_plan)
                VALUES (?, ?, ?)
            ''', (user_id, plan_date, json.dumps(meal_plan)))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving diet plan: {e}")
            return False
    
    def update_diet_feedback(self, user_id: str, plan_date: str, feedback: Dict, adherence_score: float) -> bool:
        """Update diet plan with feedback"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE diet_plans 
                SET feedback = ?, adherence_score = ?
                WHERE user_id = ? AND plan_date = ?
            ''', (json.dumps(feedback), adherence_score, user_id, plan_date))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating diet feedback: {e}")
            return False
    
    def get_diet_plan(self, user_id: str, plan_date: str) -> Optional[Dict]:
        """Get diet plan for a specific date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM diet_plans 
            WHERE user_id = ? AND plan_date = ?
        ''', (user_id, plan_date))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'user_id': result[1],
                'plan_date': result[2],
                'meal_plan': json.loads(result[3]),
                'feedback': json.loads(result[4]) if result[4] else None,
                'adherence_score': result[5],
                'created_at': result[6]
            }
        return None
    
    def get_user_diet_history(self, user_id: str, limit: int = 30) -> List[Dict]:
        """Get user's diet plan history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM diet_plans 
            WHERE user_id = ? 
            ORDER BY plan_date DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'id': result[0],
            'user_id': result[1],
            'plan_date': result[2],
            'meal_plan': json.loads(result[3]),
            'feedback': json.loads(result[4]) if result[4] else None,
            'adherence_score': result[5],
            'created_at': result[6]
        } for result in results]
