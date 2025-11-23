@echo off
echo Starting Currency Trading Analysis Platform
echo ==============================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -q -r backend\requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo No .env file found. Copying from .env.example...
    copy .env.example .env
    echo Please edit .env and add your OpenRouter API key for AI features
)

REM Initialize database
echo Initializing database...
cd backend
python -c "from database import init_db; init_db()" 2>nul || echo Database already initialized

REM Start backend
echo.
echo Starting backend server on http://localhost:8000
echo API documentation: http://localhost:8000/docs
echo.
echo To start the frontend, open a new terminal and run:
echo   cd frontend
echo   python -m http.server 8080
echo   Then open http://localhost:8080 in your browser
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
