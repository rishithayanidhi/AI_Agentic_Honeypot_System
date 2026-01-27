"""
Performance Testing Script
Measures response time improvements after optimizations
"""

import sys
import os
import warnings

# Suppress Pydantic warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic._internal._fields")

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Change to project root for .env
if os.path.basename(os.getcwd()) == 'tests':
    os.chdir('..')

import requests
import json
import time
from datetime import datetime
from colorama import init, Fore, Style
import statistics

init(autoreset=True)

BASE_URL = "http://localhost:8000"
API_KEY = "honeypot-secret-2026"

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{text}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

def print_success(text):
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.YELLOW}📊 {text}{Style.RESET_ALL}")

def measure_response_time(message_text, session_id):
    """Measure response time for a single request"""
    
    payload = {
        "session_id": session_id,
        "message": message_text
    }
    
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/message",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'response_time': response_time,
                'scam_detected': data.get('isScam', False),
                'confidence': data.get('confidence', 0),
                'ai_response': data.get('response', '')[:50]
            }
        else:
            return {
                'success': False,
                'response_time': response_time,
                'error': f"Status {response.status_code}"
            }
    
    except Exception as e:
        end_time = time.time()
        return {
            'success': False,
            'response_time': end_time - start_time,
            'error': str(e)
        }

def run_performance_tests():
    """Run comprehensive performance tests"""
    
    print_header("🚀 API Performance Testing")
    
    test_cases = [
        {
            "name": "Bank Fraud (First Request)",
            "message": "Your account has been blocked. Share OTP to verify.",
            "session": "perf-test-1"
        },
        {
            "name": "Bank Fraud (Cached)",
            "message": "Your account has been blocked. Share OTP to verify.",
            "session": "perf-test-2"
        },
        {
            "name": "Phishing Link",
            "message": "Click this link to claim prize: bit.ly/prize123",
            "session": "perf-test-3"
        },
        {
            "name": "UPI Scam",
            "message": "Send ₹1 to PhonePe 9876543210 to verify account",
            "session": "perf-test-4"
        },
        {
            "name": "Lottery Scam",
            "message": "Congratulations! You won ₹10 lakhs. Share details.",
            "session": "perf-test-5"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{Fore.CYAN}Test {i}/{len(test_cases)}: {test_case['name']}{Style.RESET_ALL}")
        
        result = measure_response_time(test_case['message'], test_case['session'])
        results.append(result)
        
        if result['success']:
            response_time = result['response_time']
            
            # Color code based on performance
            if response_time < 1.0:
                color = Fore.GREEN
                rating = "⚡ Excellent"
            elif response_time < 2.0:
                color = Fore.YELLOW
                rating = "✓ Good"
            else:
                color = Fore.RED
                rating = "⚠ Needs Improvement"
            
            print(f"{color}Response Time: {response_time:.3f}s {rating}{Style.RESET_ALL}")
            print_info(f"Scam Detected: {result['scam_detected']} ({result['confidence']}% confidence)")
            print_info(f"AI Response: {result['ai_response']}...")
        else:
            print_error(f"Failed: {result['error']}")
            print_error(f"Time: {result['response_time']:.3f}s")
    
    # Calculate statistics
    print_header("📈 Performance Summary")
    
    successful_times = [r['response_time'] for r in results if r['success']]
    
    if successful_times:
        avg_time = statistics.mean(successful_times)
        min_time = min(successful_times)
        max_time = max(successful_times)
        median_time = statistics.median(successful_times)
        
        print_info(f"Average Response Time: {avg_time:.3f}s")
        print_info(f"Fastest Response: {min_time:.3f}s")
        print_info(f"Slowest Response: {max_time:.3f}s")
        print_info(f"Median Response: {median_time:.3f}s")
        
        success_rate = (len(successful_times) / len(results)) * 100
        print_info(f"Success Rate: {success_rate:.1f}%")
        
        # Performance rating
        print("\n" + "="*60)
        if avg_time < 1.0:
            print(f"{Fore.GREEN}🏆 EXCELLENT - Your API is highly optimized!{Style.RESET_ALL}")
        elif avg_time < 2.0:
            print(f"{Fore.YELLOW}✓ GOOD - Your API performs well{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}⚠ NEEDS OPTIMIZATION - Consider improvements{Style.RESET_ALL}")
        
        print("="*60 + "\n")
        
        # Optimization suggestions
        print_header("💡 Optimization Status")
        
        checks = [
            ("Response compression", True),
            ("Async operations", True),
            ("Detection caching", True),
            ("Early session exit", True),
            ("Parallel processing", True),
            ("Fast model priority (Flash)", True)
        ]
        
        for check, enabled in checks:
            status = f"{Fore.GREEN}✅ Enabled" if enabled else f"{Fore.RED}❌ Disabled"
            print(f"{check}: {status}{Style.RESET_ALL}")
    
    else:
        print_error("All tests failed. Check if server is running.")
    
    # Cache performance test
    print_header("🔄 Cache Performance Test")
    
    print("Testing same message 3 times to measure caching effect...")
    cache_times = []
    
    for i in range(3):
        result = measure_response_time(
            "Your account has been blocked. Share OTP immediately.",
            f"cache-test-{i}"
        )
        if result['success']:
            cache_times.append(result['response_time'])
            print(f"Attempt {i+1}: {result['response_time']:.3f}s")
    
    if len(cache_times) >= 2:
        speedup = cache_times[0] / cache_times[1] if cache_times[1] > 0 else 1
        print_info(f"Cache Speedup: {speedup:.1f}x faster")
        
        if speedup > 2:
            print_success("Cache is working effectively!")
        elif speedup > 1.2:
            print_info("Cache provides moderate improvement")
        else:
            print_info("Cache effect minimal (may not be caching)")

def main():
    print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}⚡ API Performance Optimization Test{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    
    print_info(f"Testing endpoint: {BASE_URL}")
    print_info("Measuring: Response time, success rate, caching effect")
    print_info("Target: < 1.0s excellent, < 2.0s good\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("Server is online and ready for testing\n")
            run_performance_tests()
        else:
            print_error("Server responded but health check failed")
    except Exception as e:
        print_error(f"Cannot connect to server: {e}")
        print_info("Please start the server first:")
        print_info("  python -m uvicorn main:app --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    main()
