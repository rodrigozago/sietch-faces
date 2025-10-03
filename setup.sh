#!/bin/bash

echo "🚀 Setting up Sietch Faces API..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Copy .env.example to .env
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p uploads models

# Initialize database
echo "🗄️ Initializing database..."
python3 -m app.database

echo "✅ Setup complete!"
echo ""
echo "To start the API, run:"
echo "  source venv/bin/activate  # or venv\\Scripts\\activate on Windows"
echo "  uvicorn app.main:app --reload"
echo ""
echo "API will be available at: http://localhost:8000"
echo "Documentation at: http://localhost:8000/docs"
