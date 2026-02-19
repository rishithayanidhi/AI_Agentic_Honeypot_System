"""
Environment Variables Diagnostic Script
Run this to check if API keys are properly loaded
"""
import os
from config import settings

print("=" * 60)
print("🔍 ENVIRONMENT VARIABLES DIAGNOSTIC")
print("=" * 60)

# Check LLM Provider
print(f"\n📌 LLM Provider: {settings.LLM_PROVIDER}")

# Check Anthropic
print(f"\n🔑 Anthropic API Key:")
if settings.ANTHROPIC_API_KEY:
    key = settings.ANTHROPIC_API_KEY
    print(f"   ✅ Set: ...{key[-8:]}")
else:
    print(f"   ❌ NOT SET")

# Check Gemini Keys
print(f"\n🔑 Google Gemini API Keys:")
gemini_keys = settings.get_gemini_api_keys()
if gemini_keys:
    print(f"   ✅ Found {len(gemini_keys)} key(s):")
    for i, key in enumerate(gemini_keys, 1):
        print(f"      {i}. ...{key[-8:]}")
else:
    print(f"   ❌ NO KEYS FOUND")
    print(f"\n   Checking individual keys:")
    for i in range(1, 11):
        key_name = f"GOOGLE_API_KEY{'_' + str(i) if i > 1 else ''}"
        key_value = getattr(settings, key_name, None)
        if key_value:
            print(f"      {key_name}: {key_value[:20]}...")
        else:
            print(f"      {key_name}: NOT SET")

# Check OpenAI
print(f"\n🔑 OpenAI API Key:")
if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key-here":
    key = settings.OPENAI_API_KEY
    print(f"   ✅ Set: ...{key[-8:]}")
else:
    print(f"   ❌ NOT SET")

# Check Model Names
print(f"\n📝 Model Configuration:")
print(f"   Anthropic Model: {settings.ANTHROPIC_MODEL}")
print(f"   Gemini Model: {settings.GEMINI_MODEL}")
print(f"   OpenAI Model: {settings.OPENAI_MODEL}")

# Check GUVI Config
print(f"\n🔗 GUVI Callback URL:")
print(f"   {settings.GUVI_CALLBACK_URL}")

# Check Performance Settings
print(f"\n⚡ Performance Settings:")
print(f"   Max Tokens (Detection): {settings.LLM_MAX_TOKENS_DETECTION}")
print(f"   Max Tokens (Response): {settings.LLM_MAX_TOKENS_RESPONSE}")
print(f"   Request Timeout: {settings.LLM_REQUEST_TIMEOUT}s")

# Check if running on Render
print(f"\n🌐 Deployment Info:")
if os.getenv('RENDER'):
    print(f"   ✅ Running on Render")
    print(f"   Service: {os.getenv('RENDER_SERVICE_NAME', 'N/A')}")
else:
    print(f"   🏠 Running locally")

print("\n" + "=" * 60)
print("✅ Diagnostic complete!")
print("=" * 60)

# Summary
print(f"\n📊 SUMMARY:")
issues = []

if settings.LLM_PROVIDER == "gemini" and not gemini_keys:
    issues.append("❌ CRITICAL: LLM_PROVIDER is 'gemini' but no Gemini keys found!")
elif settings.LLM_PROVIDER == "anthropic" and not settings.ANTHROPIC_API_KEY:
    issues.append("❌ CRITICAL: LLM_PROVIDER is 'anthropic' but no Anthropic key found!")

if not gemini_keys and not settings.ANTHROPIC_API_KEY:
    issues.append("❌ CRITICAL: No API keys found for any LLM provider!")

if issues:
    print("\n🚨 ISSUES DETECTED:")
    for issue in issues:
        print(f"   {issue}")
    print("\n💡 FIX:")
    print("   1. Go to Render Dashboard → Your Service → Environment")
    print("   2. Add environment variables from RENDER_ENV_VARIABLES.txt")
    print("   3. Mark API keys as 'Secret'")
    print("   4. Save and redeploy")
else:
    print("   ✅ All checks passed!")

print("\n")
