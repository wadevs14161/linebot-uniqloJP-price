#!/bin/bash

# Comprehensive test script
# Tests all functionality of the UNIQLO price finder application

echo "🧪 UNIQLO Japan Price Finder - Test Suite"
echo "=========================================="
echo ""

# Function to check if a service is running
check_service() {
    local url=$1
    local name=$2
    
    if curl -s "$url" > /dev/null 2>&1; then
        echo "✅ $name is running"
        return 0
    else
        echo "❌ $name is not responding"
        return 1
    fi
}

# Function to run API tests
run_api_tests() {
    echo "🔧 Running API tests..."
    ./scripts/testing/test-sqlite-integration.sh
}

echo "1️⃣ Checking service availability..."
echo ""

# Check backend
check_service "http://localhost:5000" "Backend (Flask)"
backend_status=$?

# Check frontend
check_service "http://localhost:5173" "Frontend (React)"
frontend_status=$?

# Check nginx (if running)
check_service "http://localhost:8080" "Nginx Reverse Proxy"
nginx_status=$?

echo ""
echo "2️⃣ Service Status Summary:"
echo ""

if [ $backend_status -eq 0 ]; then
    echo "📡 Backend: ✅ Running on http://localhost:5000"
else
    echo "📡 Backend: ❌ Not running (start with: python app.py)"
fi

if [ $frontend_status -eq 0 ]; then
    echo "🌐 Frontend: ✅ Running on http://localhost:5173"
else
    echo "🌐 Frontend: ❌ Not running (start with: cd frontend && npm run dev)"
fi

if [ $nginx_status -eq 0 ]; then
    echo "🔄 Nginx: ✅ Running on http://localhost:8080"
else
    echo "🔄 Nginx: ❌ Not running (start with: docker-compose up)"
fi

echo ""

# Run API tests if backend is available
if [ $backend_status -eq 0 ]; then
    echo "3️⃣ Running comprehensive tests..."
    echo ""
    run_api_tests
else
    echo "3️⃣ Skipping API tests (backend not available)"
    echo "   To run tests, start the backend first:"
    echo "   $ python app.py"
    echo "   Then run: $ ./test.sh"
fi

echo ""
echo "4️⃣ Manual testing checklist:"
echo ""
echo "Web Interface (http://localhost:5173 or http://localhost:8080):"
echo "   □ Search for product ID: 474479"
echo "   □ Verify search history appears"
echo "   □ Test clear history button"
echo "   □ Refresh page to verify persistence"
echo ""
echo "API Endpoints:"
echo "   □ POST /api/search - Product search"
echo "   □ GET /api/history - Get search history"
echo "   □ DELETE /api/history - Clear history"
echo ""
echo "Database:"
echo "   □ Check data/search_history.db exists"
echo "   □ Verify user sessions work across requests"
echo ""
echo "🎉 Test suite completed!"
