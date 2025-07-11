#!/bin/bash

# Build and Push to GCP Artifact Registry
# This script only builds and pushes the Docker image, without deploying

set -e

echo "🐳 Building and Pushing UNIQLO Price Finder to GCP Artifact Registry"
echo "===================================================================="
echo ""

# Configuration - UPDATE THESE VALUES
PROJECT_ID="bustling-flux-461615-e6"  # ⚠️ CHANGE THIS
REGION="asia-east1"  # e.g., asia-east1, us-central1
REPOSITORY_NAME="uniqlo-app"
IMAGE_NAME="uniqlo-backend"

# Validate configuration
if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo "❌ Please update PROJECT_ID in this script with your actual GCP project ID"
    exit 1
fi

echo "📋 Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Repository: $REPOSITORY_NAME"
echo "   Image: $IMAGE_NAME"
echo ""

# Authenticate
echo "🔐 Configuring Docker authentication..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Set project
gcloud config set project $PROJECT_ID

# Create repository if needed
echo "🏗️  Ensuring Artifact Registry repository exists..."
gcloud artifacts repositories create $REPOSITORY_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="UNIQLO price finder application" 2>/dev/null || echo "Repository already exists"

# Build image
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
IMAGE_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}:${TIMESTAMP}"
echo "🔨 Building Docker image: $IMAGE_TAG"
docker build -f Dockerfile.cloudrun -t $IMAGE_TAG .

# Push image
echo "📤 Pushing image to Artifact Registry..."
docker push $IMAGE_TAG

echo ""
echo "✅ Image successfully pushed to Artifact Registry!"
echo ""
echo "📦 Image URI: $IMAGE_TAG"
echo ""
echo "🚀 Next steps for Cloud Run deployment:"
echo "   1. Go to Google Cloud Console > Cloud Run"
echo "   2. Click 'Create Service'"
echo "   3. Select 'Deploy one revision from an existing container image'"
echo "   4. Enter image URI: $IMAGE_TAG"
echo "   5. Configure:"
echo "      - Service name: uniqlo-price-finder"
echo "      - Region: $REGION"
echo "      - Allow unauthenticated invocations: ✅"
echo "      - Container port: 8080"
echo "      - Memory: 1 GiB"
echo "      - CPU: 1"
echo "   6. Add environment variables (if needed):"
echo "      - LINE_CHANNEL_SECRET"
echo "      - LINE_CHANNEL_ACCESS_TOKEN"
echo "   7. Click 'Create'"
echo ""
echo "🔗 Or use the automated deployment script:"
echo "   ./scripts/cloud/deploy-cloudrun.sh"
