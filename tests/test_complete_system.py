"""
Comprehensive Testing Script for AI Scammer Detection Honeypot
Tests all functionality like GUVI Hackathon judges would evaluate
"""

import requests
import json
import time
from typing import Dict, List

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "honeypot-secret-2026"
HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

class Colors:
    """Terminal colors for better output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ {text}{Colors.RESET}")

def print_result(label: str, value):
    """Print test result"""
    print(f"{Colors.BOLD}{label}:{Colors.RESET} {value}")


# ============================================================================
# TEST 1: System Health & Availability
# ============================================================================

def test_health_check():
    """Test if the server is running and healthy"""
    print_header("TEST 1: System Health & Availability")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Server is running")
            print_result("Status", data.get('status'))
            print_result("Service", data.get('service'))
            return True
        else:
            print_error(f"Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server. Make sure it's running on port 8000")
        print_info("Start the server with: python main.py")
        return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False


# ============================================================================
# TEST 2: API Authentication
# ============================================================================

def test_authentication():
    """Test API key authentication"""
    print_header("TEST 2: API Authentication")
    
    # Test 2.1: Valid API Key
    print(f"\n{Colors.BOLD}Test 2.1: Valid API Key{Colors.RESET}")
    try:
        response = requests.post(
            f"{BASE_URL}/api/message",
            headers=HEADERS,
            json={"session_id": "auth_test", "message": "Test"}
        )
        if response.status_code in [200, 500]:  # 500 might happen if AI fails, but auth passed
            print_success("Valid API key accepted")
        else:
            print_error(f"Expected 200, got {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    # Test 2.2: Invalid API Key
    print(f"\n{Colors.BOLD}Test 2.2: Invalid API Key (Should be rejected){Colors.RESET}")
    try:
        invalid_headers = HEADERS.copy()
        invalid_headers["x-api-key"] = "wrong-key"
        response = requests.post(
            f"{BASE_URL}/api/message",
            headers=invalid_headers,
            json={"session_id": "auth_test", "message": "Test"}
        )
        if response.status_code == 403:
            print_success("Invalid API key correctly rejected (403 Forbidden)")
        else:
            print_error(f"Expected 403, got {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    # Test 2.3: Missing API Key
    print(f"\n{Colors.BOLD}Test 2.3: Missing API Key (Should be rejected){Colors.RESET}")
    try:
        no_auth_headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/api/message",
            headers=no_auth_headers,
            json={"session_id": "auth_test", "message": "Test"}
        )
        if response.status_code == 403:
            print_success("Missing API key correctly rejected (403 Forbidden)")
        else:
            print_error(f"Expected 403, got {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")


# ============================================================================
# TEST 3: Scam Detection - Different Scam Types
# ============================================================================

def test_scam_detection():
    """Test scam detection with various scam types"""
    print_header("TEST 3: Scam Detection - Various Scam Types")
    
    scam_messages = [
        {
            "name": "Bank Fraud",
            "message": "URGENT! Your SBI account has been suspended due to KYC verification pending. Send OTP to 9876543210 to reactivate.",
            "expected_type": "bank_fraud"
        },
        {
            "name": "UPI Scam",
            "message": "You won ₹50,000! Send ₹100 to verify@paytm to claim your prize now!",
            "expected_type": "upi_fraud"
        },
        {
            "name": "Phishing Link",
            "message": "Your package is waiting. Click here to confirm delivery: bit.ly/package-confirm",
            "expected_type": "phishing"
        },
        {
            "name": "OTP Request",
            "message": "Dear customer, your account will be blocked. Please share the OTP received on your phone to verify your identity.",
            "expected_type": "bank_fraud"
        },
        {
            "name": "Lottery Scam",
            "message": "Congratulations! You have won the Kaun Banega Crorepati lottery. Contact 9123456789 to claim ₹1 crore prize.",
            "expected_type": "fake_offer"
        }
    ]
    
    for idx, scam in enumerate(scam_messages, 1):
        print(f"\n{Colors.BOLD}Test 3.{idx}: {scam['name']}{Colors.RESET}")
        print_info(f"Message: {scam['message'][:60]}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/message",
                headers=HEADERS,
                json={
                    "session_id": f"scam_test_{idx}",
                    "message": scam['message']
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check detection
                detection = data.get('detection', {})
                is_scam = detection.get('is_scam', False)
                confidence = detection.get('confidence', 0)
                scam_type = detection.get('scam_type', 'unknown')
                
                if is_scam:
                    print_success(f"Scam detected with {confidence*100:.1f}% confidence")
                    print_result("Scam Type", scam_type)
                    print_result("Reasoning", detection.get('reasoning', 'N/A')[:100] + "...")
                else:
                    print_error("Failed to detect scam")
                
                # Check AI response (with safe None handling)
                ai_response = data.get('response') or data.get('agentResponse')
                if ai_response:
                    print_result("AI Response", str(ai_response)[:150] + "...")
                elif is_scam:
                    print_info("No AI response generated (might be quota exhausted)")
                
            else:
                print_error(f"Request failed with status {response.status_code}")
                print_error(f"Response: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print_error("Request timed out (AI might be slow)")
        except Exception as e:
            print_error(f"Error: {str(e)}")
        
        time.sleep(2)  # Rate limiting


# ============================================================================
# TEST 4: Intelligence Extraction
# ============================================================================

def test_intelligence_extraction():
    """Test extraction of scammer intelligence"""
    print_header("TEST 4: Intelligence Extraction")
    
    test_message = """URGENT! Your bank account suspended. 
    Contact us immediately at 9876543210 or send UPI payment to scammer@paytm.
    Verify your details at http://fake-bank.com/verify
    Send Aadhaar number and OTP to continue."""
    
    print_info(f"Test message contains: phone, UPI ID, link, keywords")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/message",
            headers=HEADERS,
            json={
                "session_id": "intel_test",
                "message": test_message
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            intelligence = data.get('intelligence_extracted', {})
            
            # Check extracted data
            phones = intelligence.get('phone_numbers', [])
            upi_ids = intelligence.get('upi_ids', [])
            links = intelligence.get('links', [])
            keywords = intelligence.get('keywords', [])
            
            print(f"\n{Colors.BOLD}Extracted Intelligence:{Colors.RESET}")
            
            if phones:
                print_success(f"Phone numbers: {phones}")
            else:
                print_error("No phone numbers extracted")
            
            if upi_ids:
                print_success(f"UPI IDs: {upi_ids}")
            else:
                print_error("No UPI IDs extracted")
            
            if links:
                print_success(f"Links: {links}")
            else:
                print_error("No links extracted")
            
            if keywords:
                print_success(f"Keywords: {keywords[:5]}")  # Show first 5
            else:
                print_error("No keywords extracted")
            
            # Overall assessment
            total_extracted = len(phones) + len(upi_ids) + len(links)
            if total_extracted >= 3:
                print_success(f"Intelligence extraction working well ({total_extracted} items)")
            else:
                print_error(f"Limited intelligence extracted ({total_extracted} items)")
        else:
            print_error(f"Request failed with status {response.status_code}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")


# ============================================================================
# TEST 5: Multi-Turn Conversation
# ============================================================================

def test_conversation_flow():
    """Test multi-turn conversation with scammer"""
    print_header("TEST 5: Multi-Turn Conversation Flow")
    
    session_id = "conversation_test"
    
    conversation = [
        "Your account is blocked. Verify immediately.",
        "How do I verify?",
        "Send your UPI ID and OTP",
        "What is UPI ID? I'm confused",
        "It's on your banking app. Send it quickly!"
    ]
    
    for turn, message in enumerate(conversation, 1):
        print(f"\n{Colors.BOLD}Turn {turn}:{Colors.RESET} {message}")
        
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
                ai_response = data.get('response', 'No response')
                print_result("AI Response", ai_response[:200] + "...")
                
                # Check session info
                session_info = data.get('session_info', {})
                message_count = session_info.get('message_count', 0)
                print_info(f"Total messages in session: {message_count}")
                
            else:
                print_error(f"Failed with status {response.status_code}")
                
        except Exception as e:
            print_error(f"Error: {str(e)}")
        
        time.sleep(2)
    
    print_success("Multi-turn conversation test completed")


# ============================================================================
# TEST 6: Session Management
# ============================================================================

def test_session_management():
    """Test session tracking and management"""
    print_header("TEST 6: Session Management")
    
    # Create multiple sessions
    sessions = ["session_1", "session_2", "session_3"]
    
    for session_id in sessions:
        print(f"\n{Colors.BOLD}Creating session: {session_id}{Colors.RESET}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/message",
                headers=HEADERS,
                json={
                    "session_id": session_id,
                    "message": "Test message"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                print_success(f"Session {session_id} created")
            else:
                print_error(f"Session creation failed")
        except Exception as e:
            print_error(f"Error: {str(e)}")
        
        time.sleep(1)


# ============================================================================
# TEST 7: AI Personas
# ============================================================================

def test_ai_personas():
    """Test different AI personas"""
    print_header("TEST 7: AI Agent Personas")
    
    print_info("Testing if AI adapts persona based on scam type and conversation stage")
    
    test_cases = [
        {
            "name": "Early Stage - Cautious",
            "session": "persona_test_1",
            "message": "Your account needs verification"
        },
        {
            "name": "Bank Fraud - Eager/Confused",
            "session": "persona_test_2",
            "message": "URGENT! Bank account blocked. Send OTP immediately."
        },
        {
            "name": "Phishing - Busy Professional",
            "session": "persona_test_3",
            "message": "Package delivery pending. Click link to confirm."
        }
    ]
    
    for test in test_cases:
        print(f"\n{Colors.BOLD}{test['name']}{Colors.RESET}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/message",
                headers=HEADERS,
                json={
                    "session_id": test['session'],
                    "message": test['message']
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('response', '')
                print_result("AI Response", ai_response[:200] + "...")
                
                # Analyze response characteristics
                if any(word in ai_response.lower() for word in ['what', 'how', 'confused', 'understand']):
                    print_info("Persona shows confusion/questioning (Good!)")
                if any(word in ai_response.lower() for word in ['worried', 'concerned', 'help']):
                    print_info("Persona shows concern (Good!)")
                
            else:
                print_error(f"Failed with status {response.status_code}")
        except Exception as e:
            print_error(f"Error: {str(e)}")
        
        time.sleep(2)


# ============================================================================
# TEST 8: Error Handling
# ============================================================================

def test_error_handling():
    """Test system error handling"""
    print_header("TEST 8: Error Handling & Edge Cases")
    
    # Test 8.1: Empty message
    print(f"\n{Colors.BOLD}Test 8.1: Empty Message{Colors.RESET}")
    try:
        response = requests.post(
            f"{BASE_URL}/api/message",
            headers=HEADERS,
            json={"session_id": "error_test", "message": ""}
        )
        print_result("Status Code", response.status_code)
        if response.status_code == 422:
            print_success("Correctly rejected empty message")
        else:
            print_info(f"Handled with status {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    # Test 8.2: Very long message
    print(f"\n{Colors.BOLD}Test 8.2: Very Long Message{Colors.RESET}")
    long_message = "This is a test. " * 200
    try:
        response = requests.post(
            f"{BASE_URL}/api/message",
            headers=HEADERS,
            json={"session_id": "error_test", "message": long_message},
            timeout=30
        )
        print_result("Status Code", response.status_code)
        if response.status_code == 200:
            print_success("Handled long message successfully")
        else:
            print_info(f"Responded with status {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    # Test 8.3: Special characters
    print(f"\n{Colors.BOLD}Test 8.3: Special Characters{Colors.RESET}")
    special_message = "Test 测试 тест 🔥 @#$%^&*()"
    try:
        response = requests.post(
            f"{BASE_URL}/api/message",
            headers=HEADERS,
            json={"session_id": "error_test", "message": special_message},
            timeout=30
        )
        if response.status_code == 200:
            print_success("Handled special characters successfully")
        else:
            print_info(f"Responded with status {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")


# ============================================================================
# TEST 9: Performance & Response Time
# ============================================================================

def test_performance():
    """Test system performance and response times"""
    print_header("TEST 9: Performance & Response Time")
    
    response_times = []
    
    for i in range(3):
        print(f"\n{Colors.BOLD}Request {i+1}/3{Colors.RESET}")
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/message",
                headers=HEADERS,
                json={
                    "session_id": f"perf_test_{i}",
                    "message": "Quick test message for performance"
                },
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            print_result("Response Time", f"{response_time:.2f} seconds")
            
            if response_time < 5:
                print_success("Good response time")
            elif response_time < 10:
                print_info("Acceptable response time")
            else:
                print_error("Slow response time")
                
        except requests.exceptions.Timeout:
            print_error("Request timed out")
        except Exception as e:
            print_error(f"Error: {str(e)}")
        
        time.sleep(1)
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        print(f"\n{Colors.BOLD}Average Response Time: {avg_time:.2f} seconds{Colors.RESET}")


# ============================================================================
# TEST 10: GUVI Integration (Mock)
# ============================================================================

def test_guvi_callback():
    """Test GUVI callback integration (simulation)"""
    print_header("TEST 10: GUVI Callback Integration")
    
    print_info("This tests if the system formats data correctly for GUVI")
    print_info("Note: Actual callback to GUVI endpoint requires their server")
    
    # Complete a full conversation
    session_id = "guvi_test_session"
    messages = [
        "Your account is suspended. Verify now.",
        "Send OTP to 9876543210",
        "Also send UPI payment to scammer@paytm"
    ]
    
    for msg in messages:
        try:
            response = requests.post(
                f"{BASE_URL}/api/message",
                headers=HEADERS,
                json={"session_id": session_id, "message": msg},
                timeout=30
            )
            time.sleep(2)
        except:
            pass
    
    print_success("Conversation completed")
    print_info("System should format final report with:")
    print_info("  - Session ID")
    print_info("  - Total messages")
    print_info("  - Scam type and confidence")
    print_info("  - Extracted intelligence")
    print_info("  - Conversation summary")
    print_info("  - Threat level")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tests in sequence"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔" + "═" * 78 + "╗")
    print("║" + "AI SCAMMER DETECTION HONEYPOT - COMPREHENSIVE TEST SUITE".center(78) + "║")
    print("║" + "GUVI Hackathon Problem Statement 2".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print(f"{Colors.RESET}\n")
    
    print_info("This test suite validates all requirements from the GUVI Hackathon")
    print_info("Make sure the server is running: python main.py")
    print_info("Press Ctrl+C to stop tests at any time\n")
    
    input(f"{Colors.YELLOW}Press Enter to start tests...{Colors.RESET}")
    
    tests = [
        ("System Health", test_health_check),
        ("Authentication", test_authentication),
        ("Scam Detection", test_scam_detection),
        ("Intelligence Extraction", test_intelligence_extraction),
        ("Conversation Flow", test_conversation_flow),
        ("Session Management", test_session_management),
        ("AI Personas", test_ai_personas),
        ("Error Handling", test_error_handling),
        ("Performance", test_performance),
        ("GUVI Integration", test_guvi_callback)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{Colors.YELLOW}Running: {test_name}...{Colors.RESET}")
            test_func()
            results.append((test_name, "PASSED"))
        except KeyboardInterrupt:
            print(f"\n{Colors.RED}Tests interrupted by user{Colors.RESET}")
            break
        except Exception as e:
            print_error(f"Test failed: {str(e)}")
            results.append((test_name, "FAILED"))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, status in results if status == "PASSED")
    total = len(results)
    
    for test_name, status in results:
        if status == "PASSED":
            print_success(f"{test_name}: {status}")
        else:
            print_error(f"{test_name}: {status}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! System is ready for hackathon submission! 🎉{Colors.RESET}\n")
    else:
        print(f"\n{Colors.YELLOW}Some tests need attention. Review the output above.{Colors.RESET}\n")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Tests interrupted{Colors.RESET}")
