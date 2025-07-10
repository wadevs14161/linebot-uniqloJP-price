# Google Cloud Run Deployment Guide

This guide explains how to deploy the UNIQLO Japan Price Finder to Google Cloud Run for production use.

## Prerequisites

1. **Google Cloud Platform Account**
   - Create a GCP project
   - Enable billing
   - Enable Cloud Run API and Artifact Registry API

2. **Required Tools**
   - [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install)
   - Docker

3. **Authentication**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

## Quick Deployment

### Option 1: Interactive Deployment
```bash
./deploy.sh
# Choose option 4: Google Cloud Run
```

### Option 2: Direct Cloud Run Deployment
```bash
# Update PROJECT_ID in the script first
./scripts/cloud/deploy-cloudrun.sh
```

### Option 3: Build and Push Only
```bash
# If you want to build/push image separately
./scripts/cloud/build-and-push.sh
```

## Configuration

### 1. Update Project Settings
Edit the deployment script with your GCP project details:

```bash
# In scripts/cloud/deploy-cloudrun.sh
PROJECT_ID="your-project-id"        # ⚠️ CHANGE THIS
REGION="asia-east1"                 # Change if needed
SERVICE_NAME="uniqlo-price-finder"  # Change if needed
```

### 2. Environment Variables
The deployment script will prompt for:
- `LINE_CHANNEL_SECRET` - Your Line Bot channel secret
- `LINE_CHANNEL_ACCESS_TOKEN` - Your Line Bot access token

You can also set these later via GCP Console.

## Deployment Process

The deployment script will automatically:

1. **🔐 Authenticate** with Google Cloud
2. **🏗️ Create** Artifact Registry repository
3. **🐳 Build** optimized Docker image
4. **📤 Push** image to Artifact Registry
5. **🚀 Deploy** to Cloud Run with proper configuration
6. **✅ Test** the deployment

## Cloud Run Configuration

The app is deployed with these settings:
- **Port**: 8080 (automatically configured)
- **Memory**: 1GB
- **CPU**: 1 vCPU
- **Min instances**: 0 (scales to zero)
- **Max instances**: 10
- **Timeout**: 300 seconds
- **Public access**: Enabled (unauthenticated requests allowed)

## Post-Deployment Setup

### 1. Line Bot Configuration
After deployment, you'll get a service URL like:
```
https://uniqlo-price-finder-xxx-xx.a.run.app
```

Update your Line Bot webhook URL to:
```
https://your-service-url.a.run.app/find_product
```

### 2. Test Your Deployment
```bash
# Test home page
curl https://your-service-url.a.run.app/

# Test API
curl -X POST https://your-service-url.a.run.app/api/search \
  -H "Content-Type: application/json" \
  -d '{"product_id":"474479"}'
```

## Available Endpoints

Once deployed, your service provides:

- **🏠 Home Page**: `https://your-service-url.a.run.app/`
- **🤖 Line Bot**: `https://your-service-url.a.run.app/find_product`
- **🔍 Search API**: `https://your-service-url.a.run.app/api/search`
- **📊 History API**: `https://your-service-url.a.run.app/api/history`

## Database Persistence

⚠️ **Important**: Cloud Run is stateless. The SQLite database will be reset with each deployment.

For production with persistent data, consider:
1. **Cloud SQL** - Managed PostgreSQL/MySQL
2. **Firestore** - NoSQL document database
3. **Cloud Storage** - For file-based SQLite backup/restore

## Monitoring and Logs

### View Logs
```bash
gcloud logging read "resource.type=cloud_run_revision" --limit=50
```

### Service Information
```bash
gcloud run services describe uniqlo-price-finder --region=asia-east1
```

### Service URL
```bash
gcloud run services describe uniqlo-price-finder \
  --region=asia-east1 \
  --format="value(status.url)"
```

## Cost Optimization

Cloud Run pricing is based on:
- **CPU usage** during request processing
- **Memory usage** during request processing  
- **Number of requests**

The app scales to zero when not in use, so you only pay for actual usage.

## Troubleshooting

### Common Issues

1. **Build Fails**
   ```bash
   # Test Docker build locally
   docker build -f Dockerfile.cloudrun -t test-image .
   ```

2. **Service Not Accessible**
   - Check if `--allow-unauthenticated` is set
   - Verify the service URL is correct
   - Check Cloud Run logs for errors

3. **Environment Variables Missing**
   ```bash
   # Update environment variables
   gcloud run services update uniqlo-price-finder \
     --region=asia-east1 \
     --set-env-vars="LINE_CHANNEL_SECRET=your-secret"
   ```

4. **Database Issues**
   - Remember that SQLite is ephemeral in Cloud Run
   - Consider using Cloud SQL for persistence

### Getting Help

```bash
# View deployment status
gcloud run services list

# Check service details
gcloud run services describe uniqlo-price-finder --region=asia-east1

# View recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=uniqlo-price-finder" --limit=20
```

## Security Considerations

1. **Environment Variables**: Store sensitive data in Secret Manager
2. **CORS**: Configure proper origins for production
3. **Rate Limiting**: Consider implementing API rate limits
4. **Authentication**: Add authentication for admin features

## Updating Your Deployment

To update your deployed service:

```bash
# Re-run the deployment script
./scripts/cloud/deploy-cloudrun.sh

# Or just build and push new image
./scripts/cloud/build-and-push.sh
gcloud run deploy uniqlo-price-finder --image=NEW_IMAGE_URL
```

## Cleanup

To remove all resources:

```bash
# Delete Cloud Run service
gcloud run services delete uniqlo-price-finder --region=asia-east1

# Delete Docker images (optional)
gcloud artifacts repositories delete uniqlo-app --location=asia-east1
```

## Production Checklist

- [ ] Update PROJECT_ID in deployment scripts
- [ ] Set proper environment variables
- [ ] Configure Line Bot webhook URL
- [ ] Test all endpoints
- [ ] Set up monitoring/alerting
- [ ] Consider database persistence strategy
- [ ] Configure proper CORS origins
- [ ] Set up backup strategy (if needed)
