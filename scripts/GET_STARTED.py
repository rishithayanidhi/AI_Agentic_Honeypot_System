#!/usr/bin/env python3
"""
GET STARTED - Simple setup wizard for AI Agentic Honeypot System
Run this first: python GET_STARTED.py
"""

import os
import sys
import subprocess
from pathlib import Path

print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║          AI AGENTIC HONEYPOT SYSTEM - GET STARTED                ║
║                                                                  ║
║        Scam Detection & Intelligence Extraction System           ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

Welcome! This wizard will help you get started quickly.
""")

def ask_yes_no(question, default=True):
    """Ask a yes/no question"""
    suffix = "[Y/n]" if default else "[y/N]"
    response = input(f"{question} {suffix}: ").strip().lower()
    if not response:
        return default
    return response in ['y', 'yes']

def print_step(step_num, title):
    """Print a step header"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {title}")
    print('='*60 + "\n")

def main():
    print("Let's get you set up in 3 simple steps!\n")
    
    # Step 1: Check environment
    print_step(1, "Environment Check")
    
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python 3.9+ required. You have {version.major}.{version.minor}")
        print("\nPlease install Python 3.9 or higher and try again.")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    
    print("\nChecking for virtual environment...")
    if os.path.exists("venv"):
        print("✅ Virtual environment found")
    else:
        print("❌ No virtual environment found")
        if ask_yes_no("\nCreate virtual environment now?", True):
            print("Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("✅ Virtual environment created")
        else:
            print("\n⚠️  You'll need to create it manually later.")
    
    # Step 2: Installation
    print_step(2, "Installation")
    
    if ask_yes_no("Install required packages?", True):
        print("\nInstalling dependencies...")
        print("This may take a few minutes...\n")
        
        if sys.platform == "win32":
            pip_path = "venv\\Scripts\\pip"
        else:
            pip_path = "venv/bin/pip"
        
        try:
            subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
            print("\n✅ All dependencies installed successfully")
        except Exception as e:
            print(f"\n❌ Installation failed: {e}")
            print("\nTry running manually:")
            print(f"  {pip_path} install -r requirements.txt")
    else:
        print("\n⚠️  Skipped installation. You'll need to install manually.")
    
    # Step 3: Configuration
    print_step(3, "Configuration")
    
    if not os.path.exists(".env"):
        print("No .env file found. Creating from template...")
        with open(".env.example", "r") as f:
            content = f.read()
        with open(".env", "w") as f:
            f.write(content)
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")
    
    print("\n⚠️  IMPORTANT: You need to configure your API keys!")
    print("\nEdit the .env file and set:")
    print("  1. API_KEY (for your API authentication)")
    print("  2. OPENAI_API_KEY (if using OpenAI)")
    print("     OR")
    print("     ANTHROPIC_API_KEY (if using Anthropic)")
    
    if ask_yes_no("\nWould you like to configure API keys interactively now?", True):
        print("\nRunning interactive setup...")
        print("\n" + "="*60 + "\n")
        subprocess.run([sys.executable, "setup.py"])
    else:
        print("\n⚠️  Remember to edit .env file manually before running!")
    
    # Final steps
    print("\n")
    print("="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    
    print("\n📚 What to do next:\n")
    
    print("1. Make sure your .env file is configured:")
    print("   • Set your API_KEY")
    print("   • Set your LLM provider API key (OpenAI or Anthropic)\n")
    
    print("2. Start the server:")
    if sys.platform == "win32":
        print("   start.bat")
        print("   OR")
        print("   venv\\Scripts\\activate")
    else:
        print("   ./start.sh")
        print("   OR")
        print("   source venv/bin/activate")
    print("   python main.py\n")
    
    print("3. Test the system:")
    print("   python tests/test_api.py\n")
    
    print("4. Read the documentation:")
    print("   • INDEX.md - Documentation guide")
    print("   • OVERVIEW.md - Visual overview")
    print("   • README.md - Quick start guide\n")
    
    print("="*60)
    print("Need help? Check INDEX.md for documentation guide")
    print("="*60)
    print()
    
    if ask_yes_no("Would you like to start the server now?", False):
        print("\nStarting server...")
        print("Press Ctrl+C to stop\n")
        subprocess.run([sys.executable, "main.py"])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print("\nIf you encounter issues, try running setup.py instead:")
        print("  python setup.py")
        sys.exit(1)
