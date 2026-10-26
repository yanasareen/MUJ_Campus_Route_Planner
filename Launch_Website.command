#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "==========================================================="
echo "  🚀 MUJ Campus Route Planner (Manipal University Jaipur)"
echo "==========================================================="

# Check if port 5001 is already running
if curl -s http://127.0.0.1:5001/api/health | grep -q "healthy"; then
    echo "✅ Website server is already running!"
else
    echo "🌐 Starting server on port 5001..."
    nohup python3 app.py > server.log 2>&1 &
    sleep 2
fi

# Open directly in default web browser
open "http://127.0.0.1:5001"

echo "✨ Website opened in your browser: http://127.0.0.1:5001"
echo "📱 To open on your mobile or another computer on the same Wi-Fi:"
echo "   http://10.68.4.41:5001"
echo "==========================================================="
