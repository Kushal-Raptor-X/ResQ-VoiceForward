#!/bin/bash

# VoiceForward Startup Script
# This script starts all components of the VoiceForward application

echo "🚀 Starting VoiceForward Application..."
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "📦 Installing Backend Dependencies..."
cd backend
$PYTHON_CMD -m pip install -r requirements.txt --quiet
cd ..

echo "📦 Installing Real-Time Backend Dependencies..."
cd realtime_backend
$PYTHON_CMD -m pip install -r requirements.txt --quiet
cd ..

echo "📦 Installing Frontend Dependencies..."
cd frontend
npm install --silent
cd ..

echo ""
echo "✅ All dependencies installed!"
echo ""
echo "🎯 Starting services..."
echo ""

# Start backend in background
echo "🔧 Starting Main Backend (port 8000)..."
cd backend
$PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Start real-time backend in background
echo "🔧 Starting Real-Time Backend (port 8001)..."
cd realtime_backend
$PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8001 &
REALTIME_PID=$!
cd ..

# Wait a bit for real-time backend to start
sleep 3

# Start frontend
echo "🎨 Starting Frontend (port 5173)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ All services started!"
echo ""
echo "📍 Access points:"
echo "   Frontend:         http://localhost:5173"
echo "   Main Backend:     http://localhost:8000"
echo "   Real-Time Backend: http://localhost:8001"
echo ""
echo "🔍 Health checks:"
echo "   Main Backend:     http://localhost:8000/health"
echo "   Real-Time Backend: http://localhost:8001/health"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $BACKEND_PID 2>/dev/null
    kill $REALTIME_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped."
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for all background processes
wait
