# Uniqlo Japan Price Finder

A comprehensive solution for finding Uniqlo Japan product prices and stock availability with both Line Bot and Web Interface.

## Features
- 🔍 Find product on Uniqlo Japan by 6-digit product ID
- 💰 Real-time price conversion from JPY to TWD
- 📦 Stock availability by color and size
- 🤖 Line Bot integration for mobile convenience
- 🌐 Modern React web interface with search history
- 📊 Persistent search history using local storage

## Tech Stack

### Backend
- Python 3.12
- Flask (REST API & Line Bot webhook)
- BeautifulSoup4 (Web scraping)
- Line Bot SDK v3

### Frontend
- React 18 with TypeScript
- Material-UI (MUI) components
- Vite build tool
- Axios for API calls

### Infrastructure
- VM (Linux)
- nginx (Load balancer)
- ngrok (Development tunneling)

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 20.11.1+
- Line Developer Account (for Line Bot)
- Docker & Docker Compose (for containerized deployment)
- ngrok (for external access)

### Option 1: Local Development

#### Backend Setup

1. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export LINE_CHANNEL_SECRET="your_line_channel_secret"
export LINE_CHANNEL_ACCESS_TOKEN="your_line_access_token"
```

4. Start Flask server:
```bash
python app.py
```

#### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

4. Open browser to `http://localhost:5173`

### Option 2: Docker Deployment (Recommended for Production)

#### Quick Start with Docker + ngrok

1. **Automated deployment:**
```bash
./deploy-docker-ngrok.sh
```

2. **Manual deployment:**
```bash
# Build and start containers
docker-compose up --build -d

# Start ngrok tunnels (in separate terminals)
ngrok http 5000  # Backend
ngrok http 3000  # Frontend
```

#### Benefits of Docker Deployment:
- ✅ Consistent environment across different machines
- ✅ Easy scaling and management
- ✅ Isolated dependencies
- ✅ Production-ready setup
- ✅ Quick deployment with ngrok for external access

For detailed Docker deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Usage

### Web Interface
1. Open the web interface at `http://localhost:5173`
2. Enter a 6-digit Uniqlo product ID (e.g., 474479)
3. Click "Search" or press Enter
4. View product information in the search history table
5. Click "View Product" to open the product page on Uniqlo Japan

### Line Bot
1. Add Line official account: &nbsp;&nbsp;&nbsp;<img src="https://i.imgur.com/vMRg9de.png" width="100" height="100"/>
2. Send commands:
   - **Product ID**: Send 6-digit number to get product info
   - **"1"**: Get example product ID image

## Product ID Format
6-digit number from UNIQLO price tag:

<img src="https://i.imgur.com/HLw9BhO.jpg" width="200" height="200"/>

### Line Bot Examples

#### Text Input
<img src="https://i.imgur.com/FD04WtB.png" width="200" height="411"/>

#### Image Input (Deprecated)
<img src="https://i.imgur.com/yjj7aUL.png" width="200" height="411"/>

## API Endpoints

- `GET /` - Main page with links to web interface
- `POST /find_product` - Line Bot webhook endpoint
- `POST /api/search` - REST API for product search

## Project Structure

```
linebot-uniqloJP-price/
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── App.tsx          # Main React component
│   │   └── main.tsx         # App entry point
│   ├── package.json
│   └── README.md
├── app.py                   # Flask server & Line Bot
├── crawl.py                 # Web scraping logic
├── reply.py                 # Line Bot response formatting
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Development

### Running Both Services
1. Start backend: `python app.py` (port 5000)
2. Start frontend: `cd frontend && npm run dev` (port 5173)
3. Access web interface: `http://localhost:5173`
4. Access backend: `http://localhost:5000`

### ngrok Setup (for Line Bot)
```bash
ngrok http 5000
```
Use the ngrok URL as your Line Bot webhook endpoint.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both frontend and backend
5. Submit a pull request
