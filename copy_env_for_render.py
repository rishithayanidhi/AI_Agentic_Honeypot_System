"""
Copy Production Environment Variables for Render Deployment
This script outputs all environment variables formatted for easy copy-paste to Render Dashboard
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("PRODUCTION ENVIRONMENT VARIABLES FOR RENDER")
print("=" * 80)
print()
print("Copy these to Render Dashboard → Environment tab")
print("Mark all GOOGLE_API_KEY* as 'Secret' (click eye icon)")
print()
print("-" * 80)
print()

# Essential variables
essential_vars = {
    'API_KEY': os.getenv('API_KEY', 'honeypot-secret-2026'),
    'LLM_PROVIDER': 'gemini',
    'GEMINI_MODEL': os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
    'GUVI_CALLBACK_URL': os.getenv('GUVI_CALLBACK_URL', 'https://hackathon.guvi.in/api/updateHoneyPotFinalResult'),
}

# Gemini API Keys (collect all)
gemini_keys = {}
for i in range(1, 21):
    key_name = 'GOOGLE_API_KEY' if i == 1 else f'GOOGLE_API_KEY_{i}'
    key_value = os.getenv(key_name)
    if key_value and key_value != 'your-google-api-key-here':
        gemini_keys[key_name] = key_value

# Performance settings (ULTRA-SPEED - Sub-2s Target)
performance_vars = {
    'CACHE_MAX_SIZE': '2000',
    'LLM_MAX_TOKENS_DETECTION': '350',
    'LLM_MAX_TOKENS_RESPONSE': '600',
    'LLM_REQUEST_TIMEOUT': '10',
    'LLM_TEMPERATURE': '0.7',
    'ENABLE_FAST_PATH': 'true',
    'FAST_PATH_THRESHOLD': '3',
}

# Session settings
session_vars = {
    'SESSION_TIMEOUT_MINUTES': '30',
    'MAX_MESSAGES_PER_SESSION': '50',
}

# Security settings
security_vars = {
    'RATE_LIMIT_PER_MINUTE': '100',
    'MAX_REQUEST_SIZE': '1048576',
    'SCAM_DETECTION_THRESHOLD': '0.4',
    'SCAM_SCORE_THRESHOLD': '1',
}

# Debug settings
debug_vars = {
    'INCLUDE_DEBUG_INFO': 'false',
    'DEBUG': 'false',
    'LOG_LEVEL': 'INFO',
}

# Print all variables
print("# Essential Configuration")
for key, value in essential_vars.items():
    print(f"{key}={value}")

print()
print(f"# Gemini API Keys ({len(gemini_keys)} keys - {len(gemini_keys) * 20} requests/day)")
for key, value in gemini_keys.items():
    print(f"{key}={value}")

print()
print("# Performance Settings")
for key, value in performance_vars.items():
    print(f"{key}={value}")

print()
print("# Session Management")
for key, value in session_vars.items():
    print(f"{key}={value}")

print()
print("# Security & Detection")
for key, value in security_vars.items():
    print(f"{key}={value}")

print()
print("# Debug Settings")
for key, value in debug_vars.items():
    print(f"{key}={value}")

print()
print("-" * 80)
print()
print(f"✅ Total Variables: {len(essential_vars) + len(gemini_keys) + len(performance_vars) + len(session_vars) + len(security_vars) + len(debug_vars)}")
print(f"✅ Gemini API Keys: {len(gemini_keys)}")
print(f"✅ Daily Capacity: ~{len(gemini_keys) * 20} requests/day")
print()
print("🔒 IMPORTANT: Mark all GOOGLE_API_KEY* as 'Secret' in Render Dashboard!")
print()
print("=" * 80)
