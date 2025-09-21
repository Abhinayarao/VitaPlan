#!/usr/bin/env python3
"""
VitaPlan - AI-Powered Diet Planning System
Startup script for the multi-agent system
"""

import os
import sys
from app import app

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import flask
        import flask_cors
        import requests
        from dotenv import load_dotenv
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    if not os.path.exists('.env'):
        print("⚠️  .env file not found. Creating template...")
        with open('.env', 'w') as f:
            f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
            f.write("FLASK_ENV=development\n")
            f.write("DATABASE_URL=sqlite:///vitaplan.db\n")
        print("📝 Please edit .env file and add your Gemini API key")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("⚠️  Please set your Gemini API key in .env file")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def main():
    """Main startup function"""
    print("🍎 VitaPlan - AI-Powered Diet Planning System")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment
    if not check_env_file():
        print("\n📋 Setup Instructions:")
        print("1. Get your Gemini API key from https://aistudio.google.com/app/apikey")
        print("2. Edit the .env file and replace 'your_gemini_api_key_here' with your actual API key")
        print("3. Run this script again")
        sys.exit(1)
    
    print("\n🚀 Starting VitaPlan server...")
    print("📱 Open your browser and go to: http://localhost:5001")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5001)

if __name__ == '__main__':
    main()
