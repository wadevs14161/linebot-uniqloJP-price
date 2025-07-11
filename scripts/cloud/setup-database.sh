#!/bin/bash

# GCP Cloud SQL Database Setup Script
# This script creates a minimal PostgreSQL database for the UNIQLO price finder

set -e

echo "🗄️  UNIQLO Price Finder - Cloud SQL Database Setup"
echo "=================================================="
echo ""

# Configuration
PROJECT_ID="bustling-flux-461615-e6"
REGION="asia-east1"
ZONE="asia-east1-b"
DB_INSTANCE_NAME="uniqlo-db"
DB_NAME="uniqlo_price_finder"
DB_USER="uniqlo_user"
DB_TIER="db-f1-micro"  # Smallest/cheapest tier
STORAGE_SIZE="10GB"     # Minimum storage
STORAGE_TYPE="SSD"

# Generate a random password
DB_PASSWORD=$(openssl rand -base64 32)

echo "📋 Database Configuration:"
echo "   Instance: $DB_INSTANCE_NAME"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo "   Tier: $DB_TIER (cheapest option)"
echo "   Storage: $STORAGE_SIZE $STORAGE_TYPE"
echo "   Region: $REGION"
echo ""

# Check if required tools are installed
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        exit 1
    fi
}

echo "🔧 Checking prerequisites..."
check_tool "gcloud"
check_tool "openssl"

# Set the project
echo "📋 Setting GCP project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔌 Enabling required APIs..."
gcloud services enable sqladmin.googleapis.com
gcloud services enable sql-component.googleapis.com

# Create Cloud SQL instance
echo "🏗️  Creating Cloud SQL PostgreSQL instance..."
echo "   ⏳ This may take 5-10 minutes..."

gcloud sql instances create $DB_INSTANCE_NAME \
    --database-version=POSTGRES_15 \
    --tier=$DB_TIER \
    --region=$REGION \
    --availability-type=zonal \
    --storage-type=$STORAGE_TYPE \
    --storage-size=$STORAGE_SIZE \
    --storage-auto-increase \
    --backup-start-time=03:00 \
    --maintenance-release-channel=production \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=4 \
    --deletion-protection

echo "✅ Cloud SQL instance created: $DB_INSTANCE_NAME"

# Set the root password
echo "🔐 Setting database password..."
gcloud sql users set-password postgres \
    --instance=$DB_INSTANCE_NAME \
    --password="$DB_PASSWORD"

# Create application database
echo "🗄️  Creating application database..."
gcloud sql databases create $DB_NAME \
    --instance=$DB_INSTANCE_NAME

# Create application user
echo "👤 Creating application user..."
gcloud sql users create $DB_USER \
    --instance=$DB_INSTANCE_NAME \
    --password="$DB_PASSWORD"

# Get connection name for Cloud Run
CONNECTION_NAME=$(gcloud sql instances describe $DB_INSTANCE_NAME --format="value(connectionName)")

# Create .env file for local development
echo "📝 Creating environment configuration..."
cat > ../../.env.database << EOF
# Database Configuration
# Generated on $(date)

# Cloud SQL Connection
DB_CONNECTION_NAME=$CONNECTION_NAME
DB_HOST=localhost  # Use Cloud SQL Proxy for local development
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD

# For Cloud Run deployment
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@/$DB_NAME?host=/cloudsql/$CONNECTION_NAME

# Connection Pool Settings
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
EOF

echo ""
echo "🎉 Database setup completed successfully!"
echo ""
echo "📋 Database Information:"
echo "   🌐 Instance: $DB_INSTANCE_NAME"
echo "   📍 Region: $REGION"
echo "   🗄️  Database: $DB_NAME"
echo "   👤 User: $DB_USER"
echo "   🔌 Connection: $CONNECTION_NAME"
echo ""
echo "🔐 Credentials saved to: .env.database"
echo "   ⚠️  Keep this file secure and don't commit it to version control!"
echo ""
echo "🔗 Next Steps:"
echo "   1. Install Cloud SQL Proxy for local development:"
echo "      gcloud components install cloud_sql_proxy"
echo ""
echo "   2. Start Cloud SQL Proxy for local development:"
echo "      cloud_sql_proxy -instances=$CONNECTION_NAME=tcp:5432"
echo ""
echo "   3. Update your application to use the database"
echo "   4. Deploy with database connection"
echo ""
echo "💰 Cost Optimization:"
echo "   - Instance: ~\$7-10/month (db-f1-micro)"
echo "   - Storage: ~\$0.17/GB/month (10GB = ~\$1.7/month)"
echo "   - Total: ~\$8-12/month"
echo ""
echo "🛑 To delete the database (if needed):"
echo "   gcloud sql instances delete $DB_INSTANCE_NAME"
