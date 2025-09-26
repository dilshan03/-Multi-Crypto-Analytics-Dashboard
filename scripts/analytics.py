import sqlite3
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoAnalytics:
    def __init__(self, db_path="data/crypto.db"):
        self.db_path = db_path
    
    def get_price_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Get historical price data for a specific cryptocurrency"""
        conn = sqlite3.connect(self.db_path)
        
        query = """
        SELECT symbol, price_usd, timestamp, market_cap, volume_24h, price_change_24h
        FROM prices 
        WHERE symbol = ? 
        AND datetime(timestamp) >= datetime('now', '-{} days')
        ORDER BY timestamp ASC
        """.format(days)
        
        df = pd.read_sql_query(query, conn, params=(symbol,))
        conn.close()
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
        
        return df
    
    def calculate_moving_averages(self, df: pd.DataFrame, windows: List[int] = [7, 30]) -> Dict[str, float]:
        """Calculate moving averages for different time windows"""
        if df.empty:
            return {}
        
        ma_results = {}
        for window in windows:
            if len(df) >= window:
                ma_value = df['price_usd'].rolling(window=window).mean().iloc[-1]
                ma_results[f'ma_{window}d'] = round(ma_value, 2)
            else:
                ma_results[f'ma_{window}d'] = None
        
        return ma_results
    
    def calculate_percentage_changes(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate percentage changes over different time periods"""
        if df.empty:
            return {}
        
        current_price = df['price_usd'].iloc[-1]
        changes = {}
        
        # 1 hour change
        hour_ago = datetime.now() - timedelta(hours=1)
        hour_data = df[df.index >= hour_ago]
        if len(hour_data) >= 2:
            hour_price = hour_data['price_usd'].iloc[0]
            changes['change_1h'] = round(((current_price - hour_price) / hour_price) * 100, 2)
        else:
            changes['change_1h'] = None
        
        # 24 hour change
        day_ago = datetime.now() - timedelta(days=1)
        day_data = df[df.index >= day_ago]
        if len(day_data) >= 2:
            day_price = day_data['price_usd'].iloc[0]
            changes['change_24h'] = round(((current_price - day_price) / day_price) * 100, 2)
        else:
            changes['change_24h'] = None
        
        # 7 day change
        week_ago = datetime.now() - timedelta(days=7)
        week_data = df[df.index >= week_ago]
        if len(week_data) >= 2:
            week_price = week_data['price_usd'].iloc[0]
            changes['change_7d'] = round(((current_price - week_price) / week_price) * 100, 2)
        else:
            changes['change_7d'] = None
        
        # 30 day change
        month_ago = datetime.now() - timedelta(days=30)
        month_data = df[df.index >= month_ago]
        if len(month_data) >= 2:
            month_price = month_data['price_usd'].iloc[0]
            changes['change_30d'] = round(((current_price - month_price) / month_price) * 100, 2)
        else:
            changes['change_30d'] = None
        
        return changes
    
    def calculate_volatility(self, df: pd.DataFrame, days: int = 7) -> float:
        """Calculate price volatility (standard deviation of returns)"""
        if len(df) < 2:
            return 0.0
        
        # Calculate daily returns
        returns = df['price_usd'].pct_change().dropna()
        
        # Calculate volatility (standard deviation of returns)
        volatility = returns.std() * np.sqrt(24)  # Annualized volatility
        return round(volatility * 100, 2)  # Return as percentage
    
    def get_min_max_values(self, df: pd.DataFrame, days: int = 7) -> Dict[str, float]:
        """Get minimum and maximum values for a given period"""
        if df.empty:
            return {}
        
        period_data = df[df.index >= datetime.now() - timedelta(days=days)]
        
        if period_data.empty:
            return {}
        
        return {
            'min_price': round(period_data['price_usd'].min(), 2),
            'max_price': round(period_data['price_usd'].max(), 2),
            'min_time': period_data['price_usd'].idxmin().strftime('%Y-%m-%d %H:%M'),
            'max_time': period_data['price_usd'].idxmax().strftime('%Y-%m-%d %H:%M')
        }
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Relative Strength Index (RSI)"""
        if len(df) < period + 1:
            return None
        
        prices = df['price_usd']
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi.iloc[-1], 2) if not pd.isna(rsi.iloc[-1]) else None
    
    def generate_comprehensive_analytics(self, symbol: str) -> Dict:
        """Generate comprehensive analytics for a cryptocurrency"""
        logger.info(f"Generating analytics for {symbol}")
        
        # Get 30 days of data for comprehensive analysis
        df = self.get_price_data(symbol, days=30)
        
        if df.empty:
            logger.warning(f"No data available for {symbol}")
            return {}
        
        current_price = df['price_usd'].iloc[-1]
        
        analytics = {
            'symbol': symbol,
            'current_price': round(current_price, 2),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'moving_averages': self.calculate_moving_averages(df),
            'percentage_changes': self.calculate_percentage_changes(df),
            'volatility_7d': self.calculate_volatility(df, days=7),
            'volatility_30d': self.calculate_volatility(df, days=30),
            'min_max_7d': self.get_min_max_values(df, days=7),
            'min_max_30d': self.get_min_max_values(df, days=30),
            'rsi_14': self.calculate_rsi(df),
            'data_points': len(df),
            'latest_market_cap': df['market_cap'].iloc[-1] if 'market_cap' in df.columns else None,
            'latest_volume_24h': df['volume_24h'].iloc[-1] if 'volume_24h' in df.columns else None
        }
        
        return analytics
    
    def store_analytics(self, analytics: Dict):
        """Store computed analytics in the database"""
        if not analytics:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        symbol = analytics['symbol']
        timestamp = analytics['timestamp']
        
        try:
            # Store moving averages
            for metric_name, value in analytics['moving_averages'].items():
                if value is not None:
                    cursor.execute("""
                        INSERT OR REPLACE INTO analytics 
                        (symbol, metric_name, metric_value, time_period, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    """, (symbol, metric_name, value, '30d', timestamp))
            
            # Store percentage changes
            for metric_name, value in analytics['percentage_changes'].items():
                if value is not None:
                    cursor.execute("""
                        INSERT OR REPLACE INTO analytics 
                        (symbol, metric_name, metric_value, time_period, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    """, (symbol, metric_name, value, 'current', timestamp))
            
            # Store volatility metrics
            if analytics.get('volatility_7d') is not None:
                cursor.execute("""
                    INSERT OR REPLACE INTO analytics 
                    (symbol, metric_name, metric_value, time_period, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (symbol, 'volatility', analytics['volatility_7d'], '7d', timestamp))
            
            # Store RSI
            if analytics.get('rsi_14') is not None:
                cursor.execute("""
                    INSERT OR REPLACE INTO analytics 
                    (symbol, metric_name, metric_value, time_period, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (symbol, 'rsi', analytics['rsi_14'], '14d', timestamp))
            
            conn.commit()
            logger.info(f"Analytics stored for {symbol}")
            
        except Exception as e:
            logger.error(f"Error storing analytics for {symbol}: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_all_symbols(self) -> List[str]:
        """Get list of all cryptocurrency symbols in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT symbol FROM prices ORDER BY symbol")
        symbols = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return symbols
    
    def update_all_analytics(self):
        """Update analytics for all cryptocurrencies in the database"""
        symbols = self.get_all_symbols()
        logger.info(f"Updating analytics for {len(symbols)} cryptocurrencies")
        
        for symbol in symbols:
            try:
                analytics = self.generate_comprehensive_analytics(symbol)
                self.store_analytics(analytics)
            except Exception as e:
                logger.error(f"Error updating analytics for {symbol}: {e}")

if __name__ == "__main__":
    analytics = CryptoAnalytics()
    analytics.update_all_analytics()
    print("Analytics update completed!")
