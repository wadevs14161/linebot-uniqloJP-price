# Uniqlo Japan Price Finder - Frontend

A React TypeScript frontend for searching Uniqlo Japan product prices and stock availability.

## Features

- 🔍 Product search by 6-digit product ID
- 📊 Search history table with local storage
- 💰 Price display in both JPY and TWD
- 📦 Stock availability by color and size
- 🇯🇵 Japanese flag in the header
- 📱 Responsive Material-UI design

## Getting Started

### Prerequisites

- Node.js (v20.11.1 or higher)
- npm

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

### Backend Requirement

Make sure the Flask backend is running on `http://localhost:5000` for the product search functionality to work.

## Usage

1. Enter a 6-digit Uniqlo product ID (e.g., 474479)
2. Click "Search" or press Enter
3. View the product information in the search history table
4. Click "View Product" to open the product page on Uniqlo Japan

## Components

- **Search Bar**: Input field for product ID with search button
- **Search History Table**: Displays all previous searches with:
  - Product ID (6 digits)
  - Alternative Product ID
  - Product URL (clickable link)
  - Price in JPY
  - Price in TWD (converted)
  - Available sizes by color
  - Search timestamp

## Technologies Used

- React 18
- TypeScript
- Material-UI (MUI)
- Vite
- Axios for API calls

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
