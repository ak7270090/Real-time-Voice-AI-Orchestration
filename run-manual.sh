#!/bin/bash

# Manual Run Script (without Docker)

echo "========================================"
echo "Voice AI Agent - Manual Setup"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

echo "Python and Node.js found"
echo ""

# Check .env
if [ ! -f .env ]; then
    echo "No .env file found. Please run setup.sh first"
    exit 1
fi

echo "Starting services..."
echo ""

# Start backend in background
echo "Starting backend..."
cd backend

# Create venv if doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# Create necessary directories
mkdir -p uploads chroma_db

# Start backend
echo "Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "Backend running (PID: $BACKEND_PID)"

# Start voice agent
echo ""
echo "Starting LiveKit voice agent..."
python3 voice_agent.py dev &
AGENT_PID=$!
echo "Voice agent running (PID: $AGENT_PID)"

cd ..

# Start frontend in background
echo ""
echo "Starting frontend..."
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

# Start frontend
echo "Starting React development server..."
BROWSER=none npm start &
FRONTEND_PID=$!
echo "Frontend running (PID: $FRONTEND_PID)"

cd ..

echo ""
echo "========================================"
echo "Services Started!"
echo "========================================"
echo ""
echo "Frontend:    http://localhost:3000"
echo "Backend:     http://localhost:8000"
echo "API Docs:    http://localhost:8000/docs"
echo "Voice Agent: running (LiveKit worker)"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $AGENT_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait
wait
