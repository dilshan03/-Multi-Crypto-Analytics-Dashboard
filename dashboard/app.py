import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add scripts directory to path for imports
scripts_path = os.path.join(os.path.dirname(__file__), '..', 'scripts')
sys.path.insert(0, scripts_path)
from analytics import CryptoAnalytics

# Page configuration
st.set_page_config(
    page_title="Crypto Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .positive-change {
        color: #00ff00;
        font-weight: bold;
    }
    .negative-change {
        color: #ff0000;
        font-weight: bold;
    }
    .stSelectbox > div > div {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize analytics
analytics = CryptoAnalytics()

# Title and sidebar
st.title("🚀 Multi-Crypto Analytics Dashboard")
st.markdown("---")

# Sidebar for cryptocurrency selection
st.sidebar.header("📈 Dashboard Controls")

# Connect to database
@st.cache_data
def get_crypto_symbols():
    """Get list of available cryptocurrency symbols"""
    try:
        conn = sqlite3.connect("data/crypto.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT symbol FROM prices ORDER BY symbol")
        symbols = [row[0] for row in cursor.fetchall()]
        conn.close()
        return symbols
    except:
        return []

# Get available cryptocurrencies
available_symbols = get_crypto_symbols()

if not available_symbols:
    st.error("⚠️ No cryptocurrency data found. Please run the data collection scripts first.")
    st.info("Run: `python scripts/fetch_data.py` to collect initial data")
    st.stop()

# Cryptocurrency selection
selected_symbols = st.sidebar.multiselect(
    "Select Cryptocurrencies",
    options=available_symbols,
    default=available_symbols[:4] if len(available_symbols) >= 4 else available_symbols
)

if not selected_symbols:
    st.warning("Please select at least one cryptocurrency from the sidebar.")
    st.stop()

# Time period selection
time_periods = {
    "Last 24 Hours": 1,
    "Last 7 Days": 7,
    "Last 30 Days": 30,
    "Last 90 Days": 90
}

selected_period = st.sidebar.selectbox(
    "Time Period",
    options=list(time_periods.keys()),
    index=2
)

days = time_periods[selected_period]

# Main dashboard content
@st.cache_data
def get_latest_prices():
    """Get latest prices for selected cryptocurrencies"""
    conn = sqlite3.connect("data/crypto.db")
    
    placeholders = ','.join(['?' for _ in selected_symbols])
    query = f"""
    SELECT symbol, price_usd, timestamp, market_cap, volume_24h, price_change_24h
    FROM prices 
    WHERE symbol IN ({placeholders})
    AND id IN (
        SELECT MAX(id) 
        FROM prices 
        WHERE symbol IN ({placeholders})
        GROUP BY symbol
    )
    ORDER BY market_cap DESC
    """
    
    params = selected_symbols + selected_symbols
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df

@st.cache_data
def get_historical_data(symbols, days):
    """Get historical data for selected cryptocurrencies"""
    conn = sqlite3.connect("data/crypto.db")
    
    placeholders = ','.join(['?' for _ in symbols])
    query = f"""
    SELECT symbol, price_usd, timestamp, market_cap, volume_24h, price_change_24h
    FROM prices 
    WHERE symbol IN ({placeholders})
    AND datetime(timestamp) >= datetime('now', '-{days} days')
    ORDER BY timestamp ASC
    """
    
    df = pd.read_sql_query(query, conn, params=symbols)
    conn.close()
    
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df

# Get latest prices
latest_prices = get_latest_prices()

if latest_prices.empty:
    st.warning("No recent data available for selected cryptocurrencies.")
    st.stop()

# Display current prices in columns
st.subheader("💰 Current Prices & Market Data")

cols = st.columns(min(len(selected_symbols), 4))

for i, (_, row) in enumerate(latest_prices.iterrows()):
    col_idx = i % 4
    with cols[col_idx]:
        # Price change styling
        change_24h = row.get('price_change_24h', 0)
        change_class = "positive-change" if change_24h >= 0 else "negative-change"
        
        st.metric(
            label=f"{row['symbol']}",
            value=f"${row['price_usd']:,.2f}",
            delta=f"{change_24h:+.2f}%" if not pd.isna(change_24h) else None
        )
        
        # Additional metrics in expander
        with st.expander(f"{row['symbol']} Details"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Market Cap:** ${row.get('market_cap', 0):,.0f}")
            with col2:
                st.write(f"**Volume 24h:** ${row.get('volume_24h', 0):,.0f}")

st.markdown("---")

# Price charts
st.subheader("📈 Price Charts")

# Get historical data
historical_data = get_historical_data(selected_symbols, days)

if not historical_data.empty:
    # Price comparison chart
    fig_price = px.line(
        historical_data, 
        x='timestamp', 
        y='price_usd', 
        color='symbol',
        title=f"Cryptocurrency Prices - {selected_period}",
        labels={'price_usd': 'Price (USD)', 'timestamp': 'Time'}
    )
    
    fig_price.update_layout(
        height=500,
        showlegend=True,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_price, use_container_width=True)
    
    # Volume chart
    if 'volume_24h' in historical_data.columns:
        st.subheader("📊 Trading Volume")
        
        fig_volume = px.bar(
            historical_data, 
            x='timestamp', 
            y='volume_24h', 
            color='symbol',
            title=f"24h Trading Volume - {selected_period}",
            labels={'volume_24h': 'Volume (USD)', 'timestamp': 'Time'}
        )
        
        fig_volume.update_layout(
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig_volume, use_container_width=True)

# Analytics section
st.markdown("---")
st.subheader("📊 Technical Analytics")

# Get analytics for selected cryptocurrencies
for symbol in selected_symbols:
    with st.expander(f"Analytics for {symbol}"):
        try:
            symbol_analytics = analytics.generate_comprehensive_analytics(symbol)
            
            if symbol_analytics:
                # Create columns for different analytics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Moving Averages**")
                    for ma_name, ma_value in symbol_analytics.get('moving_averages', {}).items():
                        if ma_value:
                            st.write(f"{ma_name.replace('ma_', '').replace('d', ' day')}: ${ma_value:,.2f}")
                
                with col2:
                    st.write("**Price Changes**")
                    for change_name, change_value in symbol_analytics.get('percentage_changes', {}).items():
                        if change_value is not None:
                            period = change_name.replace('change_', '').replace('h', ' hour').replace('d', ' day')
                            st.write(f"{period}: {change_value:+.2f}%")
                
                with col3:
                    st.write("**Technical Indicators**")
                    if symbol_analytics.get('rsi_14'):
                        rsi = symbol_analytics['rsi_14']
                        rsi_status = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
                        st.write(f"RSI (14): {rsi:.1f} ({rsi_status})")
                    
                    if symbol_analytics.get('volatility_7d'):
                        st.write(f"Volatility (7d): {symbol_analytics['volatility_7d']:.2f}%")
                    
                    # Min/Max values
                    min_max_7d = symbol_analytics.get('min_max_7d', {})
                    if min_max_7d:
                        st.write(f"7d High: ${min_max_7d.get('max_price', 0):,.2f}")
                        st.write(f"7d Low: ${min_max_7d.get('min_price', 0):,.2f}")
            
            else:
                st.write("No analytics data available yet.")
                
        except Exception as e:
            st.error(f"Error loading analytics for {symbol}: {e}")

# Market overview
st.markdown("---")
st.subheader("🌍 Market Overview")

if not latest_prices.empty:
    # Market cap pie chart
    market_cap_data = latest_prices[latest_prices['market_cap'].notna()]
    
    if not market_cap_data.empty:
        fig_pie = px.pie(
            market_cap_data, 
            values='market_cap', 
            names='symbol',
            title="Market Cap Distribution"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Summary statistics
            st.write("**Market Summary**")
            total_market_cap = market_cap_data['market_cap'].sum()
            st.write(f"Total Market Cap: ${total_market_cap:,.0f}")
            
            st.write("**Top Performers (24h)**")
            top_performers = latest_prices.nlargest(3, 'price_change_24h')[['symbol', 'price_change_24h']]
            for _, row in top_performers.iterrows():
                st.write(f"{row['symbol']}: {row['price_change_24h']:+.2f}%")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>📊 Crypto Dashboard | Data updates every 5 minutes | Built with Streamlit & Plotly</p>
    </div>
    """, 
    unsafe_allow_html=True
)

#streamlit run dashboard/app.py