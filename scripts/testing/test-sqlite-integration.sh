#!/bin/bash

# SQLite3 Integration Test Script
# This script tests the new search history functionality

echo "🧪 Testing SQLite3 Search History Integration"
echo "============================================="

API_BASE="http://localhost:5000"
COOKIE_FILE="test_cookies.txt"

echo ""
echo "1. Testing product search (474479)..."
SEARCH_RESULT=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"product_id": "474479"}' \
  -c "$COOKIE_FILE" \
  "$API_BASE/api/search")

if echo "$SEARCH_RESULT" | grep -q "product_url"; then
    echo "✅ Search successful!"
    echo "📄 Product URL: $(echo "$SEARCH_RESULT" | grep -o '"product_url":"[^"]*"' | cut -d'"' -f4)"
    echo "💰 Price: $(echo "$SEARCH_RESULT" | grep -o '"price_jp":[0-9]*' | cut -d':' -f2)"
else
    echo "❌ Search failed!"
    echo "$SEARCH_RESULT"
fi

echo ""
echo "2. Testing another product search (467536)..."
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"product_id": "467536"}' \
  -b "$COOKIE_FILE" -c "$COOKIE_FILE" \
  "$API_BASE/api/search" > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ Second search successful!"
else
    echo "❌ Second search failed!"
fi

echo ""
echo "3. Testing search history retrieval..."
HISTORY_RESULT=$(curl -s -b "$COOKIE_FILE" "$API_BASE/api/history")

if echo "$HISTORY_RESULT" | grep -q "history"; then
    echo "✅ History retrieval successful!"
    HISTORY_COUNT=$(echo "$HISTORY_RESULT" | grep -o '"product_id"' | wc -l)
    echo "📊 Found $HISTORY_COUNT search entries"
    
    echo ""
    echo "📝 Recent searches:"
    echo "$HISTORY_RESULT" | grep -o '"product_id":"[^"]*"' | head -3 | while read -r line; do
        PRODUCT_ID=$(echo "$line" | cut -d'"' -f4)
        echo "   - Product ID: $PRODUCT_ID"
    done
else
    echo "❌ History retrieval failed!"
    echo "$HISTORY_RESULT"
fi

echo ""
echo "4. Testing clear history..."
CLEAR_RESULT=$(curl -s -X DELETE -b "$COOKIE_FILE" "$API_BASE/api/history")

if echo "$CLEAR_RESULT" | grep -q "cleared successfully"; then
    echo "✅ History cleared successfully!"
else
    echo "❌ Clear history failed!"
    echo "$CLEAR_RESULT"
fi

echo ""
echo "5. Verifying history is empty..."
EMPTY_HISTORY=$(curl -s -b "$COOKIE_FILE" "$API_BASE/api/history")

if echo "$EMPTY_HISTORY" | grep -q '"history":\[\]'; then
    echo "✅ History is now empty!"
else
    echo "❓ History might not be empty:"
    echo "$EMPTY_HISTORY"
fi

echo ""
echo "🧹 Cleaning up test files..."
rm -f "$COOKIE_FILE"

echo ""
echo "🎉 SQLite3 integration test completed!"
echo ""
echo "To test the frontend:"
echo "1. Open http://localhost:5173 in your browser"
echo "2. Search for products (e.g., 474479, 467536)"
echo "3. Check that history appears in the table"
echo "4. Test the 'Clear History' button"
echo "5. Refresh the page to verify persistence"
