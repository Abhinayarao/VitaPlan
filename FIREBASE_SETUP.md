# Firebase Setup Guide for VitaPlan

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" or "Add project"
3. Enter project name: `vitaplan-diet-app` (or your preferred name)
4. Enable Google Analytics (optional)
5. Click "Create project"

## Step 2: Enable Authentication

1. In your Firebase project, go to "Authentication" in the left sidebar
2. Click "Get started"
3. Go to "Sign-in method" tab
4. Enable "Email/Password" authentication
5. Click "Save"

## Step 3: Create Firestore Database

1. Go to "Firestore Database" in the left sidebar
2. Click "Create database"
3. Choose "Start in test mode" (for development)
4. Select a location (choose closest to your users)
5. Click "Done"

## Step 4: Get Firebase Configuration

1. Go to Project Settings (gear icon)
2. Scroll down to "Your apps" section
3. Click "Web" icon (`</>`)
4. Register your app with a nickname: `VitaPlan Web App`
5. Copy the Firebase configuration object

## Step 5: Create Service Account

1. Go to Project Settings > Service Accounts
2. Click "Generate new private key"
3. Download the JSON file
4. Rename it to `firebase-service-account.json`
5. Place it in your VitaPlan project root directory

## Step 6: Update Environment Variables

Create or update your `.env` file with:

```env
# Firebase Configuration
FIREBASE_API_KEY=your-api-key-here
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789
FIREBASE_APP_ID=your-app-id

# Keep existing variables
GEMINI_API_KEY=your-gemini-key
```

## Step 7: Install Firebase Dependencies

```bash
pip install -r requirements.txt
```

## Step 8: Test Firebase Connection

Run the app and check the console for:
- ✅ "Using Firebase as primary database" - Success!
- ❌ "Firebase initialization failed" - Check your configuration

## Firebase Collections Structure

Your Firestore will have these collections:

### users
- Document ID: Auto-generated
- Fields: user_id, name, age, gender, height, weight, bmi, health_conditions, allergies, dietary_preferences, created_at, updated_at

### conversations
- Document ID: Auto-generated
- Fields: user_id, agent_name, message, message_type, timestamp

### diet_plans
- Document ID: {user_id}_{plan_date}
- Fields: user_id, plan_date, meal_plan, created_at, updated_at

### feedback
- Document ID: {user_id}_{plan_date}
- Fields: user_id, plan_date, feedback, adherence_score, created_at

## Security Rules (Optional)

For production, update your Firestore security rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    match /conversations/{conversationId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
    
    match /diet_plans/{dietPlanId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
    
    match /feedback/{feedbackId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
  }
}
```

## Troubleshooting

### Common Issues:

1. **"Firebase service account file not found"**
   - Make sure `firebase-service-account.json` is in the project root
   - Check the file name is exactly correct

2. **"Firebase environment variable not set"**
   - Check your `.env` file has all required variables
   - Restart your Flask app after updating `.env`

3. **"Permission denied"**
   - Check your Firestore security rules
   - Make sure authentication is working

4. **"Project not found"**
   - Verify your FIREBASE_PROJECT_ID is correct
   - Check the project exists in Firebase Console

## Benefits of Firebase Integration

✅ **User Authentication** - Secure login/signup
✅ **Real-time Data** - Instant updates across devices
✅ **Scalability** - Handles multiple users easily
✅ **Cloud Storage** - No local database files
✅ **Backup** - Automatic data backup
✅ **Analytics** - User engagement tracking
✅ **Security** - Built-in security rules

## Fallback to SQLite

If Firebase fails, the app automatically falls back to SQLite, so your app will always work!


