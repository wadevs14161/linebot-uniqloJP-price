#!/bin/bash

# Cloud Run deployment test script
# This script tests if the Cloud Run deployment is configured correctly

echo "🧪 Testing Cloud Run Deployment Configuration"
echo "============================================="
echo ""

# Check if required files exist
echo "1️⃣ Checking required files..."

required_files=(
    "Dockerfile.cloudrun"
    ".gcloudignore"
    "scripts/cloud/deploy-cloudrun.sh"
    "scripts/cloud/build-and-push.sh"
    "app.py"
    "requirements.txt"
)

all_files_exist=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file is missing"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = false ]; then
    echo ""
    echo "❌ Some required files are missing. Cannot proceed with deployment."
    exit 1
fi

echo ""
echo "2️⃣ Checking Docker build (without pushing)..."

# Test Docker build
if docker build -f Dockerfile.cloudrun -t uniqlo-test . > /dev/null 2>&1; then
    echo "✅ Docker build successful"
    # Clean up test image
    docker rmi uniqlo-test > /dev/null 2>&1 || true
else
    echo "❌ Docker build failed"
    echo ""
    echo "💡 Try running manually: docker build -f Dockerfile.cloudrun -t uniqlo-test ."
    exit 1
fi

echo ""
echo "3️⃣ Checking application configuration..."

# Check if app.py has proper Cloud Run configuration
if grep -q "PORT" app.py && grep -q "0.0.0.0" app.py; then
    echo "✅ App configured for Cloud Run (PORT and host binding)"
else
    echo "❌ App not properly configured for Cloud Run"
    exit 1
fi

# Check if CORS is properly configured
if grep -q "CORS" app.py; then
    echo "✅ CORS is configured"
else
    echo "❌ CORS not configured"
    exit 1
fi

echo ""
echo "4️⃣ Checking GCP tools..."

if command -v gcloud &> /dev/null; then
    echo "✅ gcloud CLI is installed"
    
    # Check if user is authenticated
    if gcloud auth list --format="value(account)" | grep -q "@"; then
        echo "✅ gcloud is authenticated"
    else
        echo "⚠️  gcloud not authenticated. Run: gcloud auth login"
    fi
else
    echo "❌ gcloud CLI not installed"
    echo "💡 Install from: https://cloud.google.com/sdk/docs/install"
fi

echo ""
echo "5️⃣ Configuration Summary:"
echo ""
echo "📋 To deploy to Cloud Run:"
echo "   1. Update PROJECT_ID in scripts/cloud/deploy-cloudrun.sh"
echo "   2. Run: ./scripts/cloud/deploy-cloudrun.sh"
echo ""
echo "📋 To just build and push image:"
echo "   1. Update PROJECT_ID in scripts/cloud/build-and-push.sh" 
echo "   2. Run: ./scripts/cloud/build-and-push.sh"
echo ""
echo "📋 To deploy via main script:"
echo "   ./deploy.sh (choose option 4)"
echo ""

if [ "$all_files_exist" = true ]; then
    echo "🎉 Cloud Run deployment configuration is ready!"
    echo ""
    echo "⚠️  Remember to:"
    echo "   - Update PROJECT_ID in deployment scripts"
    echo "   - Set LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN"
    echo "   - Test the deployed URL after deployment"
else
    echo "❌ Cloud Run deployment configuration has issues"
fi
