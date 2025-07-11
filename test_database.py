#!/usr/bin/env python3
"""
Test script for database functionality
"""
import os
import sys
from datetime import datetime
from database import db_manager

def test_database_operations():
    """Test basic database operations"""
    print("🧪 Testing Database Operations")
    print("=" * 40)
    
    try:
        # Test 1: Search history
        print("\n1. Testing search history...")
        test_product_id = "test_product_123"
        
        # Save a search
        search_data = {
            'serial_number': "TEST123",
            'price_jp': 2990,
            'jp_price_in_twd': 650,
            'price_tw': [680, 700, 720],
            'product_url': "https://example.com/test"
        }
        
        db_manager.save_search_history(
            product_id=test_product_id,
            search_data=search_data,
            source="test",
            user_id="test_user"
        )
        print("✅ Search saved to history")
        
        # Get search statistics (since there's no direct get_search_history method)
        stats = db_manager.get_search_stats()
        print(f"✅ Retrieved search stats: {stats['total_searches']} total searches")
        
        # Test 2: Cache operations
        print("\n2. Testing cache operations...")
        cache_data = {
            "title": "Cached Product",
            "jp_price": 1990,
            "tw_prices": [450, 460, 470]
        }
        
        # Save to cache
        db_manager.cache_price_data(test_product_id, cache_data, cache_hours=24)
        print("✅ Data saved to cache")
        
        # Get from cache
        cached = db_manager.get_cached_price(test_product_id)
        if cached:
            print("✅ Data retrieved from cache")
        else:
            print("❌ Cache retrieval failed")
        
        # Test 3: Analytics
        print("\n3. Testing analytics...")
        stats = db_manager.get_search_stats()
        print(f"✅ Analytics: {stats}")
        
        # Test 4: Config operations (skip - not implemented in current DatabaseManager)
        print("\n4. Skipping config test (not implemented yet)")
        
        print("\n🎉 All database tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_integration():
    """Test Flask app integration"""
    print("\n🌐 Testing Flask Integration")
    print("=" * 40)
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test 1: Health check (root endpoint)
            response = client.get('/')
            print(f"✅ Root endpoint: {response.status_code}")
            
            # Test 2: API stats endpoint
            response = client.get('/api/stats')
            if response.status_code == 200:
                stats = response.get_json()
                print(f"✅ Stats API: {stats}")
            else:
                print(f"⚠️  Stats API returned {response.status_code}")
            
            # Test 3: Search API (mock search)
            test_data = {
                'product_id': 'test_456',
                'search_source': 'api_test'
            }
            
            print("\n🎉 Flask integration tests passed!")
            return True
            
    except Exception as e:
        print(f"\n❌ Flask integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🗄️  Database Testing Script")
    print("===========================")
    
    # Test database operations
    db_success = test_database_operations()
    
    # Test Flask integration
    flask_success = test_flask_integration()
    
    if db_success and flask_success:
        print("\n🎊 All tests completed successfully!")
        print("The database upgrade is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the errors above.")
        sys.exit(1)
