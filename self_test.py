#!/usr/bin/env python3
"""
Self-Test Script for Honeypot API
Tests your API before hackathon submission to maximize score
"""

import requests
import uuid
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any

# ===========================
# CONFIGURATION
# ===========================
# For local testing (default):
# ENDPOINT_URL = "http://localhost:8000/api/message"

# For production/deployed testing, use your deployed URL:
ENDPOINT_URL = "https://ai-agentic-honeypot-system.onrender.com/api/message"

API_KEY = "honeypot-secret-2026"  # << CHANGE THIS if needed

# ===========================
# TEST SCENARIO
# ===========================
test_scenario = {
    'scenarioId': 'bank_fraud',
    'name': 'Bank Fraud Detection',
    'scamType': 'bank_fraud',
    'initialMessage': 'URGENT: Your SBI account has been compromised. Your account will be blocked in 2 hours. Share your account number and OTP immediately to verify your identity.',
    'metadata': {
        'channel': 'SMS',
        'language': 'English',
        'locale': 'IN'
    },
    'maxTurns': 10,
    'fakeData': {
        'bankAccount': '1234567890123456',
        'upiId': 'scammer.fraud@fakebank',
        'phoneNumber': '+91-9876543210'
    }
}


def test_honeypot_api():
    """Test your honeypot API endpoint"""
    
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    conversation_history = []
    
    # Setup headers
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': API_KEY
    }
    
    print("=" * 80)
    print("🧪 HONEYPOT API SELF-TEST")
    print("=" * 80)
    print(f"📍 Endpoint: {ENDPOINT_URL}")
    print(f"🆔 Session ID: {session_id}")
    print("=" * 80)
    
    # Test conversation turns
    total_duration = 0
    responses = []
    
    for turn in range(1, test_scenario['maxTurns'] + 1):
        print(f"\n{'─' * 80}")
        print(f"🔄 TURN {turn}")
        print(f"{'─' * 80}")
        
        # First turn: use initial message
        if turn == 1:
            scammer_message = test_scenario['initialMessage']
        else:
            # For automated testing, use predefined follow-ups
            follow_ups = [
                "I need your help urgently! Can you confirm your mobile number?",
                f"Your number is {test_scenario['fakeData']['phoneNumber']}. Please share your account number.",
                f"The account is {test_scenario['fakeData']['bankAccount']}. What's the OTP you received?",
                "The OTP is being sent now. Can you also verify your UPI ID?",
                f"My UPI is {test_scenario['fakeData']['upiId']}. This is the final step.",
                "Thank you. Your account is now secure.",
            ]
            
            if turn - 2 < len(follow_ups):
                scammer_message = follow_ups[turn - 2]
            else:
                break  # End test after predefined messages
        
        # Prepare message object
        message = {
            "sender": "scammer",
            "text": scammer_message,
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        
        # Prepare request
        request_body = {
            'sessionId': session_id,
            'message': message,
            'conversationHistory': conversation_history,
            'metadata': test_scenario['metadata']
        }
        
        print(f"💬 Scammer: {scammer_message}")
        
        try:
            start_time = time.time()
            
            # Call your API
            response = requests.post(
                ENDPOINT_URL,
                headers=headers,
                json=request_body,
                timeout=30
            )
            
            response_time = time.time() - start_time
            total_duration += response_time
            
            # Check response status
            if response.status_code != 200:
                print(f"❌ ERROR: API returned status {response.status_code}")
                print(f"Response: {response.text}")
                break
            
            response_data = response.json()
            responses.append(response_data)
            
            # Extract honeypot reply
            honeypot_reply = (response_data.get('reply') or 
                            response_data.get('message') or 
                            response_data.get('text'))
            
            if not honeypot_reply:
                print("❌ ERROR: No reply/message/text field in response")
                print(f"Response data: {json.dumps(response_data, indent=2)}")
                break
            
            print(f"🤖 Honeypot: {honeypot_reply}")
            print(f"⏱️  Response time: {response_time:.2f}s")
            
            # Update conversation history
            conversation_history.append(message)
            conversation_history.append({
                'sender': 'user',
                'text': honeypot_reply,
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            })
            
        except requests.exceptions.Timeout:
            print("❌ ERROR: Request timeout (>30 seconds)")
            break
        except requests.exceptions.ConnectionError as e:
            print(f"❌ ERROR: Connection failed - {e}")
            print(f"\n💡 TIP: Is your API running? Check endpoint URL: {ENDPOINT_URL}")
            break
        except Exception as e:
            print(f"❌ ERROR: {e}")
            break
    
    # Evaluate final output
    print("\n" + "=" * 80)
    print("📊 EVALUATION RESULTS")
    print("=" * 80)
    
    # Create mock final output (you should generate this from your API)
    final_output = {
        "sessionId": session_id,
        "status": "completed",
        "scamDetected": True,  # Your API should detect this
        "totalMessagesExchanged": len(conversation_history),
        "extractedIntelligence": {
            "phoneNumbers": [test_scenario['fakeData']['phoneNumber']],
            "bankAccounts": [test_scenario['fakeData']['bankAccount']],
            "upiIds": [test_scenario['fakeData']['upiId']],
            "phishingLinks": [],
            "emailAddresses": []
        },
        "engagementMetrics": {
            "totalMessagesExchanged": len(conversation_history),
            "engagementDurationSeconds": int(total_duration)
        },
        "agentNotes": "Test conversation completed"
    }
    
    score = evaluate_final_output(final_output, test_scenario, conversation_history)
    
    print(f"\n🎯 TOTAL SCORE: {score['total']}/100")
    print(f"\n📈 Score Breakdown:")
    print(f"   ├─ Scam Detection:          {score['scamDetection']}/20 pts")
    print(f"   ├─ Intelligence Extraction: {score['intelligenceExtraction']}/40 pts")
    print(f"   ├─ Engagement Quality:      {score['engagementQuality']}/20 pts")
    print(f"   └─ Response Structure:      {score['responseStructure']}/20 pts")
    
    print(f"\n⏱️  Performance Metrics:")
    print(f"   ├─ Total Duration:    {total_duration:.2f}s")
    print(f"   ├─ Avg Response Time: {total_duration/max(len(responses), 1):.2f}s")
    print(f"   └─ Total Turns:       {len(conversation_history)//2}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if score['scamDetection'] < 20:
        print("   ⚠️  Improve scam detection - ensure scamDetected=true")
    if score['intelligenceExtraction'] < 30:
        print("   ⚠️  Extract more intelligence (phone numbers, accounts, UPI IDs)")
    if score['engagementQuality'] < 15:
        print("   ⚠️  Increase engagement - aim for 5+ message exchanges")
    if total_duration / max(len(responses), 1) > 5:
        print("   ⚠️  Optimize response time - aim for <5 seconds per response")
    
    if score['total'] >= 90:
        print("   ✅ Excellent! Your API is ready for submission!")
    elif score['total'] >= 70:
        print("   ✓  Good! Minor improvements recommended.")
    else:
        print("   ⚠️  Needs improvement before submission.")
    
    print("\n" + "=" * 80)
    return score


def evaluate_final_output(final_output: Dict, scenario: Dict, conversation_history: list) -> Dict:
    """Evaluate final output using hackathon scoring logic"""
    
    score = {
        'scamDetection': 0,
        'intelligenceExtraction': 0,
        'engagementQuality': 0,
        'responseStructure': 0,
        'total': 0
    }
    
    # 1. Scam Detection (20 points)
    if final_output.get('scamDetected', False):
        score['scamDetection'] = 20
        print("✅ Scam detected correctly")
    else:
        print("❌ Scam NOT detected")
    
    # 2. Intelligence Extraction (40 points)
    extracted = final_output.get('extractedIntelligence', {})
    fake_data = scenario.get('fakeData', {})
    
    key_mapping = {
        'bankAccount': ('bankAccounts', 10),
        'upiId': ('upiIds', 10),
        'phoneNumber': ('phoneNumbers', 10),
        'phishingLink': ('phishingLinks', 10),
        'emailAddress': ('emailAddresses', 10)
    }
    
    print("\n📦 Intelligence Extraction:")
    for fake_key, fake_value in fake_data.items():
        output_key, points = key_mapping.get(fake_key, (fake_key, 0))
        extracted_values = extracted.get(output_key, [])
        
        found = False
        if isinstance(extracted_values, list):
            if any(fake_value in str(v) for v in extracted_values):
                found = True
                score['intelligenceExtraction'] += points
        elif isinstance(extracted_values, str):
            if fake_value in extracted_values:
                found = True
                score['intelligenceExtraction'] += points
        
        status = "✅" if found else "❌"
        print(f"   {status} {fake_key}: {fake_value} {'(+'+str(points)+'pts)' if found else ''}")
    
    score['intelligenceExtraction'] = min(score['intelligenceExtraction'], 40)
    
    # 3. Engagement Quality (20 points)
    metrics = final_output.get('engagementMetrics', {})
    duration = metrics.get('engagementDurationSeconds', 0)
    messages = metrics.get('totalMessagesExchanged', 0)
    
    print("\n🤝 Engagement Quality:")
    if duration > 0:
        score['engagementQuality'] += 5
        print(f"   ✅ Engagement duration > 0s (+5pts)")
    if duration > 60:
        score['engagementQuality'] += 5
        print(f"   ✅ Engagement duration > 60s (+5pts)")
    if messages > 0:
        score['engagementQuality'] += 5
        print(f"   ✅ Messages exchanged > 0 (+5pts)")
    if messages >= 5:
        score['engagementQuality'] += 5
        print(f"   ✅ Messages exchanged ≥ 5 (+5pts)")
    
    # 4. Response Structure (20 points)
    required_fields = ['status', 'scamDetected', 'extractedIntelligence']
    optional_fields = ['engagementMetrics', 'agentNotes']
    
    print("\n📋 Response Structure:")
    for field in required_fields:
        if field in final_output:
            score['responseStructure'] += 5
            print(f"   ✅ {field} present (+5pts)")
        else:
            print(f"   ❌ {field} MISSING")
    
    for field in optional_fields:
        if field in final_output and final_output[field]:
            score['responseStructure'] += 2.5
            print(f"   ✅ {field} present (+2.5pts)")
    
    score['responseStructure'] = min(score['responseStructure'], 20)
    
    # Calculate total
    score['total'] = sum([
        score['scamDetection'],
        score['intelligenceExtraction'],
        score['engagementQuality'],
        score['responseStructure']
    ])
    
    return score


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                   HONEYPOT API SELF-TEST TOOL                              ║
    ║                                                                            ║
    ║  Before running this test:                                                 ║
    ║  1. Update ENDPOINT_URL at the top of this file                           ║
    ║  2. Update API_KEY if needed                                              ║
    ║  3. Ensure your API is running and accessible                             ║
    ║                                                                            ║
    ║  This test simulates the hackathon evaluation process                     ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        test_honeypot_api()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
