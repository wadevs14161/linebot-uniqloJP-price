#!/bin/bash

# Cloud SQL Proxy Management Script
# This script helps start/stop the Cloud SQL Proxy for local development

set -e

PROXY_PATH="/usr/local/share/google-cloud-sdk/bin/cloud_sql_proxy"
CONNECTION_NAME="bustling-flux-461615-e6:asia-east1:uniqlo-db"
LOCAL_PORT="5432"

case "${1:-}" in
    "start")
        echo "🔌 Starting Cloud SQL Proxy..."
        if pgrep -f "cloud_sql_proxy" > /dev/null; then
            echo "⚠️  Cloud SQL Proxy is already running"
            ps aux | grep cloud_sql_proxy | grep -v grep
        else
            echo "Starting proxy: $CONNECTION_NAME -> localhost:$LOCAL_PORT"
            nohup $PROXY_PATH -instances=$CONNECTION_NAME=tcp:$LOCAL_PORT > cloud_sql_proxy.log 2>&1 &
            echo "✅ Cloud SQL Proxy started (PID: $!)"
            echo "📝 Logs: cloud_sql_proxy.log"
            sleep 2
            
            # Test connection
            echo "🧪 Testing database connection..."
            if python -c "import psycopg2; psycopg2.connect(host='localhost', port=5432, database='uniqlo_price_finder', user='uniqlo_user', password='$(grep DB_PASSWORD .env.database | cut -d= -f2)')" 2>/dev/null; then
                echo "✅ Database connection successful!"
            else
                echo "❌ Database connection failed"
            fi
        fi
        ;;
    
    "stop")
        echo "🛑 Stopping Cloud SQL Proxy..."
        if pgrep -f "cloud_sql_proxy" > /dev/null; then
            pkill -f "cloud_sql_proxy"
            echo "✅ Cloud SQL Proxy stopped"
        else
            echo "⚠️  Cloud SQL Proxy is not running"
        fi
        ;;
    
    "status")
        echo "📊 Cloud SQL Proxy Status:"
        if pgrep -f "cloud_sql_proxy" > /dev/null; then
            echo "✅ Running"
            ps aux | grep cloud_sql_proxy | grep -v grep
        else
            echo "❌ Not running"
        fi
        ;;
    
    "restart")
        echo "🔄 Restarting Cloud SQL Proxy..."
        $0 stop
        sleep 2
        $0 start
        ;;
    
    *)
        echo "🗄️  UNIQLO Price Finder - Cloud SQL Proxy Manager"
        echo "================================================"
        echo ""
        echo "Usage: $0 {start|stop|status|restart}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the Cloud SQL Proxy"
        echo "  stop    - Stop the Cloud SQL Proxy"
        echo "  status  - Check if proxy is running"
        echo "  restart - Restart the proxy"
        echo ""
        echo "📋 Current Configuration:"
        echo "  Connection: $CONNECTION_NAME"
        echo "  Local Port: $LOCAL_PORT"
        echo "  Database: uniqlo_price_finder"
        echo ""
        exit 1
        ;;
esac
