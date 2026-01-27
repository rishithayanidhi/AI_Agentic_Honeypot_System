"""
Test script to verify dynamic LLM model selection works
"""
# -*- coding: utf-8 -*-
import sys
import os
import logging
import warnings

# Suppress Pydantic warnings from google-genai library
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic._internal._fields")

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Change working directory to project root so .env can be found
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.scam_detector import ScamDetector
from src.services.ai_agent import AIAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_scam_detector():
    """Test scam detector with dynamic model selection"""
    print("\n" + "="*60)
    print("TESTING SCAM DETECTOR")
    print("="*60)
    
    detector = ScamDetector()
    
    print(f"\nAvailable providers: {detector.available_providers}")
    print(f"Primary provider: {detector.primary_provider}")
    
    # Test message
    test_message = "Your bank account will be blocked! Send OTP immediately to verify at http://fake-bank.com"
    
    print(f"\nTest message: {test_message}")
    print("\nAttempting detection...")
    
    result = detector.detect_scam(test_message)
    
    print(f"\n✓ Detection Result:")
    print(f"  - Is Scam: {result.get('is_scam')}")
    print(f"  - Confidence: {result.get('confidence')}")
    print(f"  - Scam Type: {result.get('scam_type')}")
    print(f"  - Reasoning: {result.get('reasoning')}")
    
    return result

def test_ai_agent():
    """Test AI agent with dynamic model selection"""
    print("\n" + "="*60)
    print("TESTING AI AGENT")
    print("="*60)
    
    agent = AIAgent()
    
    print(f"\nAvailable providers: {agent.available_providers}")
    print(f"Primary provider: {agent.primary_provider}")
    
    # Test message
    scammer_msg = "Sir, your bank account has issue. Please share OTP to fix."
    
    print(f"\nScammer message: {scammer_msg}")
    print("\nGenerating response...")
    
    result = agent.generate_response(
        scammer_message=scammer_msg,
        conversation_history=[],
        persona="cautious_user",
        scam_type="bank_fraud",
        extracted_intel={},
        message_count=1
    )
    
    print(f"\n✓ Agent Response:")
    print(f"  - Response: {result.get('response')}")
    print(f"  - Strategy: {result.get('strategy')}")
    print(f"  - Should Continue: {result.get('should_continue')}")
    
    return result

if __name__ == "__main__":
    try:
        # Test both services
        detector_result = test_scam_detector()
        agent_result = test_ai_agent()
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        if detector_result and detector_result.get('is_scam') is not None:
            print("✓ Scam Detector: WORKING")
        else:
            print("✗ Scam Detector: FAILED")
        
        if agent_result and agent_result.get('response'):
            print("✓ AI Agent: WORKING")
        else:
            print("✗ AI Agent: FAILED")
        
        print("\n✓ All tests completed!")
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
