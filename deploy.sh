#!/bin/bash

# Main deployment script
# This script provides a simple interface to deploy the application

echo "🚀 UNIQLO Japan Price Finder - Deployment Script"
echo "================================================="
echo ""
echo "Please choose your deployment method:"
echo "1) Single ngrok tunnel (Recommended - all services through nginx)"
echo "2) Dual ngrok tunnels (Separate tunnels for backend and frontend)"
echo "3) Local development only (no ngrok)"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "🌟 Starting single ngrok tunnel deployment..."
        ./scripts/deployment/deploy-docker-ngrok.sh
        ;;
    2)
        echo "🌟 Starting dual ngrok tunnel deployment..."
        ./scripts/deployment/deploy-docker-ngrok-dual.sh
        ;;
    3)
        echo "🌟 Starting local development deployment..."
        echo "🐳 Building and starting Docker containers..."
        docker-compose -f docker/docker-compose.yml up --build -d
        echo "✅ Local deployment complete!"
        echo "🌐 Frontend: http://localhost:8080"
        echo "📡 Backend API: http://localhost:8080/api/"
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again and choose 1, 2, or 3."
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📚 For more information:"
echo "   - Main documentation: README.md"
echo "   - Deployment guide: docs/DEPLOYMENT.md"
echo "   - SQLite integration: docs/SQLITE-INTEGRATION.md"
