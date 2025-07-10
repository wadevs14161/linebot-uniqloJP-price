#!/bin/bash

echo "🔄 Cleaning up any existing sessions..."

# Kill any existing ngrok processes
pkill -f ngrok || true

# Stop any running containers
docker-compose down 2>/dev/null || true

echo ""
echo "🐳 Building and starting Docker containers with nginx reverse proxy..."

# Build and start containers
docker-compose up --build -d

# Wait for containers to be fully ready
echo "⏳ Waiting for containers to start..."
sleep 10

echo "✅ Docker containers are running!"
echo "🔗 All services accessible through: http://localhost:8080"

# Test if nginx is responding
if curl -f http://localhost:8080 >/dev/null 2>&1; then
    echo "✅ nginx reverse proxy is working"
else
    echo "❌ nginx reverse proxy is not responding. Check logs:"
    echo "   docker-compose logs nginx"
    exit 1
fi

echo ""
echo "🚀 Starting single ngrok tunnel..."

# Start single ngrok tunnel for nginx (port 8080)
echo "Starting ngrok for nginx reverse proxy (port 8080)..."
ngrok http 8080 &
NGROK_PID=$!

# Wait for ngrok to establish connection
echo "⏳ Waiting for ngrok tunnel to establish..."
sleep 5

echo ""
echo "🎯 Setup complete!"
echo ""
echo "🌐 ngrok tunnel information:"
# Try to get ngrok URL from API
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*"' | head -1 | cut -d'"' -f4)

if [ ! -z "$NGROK_URL" ]; then
    echo "   🔗 Public URL: $NGROK_URL"
    echo ""
    echo "📋 Ready to use:"
    echo "   🌐 Web interface: $NGROK_URL/"
    echo "   🤖 Line Bot webhook: $NGROK_URL/find_product"
    echo "   📡 API endpoint: $NGROK_URL/api/search"
else
    echo "   ℹ️  Check ngrok dashboard or terminal output for the public URL"
fi

echo ""
echo "📋 Next steps:"
echo "1. Copy the ngrok URL above"
echo "2. Update your Line Bot webhook URL to: [ngrok_url]/find_product"
echo "3. Share the same ngrok URL with users for web access"
echo ""
echo "🔧 Architecture:"
echo "   Internet → ngrok → nginx (port 8080) → frontend/backend containers"
echo ""
echo "📊 Monitor services:"
echo "   docker-compose logs -f     # View all logs"
echo "   curl http://localhost:8080 # Test local access"
echo ""
echo "🛑 To stop everything:"
echo "   docker-compose down && kill $NGROK_PID"

# Wait for user interrupt
echo ""
echo "Press Ctrl+C to stop all services..."
wait
