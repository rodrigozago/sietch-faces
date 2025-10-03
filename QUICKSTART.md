# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional)

## Installation Steps

### Windows

1. **Clone or download the project**
   ```bash
   cd c:\PersonalWorkspace\sietch-faces
   ```

2. **Run the setup script**
   ```bash
   setup.bat
   ```

3. **Activate the virtual environment**
   ```bash
   venv\Scripts\activate
   ```

4. **Start the API**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

### Linux/Mac

1. **Clone or download the project**
   ```bash
   cd ~/projects/sietch-faces
   ```

2. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Activate the virtual environment**
   ```bash
   source venv/bin/activate
   ```

4. **Start the API**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs

## Manual Installation

If the setup scripts don't work, follow these steps:

1. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Create .env file**
   ```bash
   cp .env.example .env
   ```

5. **Create directories**
   ```bash
   mkdir uploads models
   ```

6. **Initialize database**
   ```bash
   python -m app.database
   ```

7. **Start the API**
   ```bash
   uvicorn app.main:app --reload
   ```

## First Steps

### 1. Upload Your First Image

Open http://localhost:8000/docs and:

1. Go to the **POST /upload** endpoint
2. Click "Try it out"
3. Upload an image with faces
4. Click "Execute"
5. See the detected faces in the response

### 2. Identify a Face

1. Copy a `face_id` from the upload response
2. Go to **POST /identify**
3. Enter:
   ```json
   {
     "face_id": 1,
     "name": "John Doe",
     "auto_identify_similar": true
   }
   ```
4. The system will automatically identify similar faces

### 3. View Clusters

1. Go to **GET /clusters**
2. See groups of similar faces
3. This helps identify people who haven't been named yet

### 4. Get Statistics

1. Go to **GET /stats**
2. See overall statistics about your face database

## Troubleshooting

### Import Errors

If you get import errors, make sure:
- Virtual environment is activated
- All dependencies are installed: `pip install -r requirements.txt`

### Database Errors

If you get database errors:
```bash
python -m app.database
```

### Face Detection Not Working

The first time you run face detection, the models will be downloaded automatically. This may take a few minutes.

### Port Already in Use

If port 8000 is already in use:
```bash
uvicorn app.main:app --reload --port 8001
```

## Configuration

Edit the `.env` file to customize:

- `DATABASE_URL` - Database connection string
- `SIMILARITY_THRESHOLD` - How similar faces need to be (0.0-1.0)
- `CONFIDENCE_THRESHOLD` - Minimum confidence for face detection
- `DBSCAN_EPS` - Clustering sensitivity

## Next Steps

- Check [API_EXAMPLES.md](API_EXAMPLES.md) for more usage examples
- Read the full [README.md](README.md) for architecture details
- Explore the interactive API docs at http://localhost:8000/docs

## Running Tests

```bash
pip install pytest
pytest tests/
```

## Production Deployment

For production, use a proper ASGI server and database:

```bash
# Install production dependencies
pip install gunicorn

# Use PostgreSQL
# Update .env with: DATABASE_URL=postgresql://user:pass@localhost/dbname

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
