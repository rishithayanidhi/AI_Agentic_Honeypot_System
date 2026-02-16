"""
Self-Test Script for GUVI Hackathon Evaluation
This script tests your honeypot API against the evaluation format
Run this before submitting to ensure compatibility
"""

import requests
import uuid
import json
from datetime import datetime
import time

# ========================================
# CONFIGURATION - Update these values
# ========================================
ENDPOINT_URL = "http://localhost:8000/api/message"  # Change to your deployed URL
API_KEY = "honeypot-secret-2026"  # Your API key

# Test scenarios from evaluation documentation
TEST_SCENARIOS = [
    {
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
    },
    {
        'scenarioId': 'upi_fraud',
        'name': 'UPI Fraud Multi-turn',
        'scamType': 'upi_fraud',
        'initialMessage': 'Congratulations! You have won a cashback of Rs. 5000 from Paytm. To claim your reward, please verify your UPI details. This is from official customer support.',
        'metadata': {
            'channel': 'WhatsApp',
            'language': 'English',
            'locale': 'IN'
        },
        'maxTurns': 10,
        'fakeData': {
            'upiId': 'cashback.scam@fakeupi',
            'phoneNumber': '+91-8765432109'
        }
    },
    {
        'scenarioId': 'phishing_link',
        'name': 'Phishing Link Detection',
        'scamType': 'phishing',
        'initialMessage': 'You have been selected for iPhone 15 Pro at just Rs. 999! Click here to claim: http://amaz0n-deals.fake-site.com/claim?id=12345. Offer expires in 10 minutes!',
        'metadata': {
            'channel': 'Email',
            'language': 'English',
            'locale': 'IN'
        },
        'maxTurns': 10,
        'fakeData': {
            'phishingLink': 'http://amaz0n-deals.fake-site.com/claim?id=12345',
            'emailAddress': 'offers@fake-amazon-deals.com'
        }
    }
]


def evaluate_final_output(final_output, scenario):
    """Evaluate final output using the same logic as the evaluator"""
    
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
        print("   ✅ Scam detected correctly (+20 points)")
    else:
        print("   ❌ Scam NOT detected (0 points)")
    
    # 2. Intelligence Extraction (40 points)
    extracted = final_output.get('extractedIntelligence', {})
    fake_data = scenario.get('fakeData', {})
    
    key_mapping = {
        'bankAccount': 'bankAccounts',
        'upiId': 'upiIds',
        'phoneNumber': 'phoneNumbers',
        'phishingLink': 'phishingLinks',
        'emailAddress': 'emailAddresses'
    }
    
    print("\n   Intelligence Extraction:")
    for fake_key, fake_value in fake_data.items():
        output_key = key_mapping.get(fake_key, fake_key)
        extracted_values = extracted.get(output_key, [])
        
        found = False
        if isinstance(extracted_values, list):
            if any(fake_value in str(v) for v in extracted_values):
                found = True
        elif isinstance(extracted_values, str):
            if fake_value in extracted_values:
                found = True
        
        if found:
            score['intelligenceExtraction'] += 10
            print(f"   ✅ {output_key}: Found '{fake_value}' (+10 points)")
        else:
            print(f"   ❌ {output_key}: NOT found '{fake_value}' (0 points)")
            if extracted_values:
                print(f"      Extracted: {extracted_values}")
    
    score['intelligenceExtraction'] = min(score['intelligenceExtraction'], 40)
    
    # 3. Engagement Quality (20 points)
    metrics = final_output.get('engagementMetrics', {})
    duration = metrics.get('engagementDurationSeconds', 0)
    messages = metrics.get('totalMessagesExchanged', 0)
    
    print("\n   Engagement Quality:")
    if duration > 0:
        score['engagementQuality'] += 5
        print(f"   ✅ Duration > 0s: {duration}s (+5 points)")
    else:
        print("   ❌ Duration = 0s (0 points)")
    
    if duration > 60:
        score['engagementQuality'] += 5
        print(f"   ✅ Duration > 60s (+5 points)")
    else:
        print(f"   ❌ Duration ≤ 60s (0 points)")
    
    if messages > 0:
        score['engagementQuality'] += 5
        print(f"   ✅ Messages > 0: {messages} (+5 points)")
    else:
        print("   ❌ Messages = 0 (0 points)")
    
    if messages >= 5:
        score['engagementQuality'] += 5
        print(f"   ✅ Messages ≥ 5 (+5 points)")
    else:
        print(f"   ❌ Messages < 5 (0 points)")
    
    # 4. Response Structure (20 points)
    required_fields = ['status', 'scamDetected', 'extractedIntelligence']
    optional_fields = ['engagementMetrics', 'agentNotes']
    
    print("\n   Response Structure:")
    for field in required_fields:
        if field in final_output:
            score['responseStructure'] += 5
            print(f"   ✅ {field}: present (+5 points)")
        else:
            print(f"   ❌ {field}: MISSING (0 points)")
    
    for field in optional_fields:
        if field in final_output and final_output[field]:
            score['responseStructure'] += 2.5
            print(f"   ✅ {field}: present (+2.5 points)")
        else:
            print(f"   ⚠️  {field}: missing (optional, 0 points)")
    
    score['responseStructure'] = min(score['responseStructure'], 20)
    
    # Calculate total
    score['total'] = sum([
        score['scamDetection'],
        score['intelligenceExtraction'],
        score['engagementQuality'],
        score['responseStructure']
    ])
    
    return score


def test_scenario(scenario):
    """Test a single scenario"""
    print(f"\n{'='*70}")
    print(f"Testing: {scenario['name']}")
    print(f"Scenario ID: {scenario['scenarioId']}")
    print(f"{'='*70}")
    
    session_id = str(uuid.uuid4())
    conversation_history = []
    start_time = time.time()
    
    # Setup headers
    headers = {'Content-Type': 'application/json'}
    if API_KEY:
        headers['x-api-key'] = API_KEY
    
    print(f"\n📝 Session ID: {session_id}")
    
    # Prepare message object
    message = {
        "sender": "scammer",
        "text": scenario['initialMessage'],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Prepare request
    request_body = {
        'sessionId': session_id,
        'message': message,
        'conversationHistory': conversation_history,
        'metadata': scenario['metadata']
    }
    
    print(f"\n🚨 Scammer: {scenario['initialMessage'][:100]}...")
    
    try:
        # Call your API
        response = requests.post(
            ENDPOINT_URL,
            headers=headers,
            json=request_body,
            timeout=30
        )
        
        # Check response
        if response.status_code != 200:
            print(f"\n❌ ERROR: API returned status {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        response_data = response.json()
        
        # Extract honeypot reply
        honeypot_reply = response_data.get('reply') or \
                       response_data.get('message') or \
                       response_data.get('text')
        
        if not honeypot_reply:
            print("\n❌ ERROR: No reply/message/text field in response")
            print(f"Response data: {response_data}")
            return None
        
        end_time = time.time()
        duration = int(end_time - start_time)
        
        print(f"\n🤖 Honeypot: {honeypot_reply[:100]}...")
        print(f"\n⏱️  Response Time: {duration}s")
        
        # Update conversation history
        conversation_history.append(message)
        conversation_history.append({
            'sender': 'user',
            'text': honeypot_reply,
            'timestamp': datetime.utcnow().isoformat() + "Z"
        })
        
        # Create mock final output for evaluation
        # In real evaluation, this comes from your system
        final_output = {
            "sessionId": session_id,
            "status": "completed",
            "scamDetected": response_data.get('scamDetected', True),
            "totalMessagesExchanged": len(conversation_history),
            "extractedIntelligence": response_data.get('extractedIntelligence', {}),
            "engagementMetrics": {
                "totalMessagesExchanged": len(conversation_history),
                "engagementDurationSeconds": duration
            },
            "agentNotes": response_data.get('agentNotes', "Test evaluation")
        }
        
        # Evaluate the final output
        print(f"\n{'='*70}")
        print("📊 EVALUATION RESULTS")
        print(f"{'='*70}")
        
        score = evaluate_final_output(final_output, scenario)
        
        print(f"\n{'='*70}")
        print(f"🎯 TOTAL SCORE: {score['total']:.1f}/100")
        print(f"{'='*70}")
        print(f"   Scam Detection:        {score['scamDetection']:.1f}/20")
        print(f"   Intelligence Extraction: {score['intelligenceExtraction']:.1f}/40")
        print(f"   Engagement Quality:    {score['engagementQuality']:.1f}/20")
        print(f"   Response Structure:    {score['responseStructure']:.1f}/20")
        print(f"{'='*70}")
        
        return score
        
    except requests.exceptions.Timeout:
        print("\n❌ ERROR: Request timeout (>30 seconds)")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ ERROR: Connection failed - {e}")
        print("\n💡 Make sure your server is running:")
        print("   python main.py")
        return None
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🎯 GUVI HACKATHON EVALUATION SELF-TEST")
    print("="*70)
    print(f"\nEndpoint: {ENDPOINT_URL}")
    print(f"API Key: {'✓ Set' if API_KEY else '✗ Not set'}")
    print(f"Test Scenarios: {len(TEST_SCENARIOS)}")
    
    all_scores = []
    
    for scenario in TEST_SCENARIOS:
        score = test_scenario(scenario)
        if score:
            all_scores.append(score)
        time.sleep(1)  # Small delay between tests
    
    if all_scores:
        # Calculate weighted average (assuming equal weights for demo)
        avg_score = sum(s['total'] for s in all_scores) / len(all_scores)
        
        print("\n" + "="*70)
        print("🏆 FINAL RESULTS")
        print("="*70)
        print(f"\nTested Scenarios: {len(all_scores)}/{len(TEST_SCENARIOS)}")
        print(f"Average Score: {avg_score:.1f}/100")
        
        if avg_score >= 80:
            print(f"\n✅ EXCELLENT! Your API is ready for submission!")
        elif avg_score >= 60:
            print(f"\n⚠️  GOOD! But there's room for improvement.")
        else:
            print(f"\n❌ NEEDS WORK! Review the failures above.")
        
        print("\n" + "="*70)
        print("💡 NEXT STEPS:")
        print("="*70)
        print("1. Fix any failures shown above")
        print("2. Deploy your API to Render/Railway/Heroku")
        print("3. Update ENDPOINT_URL in this script to your deployed URL")
        print("4. Run this test again to verify deployment")
        print("5. Submit on GUVI platform with:")
        print(f"   - Deployment URL: {ENDPOINT_URL}")
        print(f"   - API Key: {API_KEY}")
        print("   - GitHub URL: https://github.com/rishithayanidhi/AI_Agentic_Honeypot_System")
        print("="*70)


if __name__ == "__main__":
    main()
