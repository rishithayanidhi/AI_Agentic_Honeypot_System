"""
Master Test Runner - Runs all tests for production readiness validation
"""
import subprocess
import sys
import time
from colorama import init, Fore, Style

init(autoreset=True)

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{text:^70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

def print_success(text):
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.YELLOW}ℹ️  {text}{Style.RESET_ALL}")

def run_test(test_name, test_file):
    """Run a single test file and return success status"""
    print_info(f"Running {test_name}...")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print_success(f"{test_name} PASSED")
            return True
        else:
            print_error(f"{test_name} FAILED")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print_error(f"{test_name} TIMED OUT")
        return False
    except Exception as e:
        print_error(f"{test_name} ERROR: {str(e)}")
        return False

def main():
    print_header("AI SCAMMER DETECTION - PRODUCTION READINESS TEST SUITE")
    
    tests = [
        ("LLM Models Test", "test_llm_models.py"),
        ("Phishing Detection Test", "test_phishing_detection.py"),
        ("AI Persona Test", "test_ai_persona.py"),
        ("All Scam Types Test", "test_all_scams.py"),
        ("Complete System Test", "test_complete_system.py"),
        ("GUVI Endpoint Test", "test_guvi_endpoint.py"),
    ]
    
    results = {}
    start_time = time.time()
    
    for test_name, test_file in tests:
        print(f"\n{'-'*70}")
        success = run_test(test_name, test_file)
        results[test_name] = success
        time.sleep(2)  # Brief pause between tests
    
    # Print summary
    print_header("TEST SUITE SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, success in results.items():
        if success:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    duration = time.time() - start_time
    
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Total Tests: {total}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Passed: {passed}{Style.RESET_ALL}")
    print(f"{Fore.RED}Failed: {total - passed}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Duration: {duration:.1f}s{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    if passed == total:
        print_success("🎉 ALL TESTS PASSED - PRODUCTION READY! 🎉")
        return 0
    else:
        print_error(f"⚠️  {total - passed} TEST(S) FAILED - NEEDS ATTENTION")
        return 1

if __name__ == "__main__":
    sys.exit(main())
