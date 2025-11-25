#!/bin/bash

echo "========================================"
echo "  GR-X BLINDSPOT COMMAND - HACKATHON"
echo "  AI Driver Coaching Platform"
echo "========================================"
echo ""

echo "[1/4] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found! Please install Python 3.8+"
    exit 1
fi

echo "[2/4] Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found! Please install Node.js 16+"
    exit 1
fi

echo "[3/4] Starting Backend Server..."
cd backend
pip install -r requirements.txt > /dev/null 2>&1
echo "Backend dependencies installed!"
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

sleep 5

echo "[4/4] Starting Frontend Server..."
cd frontend
npm install > /dev/null 2>&1
echo "Frontend dependencies installed!"
PORT=3001 npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "  SERVERS RUNNING!"
echo "========================================"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3001"
echo "  API Docs: http://localhost:8000/docs"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop all servers..."

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
