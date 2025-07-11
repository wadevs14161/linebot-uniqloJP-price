#!/bin/bash

# Docker entrypoint script for UNIQLO Price Finder
# Handles both local Docker and Cloud Run deployment

set -e

echo "🐳 UNIQLO Price Finder - Docker Startup"
echo "======================================="

# Function to start Cloud SQL Proxy in container
start_cloud_sql_proxy() {
    if [ ! -z "$DB_CONNECTION_NAME" ]; then
        echo "🔌 Starting Cloud SQL Proxy for: $DB_CONNECTION_NAME"
        /usr/local/bin/cloud_sql_proxy -instances="$DB_CONNECTION_NAME"=tcp:5432 &
        PROXY_PID=$!
        echo "✅ Cloud SQL Proxy started (PID: $PROXY_PID)"
        
        # Wait for proxy to be ready
        echo "⏳ Waiting for Cloud SQL Proxy to be ready..."
        sleep 5
        
        # Test connection
        if python -c "import psycopg2; psycopg2.connect(host='localhost', port=5432, database='$DB_NAME', user='$DB_USER', password='$DB_PASSWORD')" 2>/dev/null; then
            echo "✅ Database connection successful!"
        else
            echo "❌ Database connection failed, using SQLite fallback"
        fi
    else
        echo "📋 No Cloud SQL connection configured, using SQLite fallback"
    fi
}

# Function to detect deployment environment
detect_environment() {
    if [ ! -z "$K_SERVICE" ]; then
        echo "☁️  Running on Google Cloud Run"
        export DEPLOYMENT_ENV="cloudrun"
    elif [ ! -z "$KUBERNETES_SERVICE_HOST" ]; then
        echo "⚙️  Running on Kubernetes"
        export DEPLOYMENT_ENV="kubernetes"
    else
        echo "🐳 Running in local Docker container"
        export DEPLOYMENT_ENV="docker"
    fi
}

# Function to set up database connection
setup_database() {
    echo "🗄️  Setting up database connection..."
    
    case "$DEPLOYMENT_ENV" in
        "cloudrun")
            # Cloud Run uses Unix socket connection to Cloud SQL
            echo "📡 Using Cloud Run Cloud SQL connection"
            if [ ! -z "$DATABASE_URL" ]; then
                echo "✅ DATABASE_URL configured for Cloud Run"
            else
                echo "⚠️  No DATABASE_URL found, using SQLite fallback"
            fi
            ;;
        "docker"|"kubernetes")
            # Local Docker or Kubernetes needs Cloud SQL Proxy
            if [ ! -z "$DB_CONNECTION_NAME" ] && [ ! -z "$DB_PASSWORD" ]; then
                start_cloud_sql_proxy
            else
                echo "⚠️  Missing Cloud SQL credentials, using SQLite fallback"
                echo "   Required: DB_CONNECTION_NAME, DB_PASSWORD, DB_NAME, DB_USER"
            fi
            ;;
        *)
            echo "⚠️  Unknown environment, using SQLite fallback"
            ;;
    esac
}

# Function to wait for database
wait_for_database() {
    echo "⏳ Waiting for database to be ready..."
    
    for i in {1..30}; do
        if python -c "
from database import db_manager
try:
    with db_manager.get_session() as session:
        from sqlalchemy import text
        session.execute(text('SELECT 1'))
    print('Database ready!')
    exit(0)
except Exception as e:
    print(f'Database not ready: {e}')
    exit(1)
" 2>/dev/null; then
            echo "✅ Database is ready!"
            break
        else
            echo "🔄 Database not ready, retrying... ($i/30)"
            sleep 2
        fi
    done
}

# Function to initialize database tables
init_database() {
    echo "🏗️  Initializing database tables..."
    python -c "
from database import db_manager, Base
try:
    Base.metadata.create_all(db_manager.engine)
    print('✅ Database tables initialized')
except Exception as e:
    print(f'⚠️  Table initialization failed: {e}')
"
}

# Main startup sequence
main() {
    echo "🚀 Starting UNIQLO Price Finder..."
    
    # Detect environment
    detect_environment
    
    # Setup database connection
    setup_database
    
    # Wait for database to be ready
    wait_for_database
    
    # Initialize database tables
    init_database
    
    echo "✅ Startup complete! Running application..."
    echo ""
    
    # Execute the main command
    exec "$@"
}

# Run main function
main "$@"
