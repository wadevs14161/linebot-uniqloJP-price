"""
Database models and connection for UNIQLO Price Finder
"""
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import JSON
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('.env.database')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class SearchHistory(Base):
    """Store search history for analytics and caching"""
    __tablename__ = 'search_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(50), nullable=False, index=True)
    serial_number = Column(String(50), nullable=True, index=True)
    search_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    jp_price = Column(Integer, nullable=True)
    jp_price_in_twd = Column(Integer, nullable=True)
    tw_prices = Column(JSON, nullable=True)  # Store as JSON array
    product_data = Column(JSON, nullable=True)  # Store full product response
    product_url = Column(Text, nullable=True)
    search_source = Column(String(20), default='api', nullable=False)  # 'api', 'linebot', 'web'
    user_id = Column(String(100), nullable=True)  # Line user ID if from Line Bot
    is_successful = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)

class PriceCache(Base):
    """Cache recent price data to reduce API calls"""
    __tablename__ = 'price_cache'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(50), nullable=False, unique=True, index=True)
    serial_number = Column(String(50), nullable=True)
    cached_data = Column(JSON, nullable=False)  # Full response data
    cache_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    expiry_timestamp = Column(DateTime, nullable=False)  # When cache expires
    access_count = Column(Integer, default=1, nullable=False)
    last_accessed = Column(DateTime, default=datetime.utcnow, nullable=False)

class SystemConfig(Base):
    """Store system configuration and settings"""
    __tablename__ = 'system_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(100), nullable=False, unique=True, index=True)
    config_value = Column(Text, nullable=True)
    config_type = Column(String(20), default='string', nullable=False)  # 'string', 'int', 'float', 'json', 'bool'
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._setup_database()
    
    def _setup_database(self):
        """Initialize database connection"""
        try:
            # Try to get DATABASE_URL first (for Cloud Run)
            database_url = os.getenv('DATABASE_URL')
            
            if not database_url:
                # Fallback to individual components (for local development)
                db_host = os.getenv('DB_HOST', 'localhost')
                db_port = os.getenv('DB_PORT', '5432')
                db_name = os.getenv('DB_NAME', 'uniqlo_price_finder')
                db_user = os.getenv('DB_USER', 'uniqlo_user')
                db_password = os.getenv('DB_PASSWORD', '')
                
                if not db_password:
                    logger.warning("No database password found. Using SQLite fallback.")
                    database_url = 'sqlite:///data/uniqlo_price_finder.db'
                else:
                    database_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
            
            logger.info(f"Connecting to database: {database_url.split('@')[0]}@***")
            
            # Create engine with connection pooling
            if database_url.startswith('postgresql'):
                self.engine = create_engine(
                    database_url,
                    pool_size=int(os.getenv('DB_POOL_SIZE', '5')),
                    max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '10')),
                    pool_pre_ping=True,
                    echo=False  # Set to True for SQL debugging
                )
            else:
                # SQLite fallback
                os.makedirs('data', exist_ok=True)
                self.engine = create_engine(database_url, echo=False)
            
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database connection established successfully")
            
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            # Fallback to SQLite
            logger.info("Falling back to SQLite database")
            os.makedirs('data', exist_ok=True)
            self.engine = create_engine('sqlite:///data/uniqlo_price_finder.db', echo=False)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    def save_search_history(self, product_id: str, search_data: Dict[str, Any], 
                          source: str = 'api', user_id: Optional[str] = None,
                          is_successful: bool = True, error_message: Optional[str] = None):
        """Save search history to database"""
        try:
            with self.get_session() as session:
                history = SearchHistory(
                    product_id=product_id,
                    serial_number=search_data.get('serial_number'),
                    jp_price=search_data.get('price_jp'),
                    jp_price_in_twd=search_data.get('jp_price_in_twd'),
                    tw_prices=search_data.get('price_tw', []),
                    product_data=search_data,
                    product_url=search_data.get('product_url'),
                    search_source=source,
                    user_id=user_id,
                    is_successful=is_successful,
                    error_message=error_message
                )
                session.add(history)
                session.commit()
                logger.info(f"Search history saved for product {product_id}")
        except Exception as e:
            logger.error(f"Failed to save search history: {e}")
    
    def get_cached_price(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get cached price data if still valid"""
        try:
            with self.get_session() as session:
                cache = session.query(PriceCache).filter(
                    PriceCache.product_id == product_id,
                    PriceCache.expiry_timestamp > datetime.utcnow()
                ).first()
                
                if cache:
                    # Update access statistics
                    cache.access_count += 1
                    cache.last_accessed = datetime.utcnow()
                    session.commit()
                    logger.info(f"Cache hit for product {product_id}")
                    return cache.cached_data
                
                return None
        except Exception as e:
            logger.error(f"Failed to get cached price: {e}")
            return None
    
    def cache_price_data(self, product_id: str, data: Dict[str, Any], cache_hours: int = 1):
        """Cache price data for specified hours"""
        try:
            from datetime import timedelta
            
            with self.get_session() as session:
                expiry = datetime.utcnow() + timedelta(hours=cache_hours)
                
                # Update existing cache or create new
                cache = session.query(PriceCache).filter(PriceCache.product_id == product_id).first()
                
                if cache:
                    cache.cached_data = data
                    cache.cache_timestamp = datetime.utcnow()
                    cache.expiry_timestamp = expiry
                    cache.access_count += 1
                    cache.last_accessed = datetime.utcnow()
                else:
                    cache = PriceCache(
                        product_id=product_id,
                        serial_number=data.get('serial_number'),
                        cached_data=data,
                        expiry_timestamp=expiry
                    )
                    session.add(cache)
                
                session.commit()
                logger.info(f"Price data cached for product {product_id} (expires in {cache_hours}h)")
        except Exception as e:
            logger.error(f"Failed to cache price data: {e}")
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search statistics"""
        try:
            with self.get_session() as session:
                total_searches = session.query(SearchHistory).count()
                successful_searches = session.query(SearchHistory).filter(SearchHistory.is_successful == True).count()
                
                # Recent searches (last 24 hours)
                from datetime import timedelta
                recent_cutoff = datetime.utcnow() - timedelta(hours=24)
                recent_searches = session.query(SearchHistory).filter(
                    SearchHistory.search_timestamp > recent_cutoff
                ).count()
                
                # Popular products (top 10 most searched)
                from sqlalchemy import func
                popular_products = session.query(
                    SearchHistory.product_id,
                    func.count(SearchHistory.id).label('search_count')
                ).filter(SearchHistory.is_successful == True)\
                .group_by(SearchHistory.product_id)\
                .order_by(func.count(SearchHistory.id).desc())\
                .limit(10).all()
                
                return {
                    'total_searches': total_searches,
                    'successful_searches': successful_searches,
                    'success_rate': round(successful_searches / max(total_searches, 1) * 100, 2),
                    'recent_searches_24h': recent_searches,
                    'popular_products': [
                        {'product_id': p.product_id, 'search_count': p.search_count}
                        for p in popular_products
                    ]
                }
        except Exception as e:
            logger.error(f"Failed to get search stats: {e}")
            return {}

# Global database manager instance
db_manager = DatabaseManager()

def get_db_session() -> Session:
    """Get database session - convenience function"""
    return db_manager.get_session()
