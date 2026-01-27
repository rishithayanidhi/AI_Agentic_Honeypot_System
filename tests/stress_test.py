# -*- coding: utf-8 -*-
"""
Quick stress test - verify no rate limits
"""
import requests
import time

BASE_URL = "http://localhost:8000"
API_KEY = "honeypot-secret-2026"

test_messages = [
    "You won ₹50,000! Share your bank details.",
    "Urgent! Your account is blocked. Send OTP now.",
    "Click this link to claim your prize: bit.ly/prize123",
    "Send money to 9876543210 immediately",
    "Your UPI payment failed. Verify at paytm@upi",
    "Bank manager here. Need your CVV to reactivate.",
    "Congratulations! You're selected for lottery.",
    "KYC pending. Submit Aadhaar or account freezes.",
    "Government refund available. Share account number.",
    "WhatsApp verification required. Enter code 1234."
]

print("\n" + "="*60)
print("🚀 STRESS TEST - 10 Rapid Requests")
print("="*60 + "\n")

start_time = time.time()
results = []

for i, message in enumerate(test_messages, 1):
    try:
        req_start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/message",
            headers={"x-api-key": API_KEY},
            json={
                "session_id": f"stress-test-{i}",
                "message": message
            },
            timeout=30
        )
        req_time = time.time() - req_start
        
        if response.status_code == 200:
            data = response.json()
            scam = data.get('scamDetected', False)
            conf = data.get('confidence', 0)
            has_response = bool(data.get('response'))
            results.append((True, req_time, scam, conf))
            print(f"✅ Test {i:2d}: {req_time:.2f}s | Scam: {scam} ({conf:.0%}) | Response: {has_response}")
        else:
            results.append((False, req_time, False, 0))
            print(f"❌ Test {i:2d}: Failed - Status {response.status_code}")
            
    except Exception as e:
        results.append((False, 0, False, 0))
        print(f"❌ Test {i:2d}: Error - {str(e)[:50]}")

total_time = time.time() - start_time

print("\n" + "="*60)
print("📊 RESULTS")
print("="*60)

passed = sum(1 for r in results if r[0])
avg_time = sum(r[1] for r in results if r[0]) / passed if passed > 0 else 0
scam_detected = sum(1 for r in results if r[2])

print(f"\n✅ Passed: {passed}/10")
print(f"⏱️  Average response time: {avg_time:.2f}s")
print(f"🎯 Scams detected: {scam_detected}/10")
print(f"⚡ Total time: {total_time:.1f}s")
print(f"🚀 Throughput: {10/total_time:.1f} requests/second")

if passed == 10:
    print("\n🎉 ALL TESTS PASSED - NO RATE LIMITS!")
    print("✅ System is EVALUATION-READY!")
else:
    print(f"\n⚠️  {10-passed} tests failed")

print("\n" + "="*60 + "\n")
