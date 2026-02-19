"""
API Key Verification Script
Tests all configured Gemini API keys to ensure they're working
Run this before deployment to avoid API errors
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if google-genai is installed
try:
    from google import genai
except ImportError:
    print("❌ google-genai not installed. Run: pip install google-genai")
    sys.exit(1)

def test_gemini_key(api_key: str, key_name: str) -> bool:
    """Test a single Gemini API key"""
    try:
        client = genai.Client(api_key=api_key)
        
        # Try a simple generation
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='Say "Working" if you can read this.'
        )
        
        if response.text and len(response.text) > 0:
            print(f"✅ {key_name}: Working")
            return True
        else:
            print(f"❌ {key_name}: No response received")
            return False
            
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "API key not valid" in error_msg:
            print(f"❌ {key_name}: Invalid API key")
        elif "NOT_FOUND" in error_msg:
            print(f"❌ {key_name}: Model not found (check model name)")
        elif "RESOURCE_EXHAUSTED" in error_msg:
            print(f"⚠️  {key_name}: Quota exceeded (key works but no quota left)")
            return True  # Key is valid, just no quota
        else:
            print(f"❌ {key_name}: {error_msg}")
        return False

def main():
    print("=" * 60)
    print("🔑 GEMINI API KEY VERIFICATION")
    print("=" * 60)
    print()
    
    # Get all Gemini API keys from environment
    api_keys = []
    for i in range(1, 21):  # Check up to 20 keys
        key_name = f"GOOGLE_API_KEY" if i == 1 else f"GOOGLE_API_KEY_{i}"
        key_value = os.getenv(key_name)
        
        if key_value:
            api_keys.append((key_name, key_value))
    
    if not api_keys:
        print("❌ No Gemini API keys found in .env file!")
        print("Add keys as GOOGLE_API_KEY, GOOGLE_API_KEY_2, etc.")
        return
    
    print(f"Found {len(api_keys)} API key(s) to test\n")
    
    # Test each key
    working_keys = 0
    invalid_keys = []
    
    for key_name, key_value in api_keys:
        if test_gemini_key(key_value, key_name):
            working_keys += 1
        else:
            invalid_keys.append(key_name)
    
    print()
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total Keys: {len(api_keys)}")
    print(f"Working Keys: {working_keys}")
    print(f"Invalid Keys: {len(invalid_keys)}")
    
    if invalid_keys:
        print(f"\n⚠️  Invalid keys (comment out in .env):")
        for key_name in invalid_keys:
            print(f"   - {key_name}")
    
    print()
    
    if working_keys > 0:
        print(f"✅ {working_keys} working key(s) - Ready for deployment!")
        print(f"   Capacity: ~{working_keys * 20} requests/day (20 per key)")
    else:
        print("❌ No working keys - Cannot deploy!")
        print("   Get API keys at: https://aistudio.google.com/app/apikey")
    
    print()
    
    # Check model configuration
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    valid_models = ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.0-pro", "gemini-pro"]
    
    print("🔧 Model Configuration:")
    print(f"   Current: {gemini_model}")
    
    if gemini_model in valid_models:
        print(f"   ✅ Valid model")
    else:
        print(f"   ❌ Invalid model! Use one of: {', '.join(valid_models)}")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
