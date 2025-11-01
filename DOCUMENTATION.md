# API Documentation Guide

This document explains how to generate and view API documentation for Sietch Faces.

## Quick Start

### Generate Documentation

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Generate HTML documentation
python generate_docs.py
```

### View Documentation

After generating, you can view the documentation in several ways:

**Option 1: Open directly in browser**
```bash
# Open the docs/index.html file in your browser
open docs/index.html  # macOS
xdg-open docs/index.html  # Linux
start docs/index.html  # Windows
```

**Option 2: Serve with Python**
```bash
# Start a local web server
python -m http.server --directory docs 8080

# Then open in browser:
# http://localhost:8080
```

## Documentation Features

The generated documentation includes:

- **Module Documentation**: Overview and purpose of each module
- **Class Documentation**: Detailed information about classes, attributes, and methods
- **Function Documentation**: Complete function signatures, parameters, return types, and examples
- **Type Hints**: Full type information for better understanding
- **Source Code Links**: Direct links to source code for each item

## Interactive API Documentation

When the API is running, you can access interactive documentation:

### Swagger UI
```
http://localhost:8000/docs
```
- Interactive API testing
- Try out endpoints directly
- View request/response schemas
- See authentication requirements

### ReDoc
```
http://localhost:8000/redoc
```
- Alternative documentation interface
- Clean, organized presentation
- Better for reading and reference
- Printable format

## Documentation Structure

```
docs/
├── index.html              # Main entry point
└── app/
    ├── index.html          # App module overview
    ├── main.html           # Main API documentation
    ├── main_core.html      # Core API documentation
    ├── face_detection.html # Face detection module
    ├── face_recognition.html # Face recognition module
    ├── clustering.html     # Clustering module
    ├── services/           # Service modules
    │   ├── face_matching.html
    │   ├── claim_service.html
    │   └── api_key_service.html
    └── routes/             # API route modules
        ├── core.html
        ├── internal.html
        ├── upload.html
        ├── identify.html
        ├── person.html
        ├── stats.html
        └── clusters.html
```

## Best Practices

### For Developers

When adding new code, follow these documentation practices:

1. **Module Docstrings**: Start each file with a module-level docstring
   ```python
   """
   Brief description of the module.
   
   Detailed explanation of what this module does and how to use it.
   """
   ```

2. **Class Docstrings**: Document classes with purpose, attributes, and examples
   ```python
   class MyClass:
       """
       Brief description.
       
       Detailed explanation.
       
       Attributes:
           attr1 (type): Description.
           attr2 (type): Description.
           
       Example:
           >>> obj = MyClass()
           >>> obj.method()
       """
   ```

3. **Function Docstrings**: Use comprehensive docstrings
   ```python
   def my_function(param1: str, param2: int) -> bool:
       """
       Brief description.
       
       Detailed explanation.
       
       Args:
           param1 (str): Description of param1.
           param2 (int): Description of param2.
           
       Returns:
           bool: Description of return value.
           
       Raises:
           ValueError: When param1 is invalid.
           
       Example:
           >>> result = my_function("test", 42)
           >>> print(result)
       """
   ```

4. **Type Hints**: Always include type hints for parameters and return values

### Regenerating Documentation

Regenerate documentation after:
- Adding new modules or functions
- Updating docstrings
- Changing function signatures
- Before releases

```bash
python generate_docs.py
```

## Troubleshooting

### Import Errors

If you get import errors when generating docs:
```bash
# Make sure all dependencies are installed
pip install -r requirements.txt
pip install -r requirements-dev.txt

# If you're in a virtual environment, activate it first
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### Missing Modules

If certain modules aren't documented:
- Check that they have proper `__init__.py` files
- Ensure they can be imported without errors
- Verify all dependencies are installed

### Formatting Issues

If documentation looks incorrect:
- Check docstring formatting (use Google or NumPy style)
- Ensure proper indentation in docstrings
- Validate type hints are correct

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **pdoc3 Documentation**: https://pdoc3.github.io/pdoc/
- **Python Docstring Conventions**: PEP 257
- **Type Hints**: PEP 484

## Maintaining Documentation

Documentation should be:
- **Accurate**: Keep it in sync with code
- **Complete**: Cover all public APIs
- **Clear**: Write for your future self and others
- **Updated**: Regenerate regularly
- **Versioned**: Tag documentation with releases
