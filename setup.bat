@echo off
echo 🚀 Setting up Sietch Faces API...

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo ✅ Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Copy .env.example to .env
if not exist ".env" (
    echo 📝 Creating .env file...
    copy .env.example .env
)

REM Create directories
echo 📁 Creating directories...
if not exist "uploads" mkdir uploads
if not exist "models" mkdir models

REM Initialize database
echo 🗄️ Initializing database...
python -m app.database

echo ✅ Setup complete!
echo.
echo To start the API, run:
echo   venv\Scripts\activate
echo   uvicorn app.main:app --reload
echo.
echo API will be available at: http://localhost:8000
echo Documentation at: http://localhost:8000/docs

pause
