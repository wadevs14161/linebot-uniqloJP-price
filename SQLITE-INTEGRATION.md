# SQLite3 Search History Integration Guide

## Overview

This system now includes SQLite3 database integration to store user search history with unique user identification. The implementation provides persistent search history across sessions while respecting user privacy.

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Search History Table
```sql
CREATE TABLE search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    product_name TEXT,
    price TEXT,
    colors TEXT,
    sizes TEXT,
    image_url TEXT,
    product_url TEXT,
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);
```

## User Identification Strategy

The system uses a hybrid approach for user identification:

### 1. Session-Based Identification (Primary)
- Uses Flask sessions to track users across requests
- Session data is stored on the server side
- Provides seamless experience for users during their session

### 2. Fingerprint-Based Identification (Fallback)
- Creates a unique identifier using MD5 hash of IP address + User Agent
- Ensures users can be tracked even if sessions are cleared
- Format: MD5(IP_ADDRESS:USER_AGENT)[:16]

### 3. Implementation Details
```python
def get_user_id():
    # Check if user already has a session
    if 'user_id' in session:
        return session['user_id']
    
    # Create fingerprint-based identifier
    ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', ''))
    user_agent = request.headers.get('User-Agent', '')
    identifier_string = f"{ip_address}:{user_agent}"
    user_id = hashlib.md5(identifier_string.encode()).hexdigest()[:16]
    
    # Store in session
    session['user_id'] = user_id
    return user_id
```

## API Endpoints

### 1. Search Product (POST /api/search)
- Searches for a product and automatically saves to user's history
- Requires: `{"product_id": "XXXXXX"}`
- Returns: Product information with price, colors, sizes, etc.

### 2. Get Search History (GET /api/history)
- Retrieves user's search history
- Optional query parameter: `limit` (default: 50)
- Returns: Array of search history items with user_id for debugging

### 3. Clear Search History (DELETE /api/history)
- Clears all search history for the current user
- Returns: Success message

## Frontend Integration

### Session Support
- Frontend is configured to send credentials with requests
- `axios.defaults.withCredentials = true` ensures cookies are sent
- Each API call includes `withCredentials: true` option

### Data Structure
```typescript
interface SearchHistoryItem {
  product_id: string;
  product_name: string;
  price: string;
  colors: string[];
  sizes: string[];
  image_url: string;
  product_url: string;
  searched_at: string;
}
```

## Data Storage and Processing

### Product Information Extraction
The system extracts and stores:
- **Product ID**: Original search term
- **Price**: Formatted as "¥X,XXX"
- **Colors**: Unique colors available for the product
- **Sizes**: Only sizes that are currently in stock (stock: "IN_STOCK")
- **Product URL**: Direct link to Uniqlo Japan product page

### Stock Filtering
Only sizes with "IN_STOCK" status are saved to the history, ensuring users see relevant availability information.

## Privacy and Security

### User Privacy
- No personally identifiable information is stored
- User identification is based on browser fingerprinting
- Database files are excluded from version control (.gitignore)

### Data Persistence
- Database is stored in `data/search_history.db`
- Automatic database initialization on first run
- Graceful handling of database errors

## Deployment Considerations

### Docker Integration
- Database files are stored in a persistent `data/` directory
- Consider mounting volumes in production for data persistence
- Environment variables for configuration (Flask secret key)

### Production Recommendations
1. Use a more secure secret key in production
2. Consider using PostgreSQL or MySQL for high-traffic scenarios
3. Implement database backup strategies
4. Add rate limiting for API endpoints
5. Consider GDPR compliance for European users

## Testing the Integration

### Backend Testing
```bash
# Test search endpoint
curl -X POST -H "Content-Type: application/json" \
  -d '{"product_id": "474479"}' \
  -c cookies.txt http://localhost:5000/api/search

# Test history endpoint
curl -b cookies.txt http://localhost:5000/api/history

# Test clear history
curl -X DELETE -b cookies.txt http://localhost:5000/api/history
```

### Frontend Testing
1. Open http://localhost:5173
2. Search for multiple products
3. Verify search history appears in the table
4. Test clear history functionality
5. Refresh page to confirm persistence

## Configuration

### Environment Variables
- `FLASK_SECRET_KEY`: Secret key for Flask sessions (optional, has default)
- `LINE_CHANNEL_SECRET`: Line Bot configuration
- `LINE_CHANNEL_ACCESS_TOKEN`: Line Bot configuration

### Frontend Configuration
- `VITE_API_BASE_URL`: Backend API base URL (default: empty for same-origin)

## Troubleshooting

### Common Issues
1. **Sessions not persisting**: Ensure `withCredentials: true` in frontend
2. **Database not created**: Check write permissions in project directory
3. **Empty history**: Verify session cookies are being sent/received
4. **Stock filtering**: Products without available stock show empty sizes array

### Debug Information
- History API returns `user_id` for debugging user identification
- Flask debug mode shows detailed error messages
- Check browser network tab for cookie transmission
