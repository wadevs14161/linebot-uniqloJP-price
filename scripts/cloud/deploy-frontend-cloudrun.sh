#!/bin/bash

# Build and Deploy Frontend to Cloud Run
# This script builds the frontend Dockerfile and deploys it as a full-stack app to Cloud Run

set -e

echo "🚀 UNIQLO Price Finder - Frontend to Cloud Run Deployment"
echo "========================================================"
echo ""

# Configuration
PROJECT_ID="bustling-flux-461615-e6"
REGION="asia-east1"
SERVICE_NAME="uniqlo-price-finder-frontend"
REPOSITORY_NAME="uniqlo-app"
IMAGE_NAME="uniqlo-frontend-fullstack"

# Validate configuration
if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo "❌ Please update PROJECT_ID in this script"
    exit 1
fi

echo "📋 Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service: $SERVICE_NAME"
echo "   Image: $IMAGE_NAME"
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
check_tool "docker"

# Authenticate with GCP
echo "🔐 Authenticating with Google Cloud..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Set the project
echo "📋 Setting GCP project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Create repository if needed
echo "🏗️  Ensuring Artifact Registry repository exists..."
gcloud artifacts repositories create $REPOSITORY_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="UNIQLO price finder application" 2>/dev/null || echo "Repository already exists"

# Build and push image
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
IMAGE_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}:${TIMESTAMP}"

echo "🔨 Building Docker image from frontend directory..."
cd frontend
docker build -t $IMAGE_TAG .

echo "📦 Pushing image to Artifact Registry..."
docker push $IMAGE_TAG

# Load database configuration if available
if [ -f "../.env.database" ]; then
    echo "📦 Loading database configuration..."
    set -a
    source ../.env.database
    set +a
    echo "   ✅ Database configuration loaded"
else
    echo "⚠️  No database configuration found"
    echo "   Application will use SQLite fallback"
fi

# Prompt for LINE Bot credentials
echo "🔐 LINE Bot Configuration (optional):"
read -p "Enter LINE_CHANNEL_SECRET (or press Enter to skip): " LINE_CHANNEL_SECRET
read -p "Enter LINE_CHANNEL_ACCESS_TOKEN (or press Enter to skip): " LINE_CHANNEL_ACCESS_TOKEN

# Build environment variables
ENV_VARS=""
if [ ! -z "$LINE_CHANNEL_SECRET" ]; then
    ENV_VARS="--set-env-vars=LINE_CHANNEL_SECRET=$LINE_CHANNEL_SECRET"
fi
if [ ! -z "$LINE_CHANNEL_ACCESS_TOKEN" ]; then
    if [ ! -z "$ENV_VARS" ]; then
        ENV_VARS="$ENV_VARS,LINE_CHANNEL_ACCESS_TOKEN=$LINE_CHANNEL_ACCESS_TOKEN"
    else
        ENV_VARS="--set-env-vars=LINE_CHANNEL_ACCESS_TOKEN=$LINE_CHANNEL_ACCESS_TOKEN"
    fi
fi

# Add database URL if available
if [ ! -z "$DATABASE_URL" ]; then
    if [ ! -z "$ENV_VARS" ]; then
        ENV_VARS="$ENV_VARS,DATABASE_URL=$DATABASE_URL"
    else
        ENV_VARS="--set-env-vars=DATABASE_URL=$DATABASE_URL"
    fi
fi

# Add Cloud SQL connection if available
CLOUD_SQL_CONNECTIONS=""
if [ ! -z "$DB_CONNECTION_NAME" ]; then
    CLOUD_SQL_CONNECTIONS="--add-cloudsql-instances=$DB_CONNECTION_NAME"
    echo "🔗 Enabling Cloud SQL connection: $DB_CONNECTION_NAME"
fi

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_TAG \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --port=8080 \
    --memory=1Gi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=10 \
    --timeout=300 \
    $CLOUD_SQL_CONNECTIONS \
    $ENV_VARS

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo ""
echo "🎉 Frontend deployment completed successfully!"
echo ""
echo "📋 Service Information:"
echo "   🌐 Service URL: $SERVICE_URL"
echo "   📍 Region: $REGION"
echo "   📦 Image: $IMAGE_TAG"
echo "   🗄️  Database: $([ ! -z "$DATABASE_URL" ] && echo "PostgreSQL (Cloud SQL)" || echo "SQLite (fallback)")"
echo ""
echo "🔗 Access your application:"
echo "   Frontend: $SERVICE_URL/frontend"
echo "   API: $SERVICE_URL/api/stats"
echo "   Health: $SERVICE_URL/"
echo ""
echo "💡 Next steps:"
echo "   1. Test the deployed application"
echo "   2. Configure custom domain (optional)"
echo "   3. Set up monitoring and alerts"
echo "   4. Configure CI/CD pipeline"
