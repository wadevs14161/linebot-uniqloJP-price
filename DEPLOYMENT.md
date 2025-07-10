# Docker + ngrok Deployment Guide

This guide explains how to deploy the Uniqlo Japan Price Finder using Docker containers and expose them to external users via ngrok.

## Prerequisites

- Docker and Docker Compose installed
- ngrok account and CLI installed
- Line Bot webhook URL configuration access

## Quick Start

### Option 1: Single ngrok Tunnel (Recommended for Free Accounts)

Uses nginx reverse proxy to serve both frontend and backend through one tunnel:

```bash
# Automated deployment with single ngrok tunnel
./deploy-docker-ngrok.sh
```

**Architecture:**
```
Internet → ngrok (port 8080) → nginx → frontend (React) + backend (Flask)
```

**URLs:**
- Frontend: `https://abc123.ngrok.io/`
- API: `https://abc123.ngrok.io/api/search`
- Line Bot webhook: `https://abc123.ngrok.io/find_product`

### Option 2: Dual ngrok Tunnels (For Paid ngrok Accounts)

Separate tunnels for frontend and backend:

```bash
# Automated deployment with dual ngrok tunnels
./deploy-docker-ngrok-dual.sh
```

**Architecture:**
```
Internet → ngrok (port 5000) → Backend (Flask)
Internet → ngrok (port 3000) → Frontend (React)
```

### Option 3: Manual Deployment

#### Single Tunnel Setup:
```bash
# Build and start with nginx proxy
docker-compose up --build -d

# Start single ngrok tunnel
ngrok http 8080
```

#### Dual Tunnel Setup:
```bash
# Build and start with individual ports
docker-compose -f docker-compose.dev.yml up --build -d

# Start ngrok tunnels (in separate terminals)
ngrok http 5000  # Backend
ngrok http 3000  # Frontend
```

## Architecture

```
Internet
    ↓
[ngrok tunnels]
    ↓
[Docker containers]
├── Backend (Flask) - Port 5000
└── Frontend (React) - Port 3000
```

## Configuration

### Environment Variables

The `.env` file contains your Line Bot credentials:
```
LINE_CHANNEL_SECRET=your_secret_here
LINE_CHANNEL_ACCESS_TOKEN=your_token_here
```

### Port Mapping

- Backend: `localhost:5000` → `Docker container:5000`
- Frontend: `localhost:3000` → `Docker container:3000`

## Usage

### 1. Line Bot Setup

1. Copy the backend ngrok URL (e.g., `https://abc123.ngrok.io`)
2. Update your Line Bot webhook URL to: `https://abc123.ngrok.io/find_product`
3. Test by sending a product ID to your Line Bot

### 2. Web Interface Access

1. Copy the frontend ngrok URL (e.g., `https://def456.ngrok.io`)
2. Share this URL with users for web-based access
3. Users can search products directly in their browsers

## Monitoring

### Check container status:
```bash
docker-compose ps
```

### View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Access container shells:
```bash
# Backend container
docker-compose exec backend bash

# Frontend container  
docker-compose exec frontend sh
```

## Stopping Services

### Stop Docker containers:
```bash
docker-compose down
```

### Stop ngrok tunnels:
- Press `Ctrl+C` in ngrok terminal windows
- Or kill ngrok processes: `pkill ngrok`

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   - Change ports in `docker-compose.yml` if 5000/3000 are in use
   - Update frontend `.env` file with new backend port

2. **ngrok connection issues:**
   - Check ngrok account limits (free accounts have restrictions)
   - Verify ngrok authentication: `ngrok authtoken YOUR_TOKEN`

3. **Line Bot webhook errors:**
   - Ensure webhook URL includes `/find_product` endpoint
   - Check Line Bot console for error messages
   - Verify environment variables are correctly set

4. **CORS issues:**
   - Backend already has CORS enabled for all origins
   - If issues persist, check browser developer console

### Debug Commands

```bash
# Check if containers are running
docker ps

# Check Docker logs
docker-compose logs backend
docker-compose logs frontend

# Test backend API directly
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"product_id": "474479"}'

# Check ngrok status
curl http://localhost:4040/api/tunnels
```

## Production Considerations

For production deployment, consider:

1. **Use proper container orchestration** (Kubernetes, Docker Swarm)
2. **Replace ngrok with proper load balancer** (nginx, HAProxy)
3. **Add SSL certificates** for HTTPS
4. **Use environment-specific configurations**
5. **Add monitoring and logging** (Prometheus, ELK stack)
6. **Implement proper security measures** (firewall, rate limiting)

## Security Notes

- The `.env` file contains sensitive credentials - never commit to version control
- ngrok tunnels are public - consider using ngrok authentication for production
- Monitor ngrok usage to avoid hitting free tier limits

## Costs

### Free Tier Limitations:
- **ngrok**: 1 online ngrok process, 40 connections/minute
- **Docker**: No limits on local usage

### Upgrade Options:
- **ngrok Pro**: Multiple tunnels, custom domains, higher limits
- **Cloud hosting**: AWS, GCP, Azure for production deployment
