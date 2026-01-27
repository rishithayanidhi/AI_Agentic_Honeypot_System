# -*- coding: utf-8 -*-
"""
Quick test for AI Agent Persona functionality with error handling
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": "honeypot-secret-2026"
}

def test_persona(name, session_id, message):
    """Test a single persona scenario"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/message",
            headers=HEADERS,
            json={
                "session_id": session_id,
                "message": message
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Safely extract fields
            ai_response = data.get('response', data.get('agentResponse', 'No response'))
            scam_detected = data.get('scamDetected', data.get('scam_detected', False))
            
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Scam Detected: {scam_detected}")
            print(f"✓ AI Response: {ai_response}")
            
            # Analyze response characteristics
            if ai_response:
                response_lower = str(ai_response).lower()
                if any(word in response_lower for word in ['what', 'how', 'confused', 'understand']):
                    print(f"  ➜ Persona shows confusion/questioning (Good!)")
                if any(word in response_lower for word in ['worried', 'concerned', 'help']):
                    print(f"  ➜ Persona shows concern (Good!)")
                if any(word in response_lower for word in ['ok', 'sure', 'yes', 'please']):
                    print(f"  ➜ Persona shows compliance (Good!)")
            
            return True
        else:
            print(f"✗ Error: Status {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Request Error: {e}")
        return False
    except KeyError as e:
        print(f"✗ KeyError: {e}")
        print(f"  Response data: {json.dumps(data, indent=2)[:300]}")
        return False
    except Exception as e:
        print(f"✗ Unexpected Error: {type(e).__name__}: {e}")
        return False

def main():
    print("="*60)
    print("AI AGENT PERSONA TEST WITH ERROR HANDLING")
    print("="*60)
    
    test_cases = [
        {
            "name": "Early Stage - Cautious Persona",
            "session": "persona_test_cautious",
            "message": "Your account needs verification"
        },
        {
            "name": "Bank Fraud - Eager/Confused Persona",
            "session": "persona_test_eager",
            "message": "URGENT! Bank account blocked. Send OTP immediately to 9876543210"
        },
        {
            "name": "Phishing - Busy Professional Persona",
            "session": "persona_test_professional",
            "message": "Package delivery pending. Click http://fake-link.com to confirm."
        }
    ]
    
    results = []
    for test in test_cases:
        success = test_persona(test["name"], test["session"], test["message"])
        results.append(success)
        time.sleep(2)  # Wait between tests
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Passed: {sum(results)}/{len(results)}")
    print(f"Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n✓ All tests passed! Error handling working correctly.")
    else:
        print("\n✗ Some tests failed. Check logs above for details.")

if __name__ == "__main__":
    main()
