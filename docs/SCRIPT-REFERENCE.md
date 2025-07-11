# Script Reference

## Quick Access to Scripts

### Deployment Scripts
- **Main deployment**: `scripts/deployment/deploy-single-ngrok.sh` - Deploy unified Docker app with ngrok
- **Legacy deployment**: `scripts/deployment/deploy.sh` - Original deployment script  
- **Docker + ngrok**: `scripts/deployment/deploy-docker-ngrok.sh` - Docker with ngrok
- **Frontend build**: `scripts/deployment/build-frontend.sh` - Build React frontend

### Cloud Scripts  
- **Cloud Run deploy**: `scripts/cloud/deploy-cloudrun.sh` - Deploy to Google Cloud Run
- **Build & push**: `scripts/cloud/build-and-push.sh` - Build and push Docker images
- **Setup database**: `scripts/cloud/setup-database.sh` - Initialize cloud database

### Database Scripts
- **DB proxy management**: `scripts/database/manage-db-proxy.sh` - Manage database proxy connections

### Testing Scripts
- **Main test**: `scripts/test.sh` - Run application tests
- **SQLite integration**: `scripts/testing/test-sqlite-integration.sh` - Test database integration

### Docker Configuration
- **Cloud Run service**: `docker/cloudrun-service.yaml` - Cloud Run deployment config
- **Dev compose**: `docker/compose/docker-compose.dev.yml` - Development environment
- **Production compose**: `docker/compose/docker-compose.production.yml` - Production environment  
- **Docker entrypoint**: `docker/docker-entrypoint.sh` - Container startup script

## Usage Examples

```bash
# Deploy locally with ngrok
./scripts/deployment/deploy-single-ngrok.sh

# Deploy to Cloud Run
./scripts/cloud/deploy-cloudrun.sh

# Build frontend only
./scripts/deployment/build-frontend.sh

# Run tests
./scripts/test.sh
```
