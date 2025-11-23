#!/bin/bash

echo "🚀 Starting Currency Trading Analysis Platform"
echo "=============================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q -r backend/requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "✏️  Please edit .env and add your OpenRouter API key for AI features"
fi

# Initialize database
echo "🗄️  Initializing database..."
cd backend
python -c "from database import init_db; init_db()" 2>/dev/null || echo "Database already initialized"

# Start backend
echo ""
echo "✅ Starting backend server on http://localhost:8000"
echo "📊 API documentation: http://localhost:8000/docs"
echo ""
echo "To start the frontend, open a new terminal and run:"
echo "  cd frontend && python3 -m http.server 8080"
echo "  Then open http://localhost:8080 in your browser"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
