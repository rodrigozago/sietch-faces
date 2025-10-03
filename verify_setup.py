"""
Verify that the project is set up correctly
"""
import sys
import os

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_directories():
    """Check required directories exist"""
    dirs = ["uploads", "models", "app", "tests"]
    all_exist = True
    for d in dirs:
        if os.path.exists(d):
            print(f"✅ Directory '{d}' exists")
        else:
            print(f"❌ Directory '{d}' missing")
            all_exist = False
    return all_exist

def check_files():
    """Check required files exist"""
    files = [
        "requirements.txt",
        ".env",
        "app/main.py",
        "app/config.py",
        "app/database.py"
    ]
    all_exist = True
    for f in files:
        if os.path.exists(f):
            print(f"✅ File '{f}' exists")
        else:
            print(f"❌ File '{f}' missing")
            all_exist = False
    return all_exist

def check_dependencies():
    """Check if key dependencies are installed"""
    try:
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__}")
    except ImportError:
        print("❌ FastAPI not installed")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn installed")
    except ImportError:
        print("❌ Uvicorn not installed")
        return False
    
    return True

def main():
    print("🔍 Verifying Sietch Faces setup...\n")
    
    checks = [
        ("Python Version", check_python_version()),
        ("Directories", check_directories()),
        ("Files", check_files()),
        ("Dependencies", check_dependencies())
    ]
    
    print("\n" + "="*50)
    all_passed = all(result for _, result in checks)
    
    if all_passed:
        print("✅ All checks passed!")
        print("\nTo start the API, run:")
        print("  uvicorn app.main:app --reload")
        print("\nThen visit: http://localhost:8000/docs")
    else:
        print("❌ Some checks failed!")
        print("\nPlease run the setup script:")
        print("  Windows: setup.bat")
        print("  Linux/Mac: ./setup.sh")
    
    print("="*50)
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
