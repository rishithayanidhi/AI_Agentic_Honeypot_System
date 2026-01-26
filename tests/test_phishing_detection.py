"""Quick test for phishing link detection"""
import requests

BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": "honeypot-secret-2026"
}

# Test phishing message
message = "Your package is waiting. Click here to confirm delivery: bit.ly/package-confirm"

print("Testing phishing link detection...")
print(f"Message: {message}\n")

response = requests.post(
    f"{BASE_URL}/api/message",
    headers=HEADERS,
    json={
        "session_id": "phishing_test",
        "message": message
    },
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    print(f"Status: {response.status_code}")
    
    # Check detection
    detection = data.get('detection', {})
    is_scam = detection.get('is_scam', False)
    confidence = detection.get('confidence', 0)
    scam_type = detection.get('scam_type', 'unknown')
    reasoning = detection.get('reasoning', 'N/A')
    
    print(f"✓ Scam Detected: {is_scam}")
    print(f"✓ Confidence: {confidence*100:.1f}%")
    print(f"✓ Scam Type: {scam_type}")
    print(f"✓ Reasoning: {reasoning}")
    
    # Check response
    ai_response = data.get('response') or data.get('agentResponse')
    if ai_response:
        print(f"✓ AI Response: {ai_response}")
    else:
        print("✗ No AI response generated")
else:
    print(f"✗ Error: {response.status_code}")
    print(response.text)
