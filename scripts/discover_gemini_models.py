"""
Discover available Gemini models
"""
from google import genai
from config import settings

print("Discovering available Gemini models...\n")

try:
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)
    
    print("Attempting to list models...")
    
    # Try to list all available models
    try:
        models = client.models.list()
        print("\n✓ Available Gemini Models:")
        print("="*60)
        for model in models:
            print(f"  - {model.name}")
            if hasattr(model, 'supported_generation_methods'):
                print(f"    Methods: {model.supported_generation_methods}")
        print("="*60)
    except Exception as e:
        print(f"✗ Could not list models: {e}")
    
    # Try ACTUAL available model names from the list above
    print("\n\nTesting ACTUAL available model names:")
    print("="*60)
    
    test_models = [
        "models/gemini-2.5-flash",
        "models/gemini-2.5-pro",
        "models/gemini-flash-latest",
        "models/gemini-pro-latest",
        "models/gemini-2.0-flash",
        "models/gemini-2.0-flash-001",
        "models/gemini-2.5-flash-lite",
        "models/gemini-flash-lite-latest",
    ]
    
    working_models = []
    
    for model_name in test_models:
        try:
            print(f"\nTrying: {model_name}...", end=" ")
            response = client.models.generate_content(
                model=model_name,
                contents="Say 'hello' in JSON format: {\"message\": \"hello\"}"
            )
            print("✓ WORKS!")
            working_models.append(model_name)
            print(f"  Response: {response.text[:100]}")
        except Exception as e:
            print(f"✗ Failed: {str(e)[:80]}")
    
    print("\n" + "="*60)
    if working_models:
        print(f"\n✓ WORKING MODELS FOUND: {len(working_models)}")
        for model in working_models:
            print(f"  - {model}")
        print(f"\n✓ Update .env with: GEMINI_MODEL={working_models[0]}")
    else:
        print("\n✗ NO WORKING MODELS FOUND")
        print("\nPossible issues:")
        print("  1. API key may be invalid or expired")
        print("  2. Gemini API version mismatch")
        print("  3. Models not available in your region")
        print("  4. Check: https://ai.google.dev/gemini-api/docs/models")
    print("="*60)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
