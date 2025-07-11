#!/bin/bash

echo "🔄 Cleaning up any existing sessions..."

# Kill any existing ngrok processes
pkill -f ngrok || true

# Stop any running containers
docker-compose down 2>/dev/null || true

echo ""
echo "🐳 Building and starting UNIQLO Price Finder (Flask + React)..."

# Build and start the unified container
docker-compose up --build -d

# Wait for container to be fully ready
echo "⏳ Waiting for container to start..."
sleep 15

echo "✅ UNIQLO Price Finder is running!"
echo "🔗 Local access: http://localhost:8080"

# Test if the app is responding
if curl -f http://localhost:8080 >/dev/null 2>&1; then
    echo "✅ Application is responding"
else
    echo "❌ Application is not responding. Check logs:"
    echo "   docker-compose logs uniqlo-app"
    exit 1
fi

echo ""
echo "🚀 Starting ngrok tunnel..."

# Start ngrok tunnel for the app (port 8080)
echo "Starting ngrok for UNIQLO Price Finder (port 8080)..."
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
    echo "   🌐 React Web App: $NGROK_URL/"
    echo "   🤖 Line Bot webhook: $NGROK_URL/find_product"
    echo "   📡 API endpoint: $NGROK_URL/api/search"
    echo "   📊 Admin dashboard: $NGROK_URL/admin"
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
echo "   Internet → ngrok → UNIQLO App (Flask + React on port 8080)"
echo ""
echo "📊 Monitor services:"
echo "   docker-compose logs -f uniqlo-app # View app logs"
echo "   curl http://localhost:8080        # Test local access"
echo ""
echo "🛑 To stop everything:"
echo "   docker-compose down && kill $NGROK_PID"

# Wait for user interrupt
echo ""
echo "Press Ctrl+C to stop all services..."
wait
