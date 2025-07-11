#!/usr/bin/env python3
"""
PostgreSQL Migration Verification Test
This script demonstrates that the application is now using PostgreSQL instead of SQLite
"""
import os
import sys
from datetime import datetime
from database import db_manager

def test_postgresql_features():
    """Test PostgreSQL-specific features that aren't available in SQLite"""
    print("🗄️  PostgreSQL Migration Verification")
    print("=" * 40)
    
    try:
        with db_manager.get_session() as session:
            from sqlalchemy import text
            
            # Test 1: Check database type
            print("\n1. Database Information:")
            result = session.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"   Database: {version[:60]}...")
            
            # Test 2: Check current database name
            result = session.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"   Database Name: {db_name}")
            
            # Test 3: Check connection info
            result = session.execute(text("SELECT inet_server_addr(), inet_server_port()"))
            server_info = result.fetchone()
            if server_info[0]:  # If not null (local connections might be null)
                print(f"   Server: {server_info[0]}:{server_info[1]}")
            else:
                print("   Connection: Local (via Cloud SQL Proxy)")
            
            # Test 4: Check tables exist
            print("\n2. Database Schema:")
            result = session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            for table in tables:
                print(f"   ✅ Table: {table}")
            
            # Test 5: Check table sizes
            print("\n3. Table Statistics:")
            for table in tables:
                result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                print(f"   📊 {table}: {count} records")
            
            # Test 6: Test JSON column (PostgreSQL feature)
            print("\n4. PostgreSQL JSON Features:")
            from database import SearchHistory
            
            # Insert test data with JSON
            test_search = SearchHistory(
                product_id="postgres_test_123",
                search_timestamp=datetime.utcnow(),
                jp_price=2990,
                jp_price_in_twd=650,
                tw_prices=[680, 700, 720],  # This will be stored as JSON
                product_data={
                    "title": "PostgreSQL Test Product",
                    "colors": ["Red", "Blue"],
                    "features": ["JSON storage", "PostgreSQL native"]
                },
                search_source="postgres_test",
                is_successful=True
            )
            session.add(test_search)
            session.commit()
            
            # Query JSON data
            result = session.execute(text("""
                SELECT product_data->>'title' as title,
                       tw_prices,
                       product_data->'features' as features
                FROM search_history 
                WHERE product_id = 'postgres_test_123'
            """))
            
            json_test = result.fetchone()
            if json_test:
                print(f"   ✅ JSON Query: Title = '{json_test[0]}'")
                print(f"   ✅ JSON Array: TW Prices = {json_test[1]}")
                print(f"   ✅ JSON Path: Features = {json_test[2]}")
            
            print("\n🎉 PostgreSQL migration verification completed!")
            print("✅ All PostgreSQL features working correctly")
            
            return True
            
    except Exception as e:
        print(f"\n❌ PostgreSQL test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def compare_with_sqlite():
    """Show the difference between old SQLite and new PostgreSQL"""
    print("\n" + "=" * 50)
    print("📊 MIGRATION COMPARISON")
    print("=" * 50)
    
    print("\n🗄️  BEFORE (SQLite):")
    print("   • Local file database (data/uniqlo_price_finder.db)")
    print("   • Limited concurrent connections")
    print("   • No native JSON support")
    print("   • Single-user development")
    print("   • Manual backup required")
    
    print("\n🗄️  AFTER (PostgreSQL on Cloud SQL):")
    print("   • Managed database service on Google Cloud")
    print("   • High availability and automatic backups")
    print("   • Native JSON column support")
    print("   • Concurrent connections and scaling")
    print("   • Production-ready with monitoring")
    print("   • Automatic OS and security patches")
    
    print("\n📈 BENEFITS:")
    print("   • 🚀 Better performance for concurrent users")
    print("   • 🛡️  Enhanced security and access control")
    print("   • ☁️  Cloud-native deployment ready")
    print("   • 📊 Advanced analytics capabilities")
    print("   • 🔄 Automated backup and point-in-time recovery")
    print("   • 📈 Horizontal scaling capabilities")

if __name__ == "__main__":
    # Test if we're using PostgreSQL
    db_url = str(db_manager.engine.url)
    
    if "postgresql" not in db_url:
        print("❌ Application is still using SQLite!")
        print("   Make sure Cloud SQL Proxy is running:")
        print("   ./manage-db-proxy.sh start")
        sys.exit(1)
    
    # Run PostgreSQL verification
    success = test_postgresql_features()
    
    # Show comparison
    compare_with_sqlite()
    
    if success:
        print(f"\n🎊 MIGRATION SUCCESSFUL!")
        print("   Your UNIQLO Price Finder is now running on PostgreSQL!")
        sys.exit(0)
    else:
        print(f"\n💥 Migration verification failed.")
        sys.exit(1)
