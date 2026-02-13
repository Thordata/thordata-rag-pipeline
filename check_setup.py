"""Check if setup is correct."""
import sys

def check_dependencies():
    """Check if all required dependencies are installed."""
    missing = []
    
    required = [
        ("thordata", "thordata-sdk"),
        ("langchain", "langchain"),
        ("langchain_openai", "langchain-openai"),
        ("langchain_community", "langchain-community"),
        ("chromadb", "chromadb"),
        ("dotenv", "python-dotenv"),
        ("pydantic_settings", "pydantic-settings"),
    ]
    
    for module, package in required:
        try:
            __import__(module)
            print(f"[OK] {package}")
        except ImportError:
            print(f"[MISSING] {package}")
            missing.append(package)
    
    if missing:
        print(f"\n[ERROR] Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("\n[SUCCESS] All dependencies installed!")
    return True

def check_config():
    """Check if configuration is set up."""
    import os
    from pathlib import Path
    
    env_file = Path(".env")
    if not env_file.exists():
        print("[WARN] .env file not found")
        print("Copy .env.example to .env and fill in your credentials")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        "THORDATA_SCRAPER_TOKEN",
        "OPENAI_API_KEY",
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"[WARN] Missing environment variables: {', '.join(missing)}")
        return False
    
    print("[OK] Configuration looks good!")
    return True

if __name__ == "__main__":
    print("Checking Thordata RAG Pipeline setup...\n")
    
    deps_ok = check_dependencies()
    config_ok = check_config()
    
    if deps_ok and config_ok:
        print("\n[SUCCESS] Setup complete! You can now use the pipeline.")
        sys.exit(0)
    else:
        print("\n[ERROR] Setup incomplete. Please fix the issues above.")
        sys.exit(1)
