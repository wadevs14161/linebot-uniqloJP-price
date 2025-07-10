# Docker + ngrok deployment script (Single ngrok tunnel)
#!/bin/bash

echo "🐳 Building and starting Docker containers with nginx reverse proxy..."

# Build and start containers
docker-compose up --build -d

echo "✅ Docker containers are running!"
echo "� All services accessible through: http://localhost:8080"
echo "   �📡 Backend API: http://localhost:8080/api/"
echo "   🌐 Frontend: http://localhost:8080/"
echo "   🤖 Line Bot webhook: http://localhost:8080/find_product"

echo ""
echo "🚀 Starting single ngrok tunnel..."

# Start single ngrok tunnel for nginx (port 8080)
echo "Starting ngrok for nginx reverse proxy (port 8080)..."
ngrok http 8080 --log=stdout &
NGROK_PID=$!

echo ""
echo "🎯 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Copy the ngrok URL above (e.g., https://abc123.ngrok.io)"
echo "2. Update your Line Bot webhook URL to: [ngrok_url]/find_product"
echo "3. Share the same ngrok URL with users for web access"
echo "4. Users can access:"
echo "   - Web interface: [ngrok_url]/"
echo "   - API directly: [ngrok_url]/api/search"
echo ""
echo "🔧 Architecture:"
echo "   Internet → ngrok → nginx (port 8080) → frontend/backend containers"
echo ""
echo "To stop everything:"
echo "  docker-compose down"
echo "  kill $NGROK_PID"

# Wait for user interrupt
wait
