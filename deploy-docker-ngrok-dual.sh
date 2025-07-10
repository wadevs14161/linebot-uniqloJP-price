# Docker + dual ngrok deployment script (for users with multiple ngrok tunnels)
#!/bin/bash

echo "🐳 Building and starting Docker containers (development mode)..."

# Build and start containers with individual ports
docker-compose -f docker-compose.dev.yml up --build -d

echo "✅ Docker containers are running!"
echo "📡 Backend: http://localhost:5000"
echo "🌐 Frontend: http://localhost:3000"

echo ""
echo "🚀 Starting dual ngrok tunnels..."

# Start ngrok for backend (Line Bot webhook)
echo "Starting ngrok for backend (port 5000)..."
ngrok http 5000 --log=stdout > /tmp/ngrok-backend.log 2>&1 &
NGROK_BACKEND_PID=$!

# Wait a moment for backend ngrok to start
sleep 3

# Start ngrok for frontend (public access)
echo "Starting ngrok for frontend (port 3000)..."
ngrok http 3000 --log=stdout > /tmp/ngrok-frontend.log 2>&1 &
NGROK_FRONTEND_PID=$!

# Wait for ngrok tunnels to establish
sleep 5

echo ""
echo "🎯 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Check ngrok URLs:"
echo "   - Backend ngrok URL (for Line Bot webhook):"
curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*"' | head -1 | cut -d'"' -f4
echo "   - Frontend ngrok URL (for users):"
curl -s http://localhost:4041/api/tunnels | grep -o '"public_url":"[^"]*"' | head -1 | cut -d'"' -f4

echo ""
echo "2. Update your Line Bot webhook URL with: [backend_ngrok_url]/find_product"
echo "3. Share the frontend ngrok URL with users"
echo ""
echo "To stop everything:"
echo "  docker-compose -f docker-compose.dev.yml down"
echo "  kill $NGROK_BACKEND_PID $NGROK_FRONTEND_PID"

# Wait for user interrupt
wait
