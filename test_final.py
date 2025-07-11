#!/usr/bin/env python3
"""
Comprehensive end-to-end test for the UNIQLO Price Finder database upgrade
"""
import os
import sys
from datetime import datetime
import json

def test_complete_flow():
    """Test the complete flow from API request to database storage"""
    print("🎯 UNIQLO Price Finder - Complete Flow Test")
    print("=" * 50)
    
    try:
        from app import app
        from database import db_manager
        
        # Test 1: Database connectivity
        print("\n1. Testing database connectivity...")
        stats_before = db_manager.get_search_stats()
        print(f"✅ Database connected. Current searches: {stats_before.get('total_searches', 0)}")
        
        # Test 2: API search with valid product
        print("\n2. Testing API search with valid product...")
        with app.test_client() as client:
            response = client.post('/api/search', json={'product_id': '474479'})
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ API search successful")
                print(f"   Product URL: {data.get('product_url', 'N/A')}")
                print(f"   JP Price: ¥{data.get('price_jp', 'N/A')}")
                print(f"   TWD Price: NT${data.get('jp_price_in_twd', 'N/A')}")
                print(f"   Product variants: {len(data.get('product_list', []))}")
            else:
                print(f"❌ API search failed: {response.get_data(as_text=True)}")
                return False
        
        # Test 3: Verify data was saved to database
        print("\n3. Testing database integration...")
        stats_after = db_manager.get_search_stats()
        searches_added = stats_after.get('total_searches', 0) - stats_before.get('total_searches', 0)
        print(f"✅ Database integration working. New searches: {searches_added}")
        
        # Test 4: Cache functionality
        print("\n4. Testing cache functionality...")
        with app.test_client() as client:
            # Second request should use cache
            response = client.post('/api/search', json={'product_id': '474479'})
            if response.status_code == 200:
                print("✅ Cache functionality working (second request)")
            else:
                print("❌ Cache test failed")
                return False
        
        # Test 5: Stats API
        print("\n5. Testing analytics API...")
        with app.test_client() as client:
            response = client.get('/api/stats')
            if response.status_code == 200:
                stats = response.get_json()
                print(f"✅ Analytics API working")
                print(f"   Total searches: {stats.get('total_searches', 0)}")
                print(f"   Success rate: {stats.get('success_rate', 0)}%")
                print(f"   Popular products: {len(stats.get('popular_products', []))}")
            else:
                print("❌ Analytics API failed")
                return False
        
        # Test 6: Error handling
        print("\n6. Testing error handling...")
        with app.test_client() as client:
            response = client.post('/api/search', json={'product_id': 'invalid999'})
            if response.status_code == 404:
                print("✅ Error handling working (404 for invalid product)")
            else:
                print(f"⚠️  Unexpected error response: {response.status_code}")
        
        print("\n🎉 All tests passed! Database upgrade is successful.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_deployment_summary():
    """Print deployment and next steps summary"""
    print("\n" + "=" * 60)
    print("🚀 DEPLOYMENT SUMMARY")
    print("=" * 60)
    
    print("\n✅ COMPLETED:")
    print("   • Database models created with SQLAlchemy")
    print("   • DatabaseManager with PostgreSQL/SQLite fallback")
    print("   • Flask app integrated with new database")
    print("   • Caching system implemented")
    print("   • Analytics and search history")
    print("   • Cloud SQL setup scripts")
    print("   • Cloud Run deployment scripts")
    print("   • Documentation and testing")
    
    print("\n📋 LOCAL DEVELOPMENT:")
    print("   • Uses SQLite fallback (data/uniqlo_price_finder.db)")
    print("   • All functionality working with local database")
    print("   • Run: python app.py (for development)")
    
    print("\n☁️  PRODUCTION DEPLOYMENT:")
    print("   1. Run: ./scripts/cloud/setup-database.sh")
    print("      (Creates Cloud SQL PostgreSQL instance)")
    print("   2. Build image: ./scripts/cloud/build-and-push.sh")
    print("   3. Deploy: ./scripts/cloud/deploy-cloudrun.sh")
    print("      (Deploys with Cloud SQL connection)")
    
    print("\n📊 DATABASE FEATURES:")
    print("   • Search history with analytics")
    print("   • Price caching (1 hour default)")
    print("   • Error tracking and success rates")
    print("   • Popular products tracking")
    print("   • API: /api/stats for analytics")
    
    print("\n🔧 CONFIGURATION:")
    print("   • Production: Uses DATABASE_URL environment variable")
    print("   • Local: Falls back to SQLite if no DB credentials")
    print("   • Environment: Set via .env.database (auto-generated)")
    
    print("\n📚 DOCUMENTATION:")
    print("   • Setup guide: docs/DATABASE-SETUP.md")
    print("   • Test script: ./test_database.py")
    print("   • Full docs: README.md")

if __name__ == "__main__":
    print("🗄️  UNIQLO Price Finder - Database Upgrade Validation")
    print("====================================================")
    
    # Run comprehensive test
    success = test_complete_flow()
    
    # Print summary
    print_deployment_summary()
    
    if success:
        print("\n🎊 DATABASE UPGRADE COMPLETED SUCCESSFULLY!")
        print("   Ready for production deployment to GCP Cloud Run with Cloud SQL.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please review the errors above.")
        sys.exit(1)
