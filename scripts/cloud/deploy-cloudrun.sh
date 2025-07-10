#!/bin/bash

# GCP Cloud Run Deployment Script
# This script deploys a pre-built Docker image to Google Cloud Run
# Note: Run build-and-push.sh first to build and push the Docker image

set -e  # Exit on any error

echo "🚀 UNIQLO Japan Price Finder - GCP Cloud Run Deployment"
echo "======================================================="
echo ""

# Configuration
PROJECT_ID="bustling-flux-461615-e6"
REGION="asia-east1"
SERVICE_NAME="uniqlo-price-finder"
REPOSITORY_NAME="uniqlo-app"
IMAGE_NAME="uniqlo-backend"

# Check if PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Please set your GCP PROJECT_ID in this script"
    echo "   Edit this file and set PROJECT_ID=\"your-project-id\""
    exit 1
fi

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

echo "✅ All prerequisites are available"
echo ""

# Authenticate with GCP
echo "🔐 Authenticating with Google Cloud..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Set the project
echo "📋 Setting GCP project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Use the existing image from Artifact Registry
echo "📦 Using existing Docker image from Artifact Registry..."
IMAGE_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}:latest"

# Check if image exists in registry
echo "🔍 Verifying image exists in Artifact Registry..."
if ! gcloud artifacts docker images describe $IMAGE_TAG &>/dev/null; then
    echo "❌ Image not found in Artifact Registry: $IMAGE_TAG"
    echo "   Please run the build and push script first:"
    echo "   ./scripts/cloud/build-and-push.sh"
    exit 1
fi

echo "✅ Image found: $IMAGE_TAG"

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."

# Get environment variables from user
echo ""
echo "📝 Environment Variables Setup:"
echo "For Line Bot functionality, you need:"
echo "1. LINE_CHANNEL_SECRET"
echo "2. LINE_CHANNEL_ACCESS_TOKEN"
echo ""

read -p "Enter LINE_CHANNEL_SECRET (or press Enter to skip): " LINE_CHANNEL_SECRET
read -p "Enter LINE_CHANNEL_ACCESS_TOKEN (or press Enter to skip): " LINE_CHANNEL_ACCESS_TOKEN

# Build environment variables string
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

# Deploy the service
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
    $ENV_VARS

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Service Information:"
echo "   🌐 Service URL: $SERVICE_URL"
echo "   📍 Region: $REGION"
echo "   📦 Image: $IMAGE_TAG"
echo ""
echo "🔗 Available Endpoints:"
echo "   🏠 Home page: $SERVICE_URL/"
echo "   🤖 Line Bot webhook: $SERVICE_URL/find_product"
echo "   📡 API search: $SERVICE_URL/api/search"
echo "   📊 API history: $SERVICE_URL/api/history"
echo ""
echo "⚙️  Configuration for Line Bot:"
echo "   1. Go to Line Developers Console"
echo "   2. Set webhook URL to: $SERVICE_URL/find_product"
echo "   3. Enable webhook and disable auto-reply"
echo ""
echo "🧪 Test your deployment:"
echo "   curl $SERVICE_URL/"
echo "   curl -X POST $SERVICE_URL/api/search -H \"Content-Type: application/json\" -d '{\"product_id\":\"474479\"}'"
echo ""
echo "📊 Monitor your service:"
echo "   gcloud run services describe $SERVICE_NAME --region=$REGION"
echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit=50"
echo ""
echo "🛑 To delete the service:"
echo "   gcloud run services delete $SERVICE_NAME --region=$REGION"

# Test the deployment
echo ""
echo "🧪 Testing deployment..."
if curl -f "$SERVICE_URL/" > /dev/null 2>&1; then
    echo "✅ Service is responding correctly!"
else
    echo "⚠️  Service might still be starting up. Try the test URL in a few minutes."
fi

echo ""
echo "✨ Your UNIQLO price finder is now live on Google Cloud Run!"
echo ""
echo "💡 Deployment Workflow:"
echo "   1. Build & Push: ./scripts/cloud/build-and-push.sh"
echo "   2. Deploy: ./scripts/cloud/deploy-cloudrun.sh (this script)"
echo "   3. Update: Run step 1 then step 2 for new deployments"
