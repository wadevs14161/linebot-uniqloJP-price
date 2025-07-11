#!/bin/bash

# Script to build and deploy the React frontend

set -e

echo "🛠️  Building React Frontend"
echo "============================"

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

echo "📦 Installing dependencies..."
npm install

echo "🏗️  Building production bundle..."
npm run build

echo "📁 Copying build files to static directory..."
# Remove old frontend files
rm -rf ../static/frontend

# Copy new build files
cp -r dist ../static/frontend

# Copy the UNIQLO icon to the frontend directory
cp ../static/images/uniqlo-jp-icon.png ../static/frontend/

echo "✅ Frontend build complete!"
echo ""
echo "🌐 Frontend is now available at:"
echo "   Local: http://localhost:5000/frontend"
echo "   Flask route: /frontend"
echo ""
echo "💡 To test locally:"
echo "   1. Start Flask app: python app.py"
echo "   2. Open browser: http://localhost:5000/frontend"
