"""
Render Cold Start Warm-Up Script
Run this 5 minutes before evaluation to ensure your service is warm
"""

import requests
import time
from datetime import datetime

# Your deployed Render URL
RENDER_URL = "https://ai-agentic-honeypot-system.onrender.com"

def warm_up_service():
    """Warm up Render service by making initial requests"""
    
    print("=" * 70)
    print("🔥 RENDER SERVICE WARM-UP")
    print("=" * 70)
    print()
    print(f"📍 Target: {RENDER_URL}")
    print(f"🕐 Started: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Try health check first (multiple attempts for cold start)
    print("Step 1: Warming up health endpoint...")
    for attempt in range(3):
        try:
            print(f"   Attempt {attempt + 1}/3: ", end="", flush=True)
            start = time.time()
            response = requests.get(f"{RENDER_URL}/health", timeout=90)
            elapsed = time.time() - start
            
            if response.status_code == 200:
                print(f"✅ Success ({elapsed:.1f}s)")
                break
            else:
                print(f"⚠️  Status {response.status_code} ({elapsed:.1f}s)")
        except requests.exceptions.Timeout:
            print(f"❌ Timeout (>90s) - Retry...")
            time.sleep(10)
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}")
            time.sleep(10)
    
    print()
    print("Step 2: Testing API endpoint...")
    
    # Make a test API call
    test_payload = {
        "sessionId": "warmup-test",
        "message": {
            "sender": "scammer",
            "text": "Test message",
            "timestamp": "2026-02-19T12:00:00Z"
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    try:
        print("   Testing /api/message: ", end="", flush=True)
        start = time.time()
        response = requests.post(
            f"{RENDER_URL}/api/message",
            headers={
                "Content-Type": "application/json",
                "x-api-key": "honeypot-secret-2026"
            },
            json=test_payload,
            timeout=60
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            if "status" in data and data["status"] == "success":
                print(f"✅ Success ({elapsed:.1f}s)")
                print(f"   Reply: {data.get('reply', 'N/A')[:60]}...")
            else:
                print(f"⚠️  Unexpected response")
        else:
            print(f"❌ Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")
    
    print()
    print("=" * 70)
    print("✅ WARM-UP COMPLETE")
    print("=" * 70)
    print()
    print("Your service is now warm and ready for testing!")
    print()
    print("Next steps:")
    print("  1. Wait 10 seconds")
    print("  2. Run: python self_test.py")
    print("  3. Expected: Fast responses (<5s) and score 90+")
    print()

if __name__ == "__main__":
    warm_up_service()
