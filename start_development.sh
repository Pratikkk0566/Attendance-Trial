#!/bin/bash

echo "🚀 Starting Attendance App Development Environment..."
echo

# Check if Python virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "❌ Python virtual environment not found!"
    echo "Please run: cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if Node modules exist
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Node modules not found!"
    echo "Please run: cd frontend && npm install"
    exit 1
fi

echo "[1/3] Starting Backend Server..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!

echo "[2/3] Starting Frontend Server..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "[3/3] Waiting for servers to start..."
sleep 5

echo
echo "✅ Development environment started!"
echo
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo
echo "Press Ctrl+C to stop all servers..."

# Wait for user interrupt
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait