import os
import sys
import hashlib
from flask import (Flask, render_template, request, abort, jsonify, session, send_from_directory, send_file)
from flask_cors import CORS
from linebot.v3 import (
    WebhookParser,
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage
)

from crawl import product_crawl
from database import db_manager
from reply import reply_message


app = Flask(__name__)
# Configure CORS for production deployment
cors_origins = ["*"]  # In production, specify your actual frontend domain
CORS(app, supports_credentials=True, origins=cors_origins)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'uniqlo-price-finder-secret-key-2024')

# Ensure proper JSON encoding for Japanese characters
app.config['JSON_AS_ASCII'] = False

# Database initialization
def init_db():
    """Initialize the database - now handled by DatabaseManager"""
    # Database initialization is now handled by the DatabaseManager
    # This function is kept for compatibility but does nothing
    pass

def get_user_id():
    """Get or create a unique user identifier"""
    # Check if user already has a session
    if 'user_id' in session:
        return session['user_id']
    
    # Create a new user identifier using IP + User Agent hash
    ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', ''))
    user_agent = request.headers.get('User-Agent', '')
    
    # Create a hash-based identifier
    identifier_string = f"{ip_address}:{user_agent}"
    user_id = hashlib.md5(identifier_string.encode()).hexdigest()[:16]
    
    # Store in session
    session['user_id'] = user_id
    
    # User management is now handled by the database manager
    # No need to manually store user info
    
    return user_id

def save_search_to_history(user_id, product_id, result):
    """Save search result to user's history using the new database manager"""
    if result == -1 or not result:
        db_manager.save_search_history(
            product_id=product_id,
            search_data={},
            source='web',
            user_id=user_id,
            is_successful=False,
            error_message="Search failed"
        )
        return
    
    # Save successful search to database
    db_manager.save_search_history(
        product_id=product_id,
        search_data=result,
        source='web',
        user_id=user_id,
        is_successful=True
    )

def get_user_search_history(user_id, limit=50):
    """Get user's search history using the new database manager"""
    try:
        with db_manager.get_session() as session:
            from database import SearchHistory
            
            # Get recent searches for this user
            searches = session.query(SearchHistory).filter(
                SearchHistory.user_id == user_id,
                SearchHistory.is_successful == True
            ).order_by(SearchHistory.search_timestamp.desc()).limit(limit).all()
            
            history = []
            for search in searches:
                # Extract data from stored JSON
                data = search.product_data or {}
                colors = []
                sizes = []
                
                if data.get('product_list'):
                    colors = list(set([item['color'] for item in data['product_list'] if item.get('color')]))
                    sizes = []
                    for item in data['product_list']:
                        if item.get('size') and item.get('stock') == 'IN_STOCK':
                            sizes.append(item['size'])
                    sizes = list(set(sizes))
                
                # Extract page title from stored JSON data
                page_title = data.get('page_title', '')
                
                history.append({
                    'product_id': search.product_id,
                    'product_name': page_title,  # Use the scraped page title
                    'price': f"¥{search.jp_price:,}" if search.jp_price else '',
                    'colors': colors,
                    'sizes': sizes,
                    'image_url': '',  # Not available
                    'product_url': search.product_url or '',
                    'searched_at': search.search_timestamp.isoformat()
                })
            
            return history
    except Exception as e:
        print(f"Error getting search history: {e}")
        return []

# Initialize database on startup
init_db()

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

parser = WebhookParser(channel_secret)
handler = WebhookHandler(channel_secret)

configuration = Configuration(
    access_token=channel_access_token
)


@app.route('/', methods=['GET', 'POST'])
def index():
    return '''
    <html>
        <head>
            <title>Uniqlo Japan Price Finder</title>
            <style>
                body {
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .container {
                    text-align: center;
                    background: rgba(255, 255, 255, 0.1);
                    padding: 2rem;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
                }
                h1 {
                    font-size: 3em;
                    margin-bottom: 1rem;
                }
                .subtitle {
                    font-size: 1.2em;
                    margin-bottom: 2rem;
                    opacity: 0.9;
                }
                .button {
                    display: inline-block;
                    padding: 15px 30px;
                    margin: 10px;
                    background: rgba(255, 255, 255, 0.2);
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-radius: 10px;
                    color: white;
                    text-decoration: none;
                    font-size: 1.1em;
                    transition: all 0.3s ease;
                }
                .button:hover {
                    background: rgba(255, 255, 255, 0.3);
                    transform: translateY(-2px);
                }
                .flag {
                    font-size: 2em;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>UNIQLO 日本 找價格</h1>
                <p class="subtitle">Line Bot Server & Web Interface</p>
                <div>
                    <a href="/frontend" class="button" target="_blank">
                        🌐 Open Web Interface
                    </a>
                    <div style="margin-top: 1rem; font-size: 0.9em; opacity: 0.8;">
                        <p>Backend API: REST endpoints for product search</p>
                        <p>Line Bot: Webhook endpoint for Line messaging</p>
                        <p>Frontend: Available at /frontend (if served)</p>
                    </div>
                </div>
            </div>
        </body>
    </html>
    '''



@app.route("/find_product", methods=['POST'])
def find_product():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    message_input = event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if message_input == "1":
            print("User ask for example!")
            img_url = "https://i.imgur.com/HLw9BhO.jpg"
            reply = ImageMessage(original_content_url=img_url, preview_image_url=img_url)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                replyToken=event.reply_token,
                messages=[reply]))
        else:
            print("Start crawling!")
            result = product_crawl(message_input)
            reply_message(result, event, line_bot_api)
                    
    return 'OK'

@app.route("/api/search", methods=['POST'])
def api_search():
    """API endpoint for product search from React frontend with caching"""
    try:
        data = request.get_json()
        product_id = data.get('product_id', '').strip()
        
        if not product_id:
            return jsonify({'error': 'Product ID is required'}), 400
        
        # Get user identifier
        user_id = get_user_id()
        
        print(f"API Search for product ID: {product_id} by user: {user_id}")
        
        # Try to get cached data first
        cached_result = db_manager.get_cached_price(product_id)
        if cached_result:
            print(f"Using cached data for product {product_id}")
            # Save cache hit to history
            db_manager.save_search_history(
                product_id=product_id,
                search_data=cached_result,
                source='api_cached',
                user_id=user_id,
                is_successful=True
            )
            return jsonify(cached_result)
        
        # No cache, fetch fresh data
        result = product_crawl(product_id)
        
        if result == -1:
            # Save failed search
            db_manager.save_search_history(
                product_id=product_id,
                search_data={},
                source='api',
                user_id=user_id,
                is_successful=False,
                error_message="Product not found"
            )
            return jsonify({'error': 'Product not found'}), 404
        
        # Cache the successful result (1 hour cache)
        db_manager.cache_price_data(product_id, result, cache_hours=1)
        
        # Save successful search to history
        save_search_to_history(user_id, product_id, result)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"API Error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route("/api/history", methods=['GET'])
def api_get_history():
    """API endpoint to get user's search history"""
    try:
        user_id = get_user_id()
        limit = request.args.get('limit', 50, type=int)
        
        history = get_user_search_history(user_id, limit)
        
        return jsonify({
            'history': history,
            'user_id': user_id  # For debugging purposes
        })
        
    except Exception as e:
        print(f"History API Error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route("/api/history", methods=['DELETE'])
def api_clear_history():
    """API endpoint to clear user's search history"""
    try:
        user_id = get_user_id()
        
        # Clear search history using database manager
        with db_manager.get_session() as session:
            from database import SearchHistory
            session.query(SearchHistory).filter(SearchHistory.user_id == user_id).delete()
            session.commit()
        
        return jsonify({'message': 'Search history cleared successfully'})
        
    except Exception as e:
        print(f"Clear History API Error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route("/api/stats", methods=['GET'])
def api_get_stats():
    """API endpoint to get database statistics"""
    try:
        stats = db_manager.get_search_stats()
        return jsonify(stats)
    except Exception as e:
        print(f"Stats API Error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Frontend routes - serve React app
@app.route('/frontend')
@app.route('/frontend/')
def frontend_home():
    """Serve the React frontend index.html"""
    try:
        return send_file('static/frontend/index.html')
    except FileNotFoundError:
        return jsonify({'error': 'Frontend not built. Please build the React app first.'}), 404

@app.route('/frontend/<path:filename>')
def frontend_assets(filename):
    """Serve React frontend static assets"""
    try:
        return send_from_directory('static/frontend', filename)
    except FileNotFoundError:
        # If file not found, serve index.html for client-side routing
        return send_file('static/frontend/index.html')


if __name__ == '__main__':
    # Get port from environment variable (Cloud Run sets PORT automatically)
    port = int(os.getenv('PORT', 5000))
    # Cloud Run expects the app to bind to 0.0.0.0
    app.run(debug=False, host='0.0.0.0', port=port)
