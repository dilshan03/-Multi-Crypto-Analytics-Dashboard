import requests
import sqlite3
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/fetch_log.log'),
        logging.StreamHandler()
    ]
)

# Supported cryptocurrencies
CRYPTOCURRENCIES = {
    'bitcoin': 'BTC',
    'ethereum': 'ETH', 
    'cardano': 'ADA',
    'solana': 'SOL',
    'polkadot': 'DOT',
    'chainlink': 'LINK',
    'litecoin': 'LTC',
    'bitcoin-cash': 'BCH'
}

def create_database_schema():
    """Create database tables with enhanced schema"""
    conn = sqlite3.connect("data/crypto.db")
    cursor = conn.cursor()
    
    # Check if old schema exists and migrate if needed
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='prices'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        # Check if we have the old schema (with 'rate' column)
        cursor.execute("PRAGMA table_info(prices)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'rate' in columns and 'symbol' not in columns:
            logging.info("Migrating from old schema to new schema")
            # Backup old data
            cursor.execute("SELECT * FROM prices")
            old_data = cursor.fetchall()
            
            # Drop old table
            cursor.execute("DROP TABLE prices")
            
            # Create new table with enhanced schema
            cursor.execute("""
                CREATE TABLE prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    name TEXT NOT NULL,
                    price_usd REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    market_cap REAL,
                    volume_24h REAL,
                    price_change_24h REAL
                )
            """)
            
            # Migrate old data (assuming it's Bitcoin data)
            for row in old_data:
                cursor.execute("""
                    INSERT INTO prices (symbol, name, price_usd, timestamp, market_cap, volume_24h, price_change_24h)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ('BTC', 'bitcoin', row[2], row[3], None, None, None))
            
            logging.info(f"Migrated {len(old_data)} records from old schema")
    
    else:
        # Create new table with enhanced schema
        cursor.execute("""
            CREATE TABLE prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                name TEXT NOT NULL,
                price_usd REAL NOT NULL,
                timestamp TEXT NOT NULL,
                market_cap REAL,
                volume_24h REAL,
                price_change_24h REAL
            )
        """)
    
    # Analytics table for computed metrics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            time_period TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            UNIQUE(symbol, metric_name, time_period, timestamp)
        )
    """)
    
    # Create indexes for better performance (only if columns exist)
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_symbol_time ON prices(symbol, timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_symbol_metric ON analytics(symbol, metric_name)")
    except sqlite3.OperationalError as e:
        logging.warning(f"Could not create indexes: {e}")
    
    conn.commit()
    conn.close()
    logging.info("Database schema created/updated successfully")

def fetch_crypto_data():
    """Fetch data for all supported cryptocurrencies"""
    try:
        # Build API URL for multiple cryptocurrencies
        crypto_ids = ','.join(CRYPTOCURRENCIES.keys())
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_ids}&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true"
        
        logging.info(f"Fetching data for {len(CRYPTOCURRENCIES)} cryptocurrencies")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data
        
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error during data fetch: {e}")
        return None

def store_crypto_data(data):
    """Store cryptocurrency data in database"""
    if not data:
        logging.warning("No data to store")
        return False
        
    conn = sqlite3.connect("data/crypto.db")
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stored_count = 0
    
    try:
        for coin_id, coin_data in data.items():
            if 'usd' in coin_data:
                symbol = CRYPTOCURRENCIES.get(coin_id, coin_id.upper())
                price = coin_data['usd']
                market_cap = coin_data.get('usd_market_cap')
                volume_24h = coin_data.get('usd_24h_vol')
                price_change_24h = coin_data.get('usd_24h_change')
                
                cursor.execute("""
                    INSERT INTO prices (symbol, name, price_usd, timestamp, market_cap, volume_24h, price_change_24h)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (symbol, coin_id, price, timestamp, market_cap, volume_24h, price_change_24h))
                
                stored_count += 1
                logging.info(f"Stored data for {symbol}: ${price:,.2f}")
        
        conn.commit()
        logging.info(f"Successfully stored data for {stored_count} cryptocurrencies")
        return True
        
    except Exception as e:
        logging.error(f"Error storing data: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def fetch_and_store():
    """Main function to fetch and store cryptocurrency data"""
    logging.info("Starting cryptocurrency data fetch")
    
    # Ensure database schema exists
    create_database_schema()
    
    # Fetch data from API
    data = fetch_crypto_data()
    
    # Store data in database
    success = store_crypto_data(data)
    
    if success:
        logging.info("Data collection completed successfully")
    else:
        logging.error("Data collection failed")
    
    return success

if __name__ == "__main__":
    fetch_and_store()

#python scripts/fetch_data.py