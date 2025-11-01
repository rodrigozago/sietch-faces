#!/usr/bin/env python3
"""
Documentation generation script for Sietch Faces API.

This script uses pdoc3 to generate HTML documentation from docstrings
in the codebase. The generated documentation is saved to the docs/ directory.

Prerequisites:
    pip install -r requirements.txt
    pip install -r requirements-dev.txt

Usage:
    python generate_docs.py

Output:
    HTML documentation in ./docs/ directory
"""
import subprocess
import sys
import os
from pathlib import Path


def check_dependencies():
    """
    Check if required dependencies are installed.
    
    Returns:
        bool: True if all dependencies are available, False otherwise.
    """
    try:
        import pdoc
        return True
    except ImportError:
        print("\n❌ Error: pdoc3 not installed.")
        print("   Install it with: pip install -r requirements-dev.txt")
        return False


def generate_documentation():
    """
    Generate HTML documentation using pdoc3.
    
    Generates comprehensive API documentation from docstrings in the app module.
    The documentation is saved to the docs/ directory and includes:
    - Module documentation
    - Class documentation
    - Function/method documentation
    - Type hints and signatures
    
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    print("=" * 60)
    print("📚 Generating API Documentation")
    print("=" * 60)
    
    if not check_dependencies():
        return 1
    
    # Ensure docs directory exists
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    print(f"📁 Output directory: {docs_dir.absolute()}")
    
    # Generate documentation using pdoc3 for the entire app module
    print(f"\n📝 Documenting app module...")
    
    try:
        # Run pdoc3 to generate HTML documentation for entire app module
        cmd = [
            sys.executable, "-m", "pdoc",
            "--html",
            "--output-dir", str(docs_dir),
            "--force",
            "app"  # Document entire app module
        ]
        
        print(f"\n🔧 Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"\n❌ Error generating documentation:")
            print(result.stderr)
            print("\nNote: Make sure all dependencies are installed:")
            print("  pip install -r requirements.txt")
            print("  pip install -r requirements-dev.txt")
            return result.returncode
        
        print(f"\n✅ Documentation generated successfully!")
        
        # Create an index.html that redirects to app module
        index_path = docs_dir / "index.html"
        with open(index_path, "w") as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="0; url=app/index.html">
    <title>Sietch Faces API Documentation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            max-width: 800px;
            margin: 100px auto;
            padding: 20px;
            text-align: center;
        }
        h1 { color: #333; }
        a { color: #0066cc; }
    </style>
</head>
<body>
    <h1>📚 Sietch Faces API Documentation</h1>
    <p>Redirecting to <a href="app/index.html">API documentation</a>...</p>
    <p><small>If not redirected automatically, click the link above.</small></p>
</body>
</html>
""")
        
        print(f"\n📋 Documentation index created")
        print(f"\n🌐 View documentation:")
        print(f"   file://{index_path.absolute()}")
        print(f"\n💡 Tip: You can also serve the docs with:")
        print(f"   python -m http.server --directory docs 8080")
        print(f"   Then open: http://localhost:8080")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(generate_documentation())
