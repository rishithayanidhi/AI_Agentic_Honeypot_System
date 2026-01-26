"""Test all scam detection types"""
import requests
import time

BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": "honeypot-secret-2026"
}

scam_messages = [
    {
        "name": "Bank Fraud",
        "message": "URGENT! Your SBI account has been suspended due to KYC verification pending. Send OTP to 9876543210 to reactivate."
    },
    {
        "name": "UPI Scam",
        "message": "You won Rs 50,000! Send Rs 100 to verify@paytm to claim your prize now!"
    },
    {
        "name": "Phishing Link",
        "message": "Your package is waiting. Click here to confirm delivery: bit.ly/package-confirm"
    },
    {
        "name": "OTP Request",
        "message": "Dear customer, your account will be blocked. Please share the OTP received on your phone to verify your identity."
    },
    {
        "name": "Lottery Scam",
        "message": "Congratulations! You have won the Kaun Banega Crorepati lottery. Contact 9123456789 to claim Rs 1 crore prize."
    }
]

print("="*70)
print("TESTING ALL SCAM DETECTION TYPES")
print("="*70)

passed = 0
failed = 0

for idx, test in enumerate(scam_messages, 1):
    print(f"\nTest {idx}: {test['name']}")
    print(f"Message: {test['message'][:60]}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/message",
            headers=HEADERS,
            json={
                "session_id": f"scam_test_{idx}",
                "message": test['message']
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            detection = data.get('detection', {})
            is_scam = detection.get('is_scam', False)
            confidence = detection.get('confidence', 0)
            scam_type = detection.get('scam_type', 'unknown')
            
            if is_scam:
                print(f"  PASS - Scam detected: {confidence*100:.1f}% confidence")
                print(f"  Type: {scam_type}")
                passed += 1
            else:
                print(f"  FAIL - Not detected as scam")
                failed += 1
            
            # Check AI response
            ai_response = data.get('response') or data.get('agentResponse')
            if ai_response:
                print(f"  AI: {str(ai_response)[:80]}...")
            else:
                print(f"  AI: No response (quota exhausted)")
                
        else:
            print(f"  FAIL - HTTP {response.status_code}")
            failed += 1
            
    except Exception as e:
        print(f"  FAIL - Error: {e}")
        failed += 1
    
    time.sleep(1)

print("\n" + "="*70)
print(f"RESULTS: {passed} passed, {failed} failed")
print("="*70)
