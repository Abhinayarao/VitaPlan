"""
Firebase Configuration
Replace these values with your actual Firebase project config
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Firebase Configuration
FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY", "AIzaSyA2DrMR0ET4miut3fva6Aq1Pea53wp-Ocs"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", "vitaplan-42595.firebaseapp.com"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID", "vitaplan-42595"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", "vitaplan-42595.firebasestorage.app"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", "827522536498"),
    "appId": os.getenv("FIREBASE_APP_ID", "1:827522536498:web:4c1ee62813bd4dfa13582b"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL", "https://vitaplan-42595-default-rtdb.firebaseio.com/")
}

# Firestore Collections
COLLECTIONS = {
    "users": "users",
    "conversations": "conversations", 
    "diet_plans": "diet_plans",
    "feedback": "feedback"
}
