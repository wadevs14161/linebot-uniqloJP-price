# Database Setup for UNIQLO Price Finder

This document explains how to set up and use the Cloud SQL PostgreSQL database for the UNIQLO Price Finder application.

## Overview

The application uses **Google Cloud SQL PostgreSQL** for production and falls back to **SQLite** for local development or when Cloud SQL is not available.

## Database Schema

### Tables

1. **search_history** - Stores all product searches
   - `id` - Primary key
   - `product_id` - UNIQLO product ID
   - `serial_number` - Product serial number
   - `search_timestamp` - When the search occurred
   - `jp_price` - Price in Japanese Yen
   - `jp_price_in_twd` - Price converted to TWD
   - `tw_prices` - Taiwan prices (JSON array)
   - `product_data` - Full product information (JSON)
   - `product_url` - UNIQLO product URL
   - `search_source` - Source: 'api', 'linebot', 'web', 'api_cached'
   - `user_id` - User identifier
   - `is_successful` - Whether search was successful
   - `error_message` - Error details if search failed

2. **price_cache** - Caches recent price data
   - `id` - Primary key
   - `product_id` - UNIQLO product ID (unique)
   - `serial_number` - Product serial number
   - `cached_data` - Full response data (JSON)
   - `cache_timestamp` - When data was cached
   - `expiry_timestamp` - When cache expires
   - `access_count` - Number of times accessed
   - `last_accessed` - Last access time

3. **system_config** - System configuration
   - `id` - Primary key
   - `config_key` - Configuration key (unique)
   - `config_value` - Configuration value
   - `config_type` - Value type: 'string', 'int', 'float', 'json', 'bool'
   - `description` - Configuration description
   - `created_at` - Creation timestamp
   - `updated_at` - Last update timestamp

## Setup Instructions

### 1. Create Cloud SQL Database

Run the database setup script:

```bash
./scripts/cloud/setup-database.sh
```

This script will:
- Create a Cloud SQL PostgreSQL instance (db-f1-micro tier)
- Create the application database
- Create database user with credentials
- Generate `.env.database` file with connection details

### 2. Local Development Setup

For local development with Cloud SQL:

1. Install Cloud SQL Proxy:
   ```bash
   gcloud components install cloud_sql_proxy
   ```

2. Start Cloud SQL Proxy:
   ```bash
   cloud_sql_proxy -instances=YOUR_CONNECTION_NAME=tcp:5432
   ```

3. Your application will automatically connect using the settings in `.env.database`

### 3. Production Deployment

When deploying to Cloud Run, the deployment script will:
- Read database configuration from `.env.database`
- Set up Cloud SQL connection for Cloud Run
- Configure environment variables automatically

## Features

### Caching System
- **Cache Duration**: 1 hour for API searches
- **Cache Strategy**: Product ID based
- **Benefits**: Reduces API calls and improves response time

### Analytics
- **Search History**: All searches are logged
- **Success Tracking**: Failed searches are recorded with error messages
- **Usage Statistics**: Access counts and patterns
- **Popular Products**: Most searched items tracking

### API Endpoints

#### New Database-Related Endpoints:

1. **GET /api/stats** - Get database statistics
   ```json
   {
     "total_searches": 1250,
     "successful_searches": 1180,
     "success_rate": 94.4,
     "recent_searches_24h": 45,
     "popular_products": [
       {"product_id": "474479", "search_count": 23},
       {"product_id": "455942", "search_count": 18}
     ]
   }
   ```

2. **GET /api/history** - Get user search history (enhanced)
   - Now includes more detailed product information
   - Faster queries with proper indexing

3. **DELETE /api/history** - Clear user search history
   - Uses database manager for proper cleanup

## Cost Optimization

### Database Costs (Monthly Estimates)
- **Cloud SQL Instance**: ~$7-10/month (db-f1-micro)
- **Storage**: ~$1.70/month (10GB SSD)
- **Total**: ~$8-12/month

### Optimization Features
- **Connection Pooling**: Reduces connection overhead
- **Automatic Fallback**: Uses SQLite if Cloud SQL unavailable
- **Smart Caching**: Reduces database queries
- **Efficient Indexing**: Optimized query performance

## Maintenance

### Regular Tasks
1. **Monitor Storage**: Database will auto-increase storage as needed
2. **Review Logs**: Check Cloud SQL logs for performance issues
3. **Cache Cleanup**: Old cache entries are automatically handled
4. **Backup Review**: Daily backups are configured automatically

### Scaling Considerations
- Current setup handles ~1000 searches/day comfortably
- For higher volume, consider upgrading to db-g1-small
- Add read replicas if needed for geographic distribution

## Security

### Database Security
- **Private IP**: Database not directly accessible from internet
- **IAM Integration**: Uses Google Cloud IAM for access control
- **Encryption**: Data encrypted at rest and in transit
- **Backup Encryption**: Automated backups are encrypted

### Application Security
- **Connection String**: Stored securely in environment variables
- **No SQL Injection**: Uses SQLAlchemy ORM with parameterized queries
- **User Isolation**: User data isolated by user_id

## Troubleshooting

### Common Issues

1. **Connection Timeout**
   ```
   Solution: Check Cloud SQL instance status and firewall rules
   ```

2. **Authentication Failed**
   ```
   Solution: Verify DATABASE_URL and Cloud SQL IAM permissions
   ```

3. **SQLite Fallback Active**
   ```
   Solution: Check .env.database file and Cloud SQL connectivity
   ```

### Debug Commands

```bash
# Check Cloud SQL instance status
gcloud sql instances describe uniqlo-db

# View Cloud SQL logs
gcloud sql operations list --instance=uniqlo-db

# Test database connection
cloud_sql_proxy -instances=CONNECTION_NAME=tcp:5432 &
psql "host=127.0.0.1 port=5432 dbname=uniqlo_price_finder user=uniqlo_user"
```

## Migration from SQLite

If you have existing SQLite data, you can migrate it:

1. Export SQLite data:
   ```python
   # Custom migration script needed - contact developer
   ```

2. Import to PostgreSQL:
   ```sql
   -- Manual SQL import process
   ```

## Monitoring

### Key Metrics to Monitor
- **Search Success Rate**: Should be >95%
- **Cache Hit Rate**: Should be >30% during peak usage
- **Database Connections**: Should stay within pool limits
- **Query Performance**: Average query time <100ms

### Alerting
Set up alerts for:
- Database connection failures
- High error rates in search_history
- Cache expiry issues
- Storage approaching limits
