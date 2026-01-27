# -*- coding: utf-8 -*-
"""
Production Readiness Validation
Final check before deployment
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
import time
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://localhost:8000"
API_KEY = "honeypot-secret-2026"

def test_api_health():
    """Check if API is running"""
    for attempt in range(3):
        try:
            resp = requests.get(f"{BASE_URL}/health", timeout=10)
            if resp.status_code == 200:
                return True
            time.sleep(1)
        except:
            if attempt < 2:
                time.sleep(1)
    return False

def test_scam_detection():
    """Test scam detection functionality"""
    try:
        resp = requests.post(
            f"{BASE_URL}/api/message",
            headers={"x-api-key": API_KEY},
            json={
                "session_id": "prod-test-001",
                "message": "Your bank account is blocked. Share OTP immediately."
            },
            timeout=20
        )
        if resp.status_code != 200:
            return False
        
        data = resp.json()
        return (data.get('isScam') == True and 
                data.get('confidence', 0) >= 0.5 and
                data.get('response') is not None)
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_ai_response():
    """Test AI agent response generation"""
    try:
        resp = requests.post(
            f"{BASE_URL}/api/message",
            headers={"x-api-key": API_KEY},
            json={
                "session_id": "prod-test-002",
                "message": "Send me your UPI ID to verify"
            },
            timeout=20
        )
        if resp.status_code != 200:
            return False
        
        data = resp.json()
        return data.get('response') is not None and len(data.get('response', '')) > 0
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_intelligence_extraction():
    """Test intelligence extraction"""
    try:
        resp = requests.post(
            f"{BASE_URL}/api/message",
            headers={"x-api-key": API_KEY},
            json={
                "session_id": "prod-test-003",
                "message": "Call 9876543210 or send to verify@paytm"
            },
            timeout=20
        )
        if resp.status_code != 200:
            return False
        
        data = resp.json()
        intel = data.get('extractedIntelligence', {})
        return (len(intel.get('phoneNumbers', [])) > 0 or 
                len(intel.get('upiIds', [])) > 0)
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_authentication():
    """Test API key authentication"""
    try:
        # Test without key
        resp = requests.post(
            f"{BASE_URL}/api/message",
            json={"session_id": "test", "message": "test"},
            timeout=10
        )
        if resp.status_code != 403:
            return False
        
        # Test with wrong key
        resp = requests.post(
            f"{BASE_URL}/api/message",
            headers={"x-api-key": "wrong-key"},
            json={"session_id": "test", "message": "test"},
            timeout=10
        )
        return resp.status_code == 403
    except Exception as e:
        print(f"   Error: {e}")
        return False

def main():
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}PRODUCTION READINESS VALIDATION{Style.RESET_ALL:^70}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    tests = [
        ("API Health Check", test_api_health),
        ("Scam Detection", test_scam_detection),
        ("AI Response Generation", test_ai_response),
        ("Intelligence Extraction", test_intelligence_extraction),
        ("API Authentication", test_authentication),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"{Fore.YELLOW}Testing: {test_name}...{Style.RESET_ALL}", end=" ")
        try:
            result = test_func()
            if result:
                print(f"{Fore.GREEN}PASS{Style.RESET_ALL}")
                results.append(True)
            else:
                print(f"{Fore.RED}FAIL{Style.RESET_ALL}")
                results.append(False)
        except Exception as e:
            print(f"{Fore.RED}ERROR: {str(e)}{Style.RESET_ALL}")
            results.append(False)
        time.sleep(1)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Results: {passed}/{total} tests passed{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    if passed == total:
        print(f"{Fore.GREEN}SUCCESS: System is PRODUCTION READY!{Style.RESET_ALL}\n")
        return 0
    else:
        print(f"{Fore.RED}WARNING: {total-passed} test(s) failed - review needed{Style.RESET_ALL}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
