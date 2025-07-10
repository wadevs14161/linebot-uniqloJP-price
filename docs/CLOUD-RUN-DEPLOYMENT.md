# Google Cloud Run Deployment Guide

This guide covers deploying the UNIQLO Japan Price Finder to Google Cloud Run for production use.

## Prerequisites

1. **Google Cloud Platform Account** with billing enabled
2. **Google Cloud SDK (gcloud)** installed and configured
3. **Docker** installed locally
4. **Project with required APIs enabled:**
   - Cloud Run API
   - Artifact Registry API
   - Cloud Build API (optional)

## Setup GCP Project

```bash
# Install gcloud if not already installed
# https://cloud.google.com/sdk/docs/install

# Login to Google Cloud
gcloud auth login

# Create a new project (optional)
gcloud projects create your-project-id --name="UNIQLO Price Finder"

# Set the project
gcloud config set project your-project-id

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

## Deployment Options

### Option 1: Automated Deployment (Recommended)

1. **Update project configuration:**
   ```bash
   # Edit the deployment script
   vim scripts/cloud/deploy-cloudrun.sh
   # Set your PROJECT_ID at the top of the file
   ```

2. **Run the deployment script:**
   ```bash
   ./scripts/cloud/deploy-cloudrun.sh
   ```

3. **Follow the prompts to enter your Line Bot credentials**

### Option 2: Manual Build and Push

1. **Build and push to Artifact Registry:**
   ```bash
   # Edit the build script
   vim scripts/cloud/build-and-push.sh
   # Set your PROJECT_ID
   
   # Run the build script
   ./scripts/cloud/build-and-push.sh
   ```

2. **Deploy via Google Cloud Console:**
   - Go to [Cloud Run Console](https://console.cloud.google.com/run)
   - Click "Create Service"
   - Select your pushed image
   - Configure service settings (see below)

### Option 3: Using Main Deploy Script

```bash
./deploy.sh
# Choose option 4 for Google Cloud Run
```

## Service Configuration

When deploying to Cloud Run, use these settings:

### Basic Settings
- **Service name:** `uniqlo-price-finder`
- **Region:** `us-central1` (or your preferred region)
- **CPU allocation:** Only during request processing
- **Allow unauthenticated invocations:** ✅ Yes

### Container Settings
- **Container port:** `8080`
- **Memory:** `1 GiB`
- **CPU:** `1`
- **Request timeout:** `300` seconds
- **Maximum requests per container:** `100`

### Autoscaling
- **Minimum instances:** `0`
- **Maximum instances:** `10`

### Environment Variables
```
PORT=8080
FLASK_ENV=production
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_line_access_token
FLASK_SECRET_KEY=your_secret_key (optional)
```

## Post-Deployment Configuration

### 1. Get Your Service URL
```bash
gcloud run services describe uniqlo-price-finder \
  --region=us-central1 \
  --format="value(status.url)"
```

### 2. Configure Line Bot Webhook
1. Go to [Line Developers Console](https://developers.line.biz/)
2. Select your bot
3. Go to Messaging API settings
4. Set Webhook URL to: `https://YOUR_SERVICE_URL/find_product`
5. Enable webhook
6. Disable auto-reply messages

### 3. Test Your Deployment
```bash
# Test the home page
curl https://YOUR_SERVICE_URL/

# Test the API
curl -X POST https://YOUR_SERVICE_URL/api/search \
  -H "Content-Type: application/json" \
  -d '{"product_id": "474479"}'

# Test search history
curl https://YOUR_SERVICE_URL/api/history
```

## Available Endpoints

Once deployed, your service will provide:

- **Home Page:** `https://YOUR_SERVICE_URL/`
- **Line Bot Webhook:** `https://YOUR_SERVICE_URL/find_product`
- **Product Search API:** `https://YOUR_SERVICE_URL/api/search`
- **Search History API:** `https://YOUR_SERVICE_URL/api/history`
- **Clear History API:** `https://YOUR_SERVICE_URL/api/history` (DELETE)

## Monitoring and Maintenance

### View Logs
```bash
# Real-time logs
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=uniqlo-price-finder"

# Recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=uniqlo-price-finder" --limit=100
```

### Monitor Performance
```bash
# Service details
gcloud run services describe uniqlo-price-finder --region=us-central1

# Metrics in Cloud Console
# Go to Cloud Run > uniqlo-price-finder > Metrics tab
```

### Update Deployment
```bash
# Rebuild and redeploy
./scripts/cloud/deploy-cloudrun.sh

# Or just redeploy existing image
gcloud run deploy uniqlo-price-finder \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/uniqlo-app/uniqlo-backend:latest \
  --region=us-central1
```

## Cost Management

### Cost Optimization Tips
1. **Set appropriate autoscaling:** Min instances = 0 for cost savings
2. **Monitor usage:** Use Cloud Monitoring to track requests
3. **Resource allocation:** Start with 1 CPU / 1 GiB memory
4. **Regional choice:** Choose region closest to your users

### Estimated Costs
- **Requests:** $0.40 per million requests
- **CPU time:** $0.00002400 per vCPU-second
- **Memory:** $0.00000250 per GiB-second
- **Free tier:** 2 million requests per month

## Troubleshooting

### Common Issues

1. **Service not starting:**
   ```bash
   # Check logs
   gcloud logging read "resource.type=cloud_run_revision" --limit=50
   ```

2. **Environment variables not set:**
   ```bash
   # Update environment variables
   gcloud run services update uniqlo-price-finder \
     --set-env-vars="LINE_CHANNEL_SECRET=xxx,LINE_CHANNEL_ACCESS_TOKEN=yyy" \
     --region=us-central1
   ```

3. **Database persistence:**
   - Cloud Run is stateless, so SQLite data won't persist between deployments
   - Consider using Cloud SQL or Firestore for persistent storage in production

4. **CORS issues:**
   - The app is configured to allow all origins in production
   - For security, update the CORS settings in `app.py` to specify your domain

### Support Resources
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)

## Security Considerations

1. **Environment Variables:** Store sensitive data in Secret Manager
2. **IAM:** Use least privilege access principles
3. **CORS:** Restrict origins to your actual domains
4. **HTTPS:** Cloud Run provides automatic HTTPS
5. **Database:** Consider using managed databases for production

## Cleanup

To remove all resources:

```bash
# Delete Cloud Run service
gcloud run services delete uniqlo-price-finder --region=us-central1

# Delete Artifact Registry repository
gcloud artifacts repositories delete uniqlo-app --location=us-central1

# Delete project (if no longer needed)
gcloud projects delete your-project-id
```
