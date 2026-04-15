#!/bin/bash
# IKMC Math Practice App - Startup Script

echo "🦘 Starting IKMC Math Practice App..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python3."
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js (v18+)."
    exit 1
fi

# Install backend deps
echo "📦 Installing Python dependencies..."
cd backend
pip3 install -r requirements.txt -q
echo "✅ Backend dependencies ready"

# Start Flask backend
echo "🚀 Starting Flask backend on http://localhost:5000 ..."
python3 app.py &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 2

# Install & start frontend
echo ""
echo "📦 Installing Node dependencies..."
cd ../frontend
npm install --silent
echo "✅ Frontend dependencies ready"

echo "🚀 Starting React frontend on http://localhost:3000 ..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "======================================"
echo "🦘 IKMC Math Practice is running!"
echo "======================================"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both servers."
echo ""

# Cleanup on exit
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

wait
