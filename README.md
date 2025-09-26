# 🚀 Multi-Crypto Analytics Dashboard

A comprehensive cryptocurrency tracking and analytics dashboard that monitors multiple cryptocurrencies, performs technical analysis, and provides real-time market insights.

## ✨ Features

### 🔥 Core Functionality
- **Multi-Cryptocurrency Support**: Track 8+ major cryptocurrencies (BTC, ETH, ADA, SOL, DOT, LINK, LTC, BCH)
- **Real-time Data Collection**: Automated data fetching every 1-5 minutes
- **Historical Data Storage**: Time-series database with comprehensive price history
- **Advanced Analytics**: Moving averages, RSI, volatility, percentage changes
- **Interactive Dashboard**: Beautiful web interface with Plotly charts

### 📊 Analytics & Metrics
- **Moving Averages**: 7-day and 30-day moving averages
- **Price Changes**: 1-hour, 24-hour, 7-day, and 30-day percentage changes
- **Technical Indicators**: RSI (14-day), volatility calculations
- **Market Data**: Market cap, 24h volume, min/max values
- **Visualizations**: Interactive price charts, volume analysis, market cap distribution

### 🛠️ Automation & Monitoring
- **Automated Scheduling**: Configurable data collection intervals
- **Error Handling**: Robust retry logic and failure monitoring
- **Comprehensive Logging**: Detailed logs for API requests and data collection
- **Database Optimization**: Indexed tables for fast queries

## 🏗️ Project Structure

```
api-dashboard-project/
├── dashboard/
│   └── app.py                 # Streamlit web dashboard
├── data/
│   ├── crypto.db             # SQLite database
│   ├── fetch_log.log         # Data collection logs
│   └── scheduler_log.log     # Scheduler logs
├── scripts/
│   ├── fetch_data.py         # Multi-crypto data fetching
│   ├── analytics.py          # Technical analysis engine
│   └── scheduler.py          # Automated scheduler
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd api-dashboard-project

# Install dependencies
pip install -r requirements.txt
```

### 2. Initial Data Collection

```bash
# Fetch initial data for all cryptocurrencies
python scripts/fetch_data.py
```

### 3. Generate Analytics

```bash
# Compute technical indicators and analytics
python scripts/analytics.py
```

### 4. Run the Dashboard

```bash
# Start the web dashboard
streamlit run dashboard/app.py
```

### 5. Start Automated Collection

```bash
# Run the scheduler (collects data every 5 minutes)
python scripts/scheduler.py
```

## 📈 Usage Guide

### Dashboard Features

1. **Cryptocurrency Selection**: Choose which cryptocurrencies to display
2. **Time Periods**: View data for 24 hours, 7 days, 30 days, or 90 days
3. **Price Charts**: Interactive line charts with multiple cryptocurrencies
4. **Volume Analysis**: Trading volume visualization
5. **Technical Analytics**: Detailed technical indicators for each cryptocurrency
6. **Market Overview**: Market cap distribution and top performers

### Data Collection

The system automatically collects data for these cryptocurrencies:
- Bitcoin (BTC)
- Ethereum (ETH)
- Cardano (ADA)
- Solana (SOL)
- Polkadot (DOT)
- Chainlink (LINK)
- Litecoin (LTC)
- Bitcoin Cash (BCH)

### Analytics Computed

- **Moving Averages**: 7-day and 30-day
- **Price Changes**: 1h, 24h, 7d, 30d percentage changes
- **Volatility**: 7-day and 30-day volatility calculations
- **RSI**: 14-day Relative Strength Index
- **Min/Max**: Highest and lowest prices in 7-day and 30-day periods

## 🔧 Configuration

### Scheduler Intervals

Edit `scripts/scheduler.py` to change collection frequency:

```python
# In the main() function
scheduler.run_scheduler(interval_minutes=5)  # Change this value
```

**Recommended intervals:**
- 1-2 minutes: High frequency (be mindful of API limits)
- 5 minutes: Balanced (recommended)
- 10+ minutes: Lower frequency

### Adding New Cryptocurrencies

Edit `scripts/fetch_data.py`:

```python
CRYPTOCURRENCIES = {
    'bitcoin': 'BTC',
    'ethereum': 'ETH',
    # Add new cryptocurrencies here
    'new-coin': 'NEW',
}
```

## 📊 Database Schema

### Prices Table
- `id`: Primary key
- `symbol`: Cryptocurrency symbol (BTC, ETH, etc.)
- `name`: Full name (bitcoin, ethereum, etc.)
- `price_usd`: Current price in USD
- `timestamp`: Data collection time
- `market_cap`: Market capitalization
- `volume_24h`: 24-hour trading volume
- `price_change_24h`: 24-hour price change percentage

### Analytics Table
- `id`: Primary key
- `symbol`: Cryptocurrency symbol
- `metric_name`: Analytics metric name
- `metric_value`: Computed metric value
- `time_period`: Time period for the metric
- `timestamp`: Computation time

## 🔍 Monitoring & Logs

### Log Files
- `data/fetch_log.log`: Data collection logs
- `data/scheduler_log.log`: Scheduler operation logs

### Log Levels
- **INFO**: Successful operations
- **WARNING**: Non-critical issues
- **ERROR**: Failed operations and exceptions

### Monitoring Features
- API request success/failure tracking
- Consecutive failure counting
- Automatic retry logic
- Scheduler status reporting

## 🛡️ Error Handling

The system includes comprehensive error handling:

- **API Failures**: Automatic retry with exponential backoff
- **Database Errors**: Transaction rollback on failures
- **Network Issues**: Timeout handling and connection retries
- **Data Validation**: Input validation and sanitization

## 📋 Requirements

- Python 3.7+
- SQLite3
- Internet connection for API access

### Dependencies
- `requests`: API communication
- `pandas`: Data manipulation
- `streamlit`: Web dashboard
- `plotly`: Interactive charts
- `numpy`: Numerical computations
- `schedule`: Task scheduling

## 🔮 Future Enhancements

- [ ] Price alerts and notifications
- [ ] Portfolio tracking
- [ ] More technical indicators (MACD, Bollinger Bands)
- [ ] Export functionality (CSV, PDF reports)
- [ ] Mobile-responsive design improvements
- [ ] Historical data export
- [ ] API rate limit optimization
- [ ] Docker containerization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the log files for error details
2. Verify API connectivity
3. Ensure database permissions
4. Check Python dependencies

---

**Happy Trading! 📈🚀**
