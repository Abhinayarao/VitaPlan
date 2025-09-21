"""
Test Firebase connection
"""
from hybrid_database import HybridDatabase

def test_firebase_connection():
    """Test if Firebase is working"""
    print("🔥 Testing Firebase-only connection...")
    
    try:
        # Initialize Firebase-only database
        db = HybridDatabase(use_firebase=True)
        
        # Test creating a user
        test_user_id = "test_user_123"
        success = db.create_user(
            user_id=test_user_id,
            name="Test User",
            age=25,
            gender="male",
            height=175.0,
            weight=70.0,
            bmi=22.9,
            health_conditions=["None"],
            allergies=["None"],
            dietary_preferences=["vegetarian"]
        )
        
        if success:
            print("✅ Firebase connection successful!")
            print("✅ User created successfully!")
            
            # Test getting user
            user = db.get_user(test_user_id)
            if user:
                print(f"✅ User retrieved: {user['name']}")
                print(f"   - Age: {user['age']}")
                print(f"   - BMI: {user['bmi']}")
                print(f"   - Dietary preferences: {user['dietary_preferences']}")
                
                # Test conversation
                db.add_conversation(test_user_id, "TestAgent", "Hello from Firebase!", "test")
                conversations = db.get_conversations(test_user_id, 5)
                print(f"✅ Conversation added: {len(conversations)} conversations found")
                
                print("\n🎉 Firebase-only mode is working perfectly!")
            else:
                print("❌ Failed to retrieve user")
        else:
            print("❌ Failed to create user")
            
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
        print("💡 Make sure you have:")
        print("   1. firebase-service-account.json file in the project root")
        print("   2. All Firebase environment variables set in .env")
        print("   3. Firebase project properly configured")

if __name__ == "__main__":
    test_firebase_connection()
