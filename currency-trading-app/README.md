# 📊 Currency Trading Analysis Platform

A comprehensive, AI-powered forex trading analysis platform that helps you monitor currency fluctuations, analyze market trends, and make informed trading decisions.

## 🌟 Features

### Core Functionality
- **Real-time Currency Rates**: Live exchange rates for 150+ currencies
- **Historical Data Tracking**: Store and analyze historical price movements
- **Portfolio Management**: Track your currency holdings and P&L
- **Technical Analysis**:
  - Moving Averages (SMA, EMA)
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - Volatility Analysis
- **Trading Signals**: Automated buy/sell/hold recommendations
- **News & Events**: Latest forex news and economic calendar
- **AI-Powered Analysis**: LLM-based qualitative market analysis via OpenRouter

### Advanced Features
- **Multi-dimensional Signal Generation**: Combines technical, fundamental, and sentiment analysis
- **Opportunity Scanner**: Find the best trading opportunities across major currency pairs
- **Daily Market Summaries**: AI-generated briefings on market conditions
- **Currency Fundamentals**: Learn what drives each currency's value
- **Interactive Charts**: Visualize price history and portfolio allocation
- **Beautiful Web Interface**: Modern, responsive dashboard

## 🏗️ Architecture

```
currency-trading-app/
├── backend/                  # Python FastAPI backend
│   ├── app.py               # Main application
│   ├── config.py            # Configuration
│   ├── database.py          # Database models
│   ├── requirements.txt     # Python dependencies
│   └── services/            # Business logic
│       ├── currency_service.py      # Currency data fetching
│       ├── historical_service.py    # Historical data management
│       ├── portfolio_service.py     # Portfolio tracking
│       ├── technical_analysis.py    # Technical indicators
│       ├── news_service.py          # News fetching
│       ├── llm_service.py           # AI analysis
│       └── signals_service.py       # Trading signals
├── frontend/                # Web interface
│   ├── index.html          # Main page
│   ├── styles.css          # Styling
│   └── app.js              # Frontend logic
├── data/                   # SQLite database
└── .env                    # Configuration (create from .env.example)
```

## 📚 Understanding Currency Trading

### What Drives Currency Values?

**1. Interest Rates**
- Central banks (Federal Reserve, ECB, Bank of Japan, etc.) set interest rates
- Higher rates attract foreign investment, strengthening the currency
- Lower rates can weaken a currency but stimulate economic growth

**2. Inflation**
- Low, stable inflation = strong currency
- High inflation erodes purchasing power and weakens currency
- Central banks adjust rates to control inflation

**3. Economic Performance (GDP)**
- Strong economic growth attracts investment
- GDP reports, employment data, manufacturing indices all impact currency value
- IMF and World Bank provide macroeconomic data for countries

**4. Trade Balance**
- Countries with trade surpluses (exports > imports) see currency demand increase
- Trade deficits can weaken a currency over time
- Check trade balance reports quarterly

**5. Political Stability & Geopolitical Events**
- Elections, policy changes, international conflicts affect currency values
- Political uncertainty typically weakens a currency
- Safe-haven currencies (USD, CHF, JPY) strengthen during crises

**6. Market Sentiment**
- Trader psychology and speculation drive short-term movements
- News events can trigger rapid price changes
- "Risk-on" vs "risk-off" market environments

### Key Economic Indicators to Watch

| Indicator | Impact | Frequency |
|-----------|--------|-----------|
| Interest Rate Decisions | HIGH | Monthly/Quarterly |
| Non-Farm Payrolls (US) | HIGH | Monthly |
| GDP Growth Rate | HIGH | Quarterly |
| Inflation (CPI/PPI) | HIGH | Monthly |
| Trade Balance | MEDIUM | Monthly |
| Retail Sales | MEDIUM | Monthly |
| Manufacturing PMI | MEDIUM | Monthly |
| Central Bank Minutes | HIGH | Varies |

### Data Sources We Use

**Currency Rates:**
- **Frankfurter API**: Free, no API key required, historical data available
- **ExchangeRate.host**: Backup source for real-time rates

**Economic Data:**
- **IMF API**: Macroeconomic indicators, GDP, inflation, reserves
- Coverage: 180+ countries
- Historical data available for trend analysis

**News & Sentiment:**
- Financial news aggregation from multiple sources
- Economic calendar with high-impact events
- AI-powered sentiment analysis

**AI Analysis:**
- **OpenRouter**: Access to multiple LLMs (Claude, GPT-4, Gemini)
- Qualitative analysis of market conditions
- Natural language explanations of complex data

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git
- A modern web browser

### Installation

1. **Clone or navigate to the project**
   ```bash
   cd currency-trading-app
   ```

2. **Set up Python virtual environment** (recommended)
   ```bash
   python -m venv venv

   # On Windows:
   venv\Scripts\activate

   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example file
   cp ../.env.example ../.env

   # Edit .env and add your OpenRouter API key (for AI features)
   # Get a free key from: https://openrouter.ai/keys
   ```

5. **Initialize the database**
   ```bash
   python -c "from database import init_db; init_db()"
   ```

6. **Start the backend server**
   ```bash
   python app.py
   ```

   The API will be available at `http://localhost:8000`

7. **Open the frontend** (in a new terminal)
   ```bash
   # Navigate to frontend directory
   cd ../frontend

   # Serve the frontend (Python 3)
   python -m http.server 8080
   ```

   Open your browser to `http://localhost:8080`

### Quick Start Without AI Features

If you want to test the platform without setting up OpenRouter:
- Leave the `OPENROUTER_API_KEY` blank in `.env`
- All features work except AI analysis endpoints
- Technical analysis, signals, portfolio, and charts work perfectly

## 📖 Usage Guide

### 1. Dashboard
- **Currency Converter**: Convert between any supported currencies
- **Top Movers**: See which currency pairs moved the most in 24h
- **Price Charts**: Visualize historical price movements

### 2. Trading Signals
- **Generate Signal**: Get buy/sell/hold recommendation for any pair
- **Scan Opportunities**: Find the best trading setups across major pairs
- **Recent Signals**: View your signal history

### 3. Portfolio Management
- **Add Positions**: Record your currency purchases
- **Track P&L**: See real-time profit/loss for each position
- **Allocation Chart**: Visualize your portfolio distribution

### 4. AI Analysis
- **Currency Pair Analysis**: Get in-depth AI analysis combining technical and fundamental factors
- **Daily Summary**: AI-generated market briefing with top movers and key events
- **Currency Fundamentals**: Learn what drives each currency (educational)

### 5. News & Events
- **Latest News**: Forex-related news headlines
- **Economic Calendar**: Upcoming high-impact economic events

## 🔧 API Endpoints

### Currency Rates
- `GET /api/rates/latest?base=USD` - Latest rates for a base currency
- `GET /api/rates/pair/{from}/{to}` - Specific currency pair rate
- `GET /api/rates/convert?amount=100&from_currency=USD&to_currency=EUR` - Convert amount
- `GET /api/rates/supported` - List all supported currencies

### Historical Data
- `GET /api/historical/{base}/{quote}?days=30` - Historical rates
- `POST /api/historical/fetch` - Fetch and store historical data
- `GET /api/historical/change/{base}/{quote}?hours=24` - Price change over period

### Portfolio
- `GET /api/portfolio` - Get portfolio value and positions
- `POST /api/portfolio/position` - Add new position
- `DELETE /api/portfolio/position/{id}` - Delete position
- `GET /api/portfolio/allocation` - Currency allocation breakdown

### Trading Signals
- `GET /api/signals/{base}/{quote}?use_llm=false` - Generate trading signal
- `GET /api/signals/recent?limit=10` - Recent signals
- `POST /api/signals/scan?signal_type=BUY&min_strength=60` - Scan for opportunities

### News
- `GET /api/news?use_mock=true` - Latest forex news
- `GET /api/news/calendar` - Economic calendar events

### AI Analysis
- `POST /api/analysis/currency-pair?base=EUR&quote=USD` - AI pair analysis
- `GET /api/analysis/daily-summary` - Daily market summary
- `GET /api/analysis/fundamentals/{currency}` - Currency fundamentals explanation

## 💡 Trading Strategies & Tips

### For Beginners
1. **Start Small**: Test with paper trading before using real money
2. **Learn the Basics**: Use the "Currency Fundamentals" feature
3. **Follow the Signals**: Our combined technical+sentiment signals provide a good starting point
4. **Watch Economic Calendar**: High-impact events can cause significant volatility

### Intermediate Strategies
1. **Trend Following**: Use moving average crossovers (built into our signals)
2. **Mean Reversion**: Look for oversold (RSI < 30) or overbought (RSI > 70) conditions
3. **News Trading**: Trade around major economic announcements
4. **Carry Trade**: Buy high-interest currencies, sell low-interest ones

### Using the Platform Effectively
1. **Daily Routine**:
   - Check Daily Summary for market overview
   - Review Top Movers for unusual activity
   - Scan for Opportunities with your criteria
   - Read latest news for context

2. **Before Trading**:
   - Generate signal for your pair
   - Check AI Analysis for deeper insights
   - Review economic calendar for upcoming events
   - Check your portfolio allocation

3. **Risk Management**:
   - Never risk more than 1-2% of portfolio on a single trade
   - Use stop losses
   - Diversify across multiple currency pairs
   - Track all positions in the portfolio manager

## ⚠️ Important Disclaimers

1. **Not Financial Advice**: This tool is for educational and research purposes only
2. **Risk Warning**: Forex trading carries substantial risk of loss
3. **AI Limitations**: LLM analysis should supplement, not replace, your own research
4. **Data Accuracy**: While we use reliable sources, always verify critical information
5. **No Guarantees**: Past performance does not guarantee future results

## 🔒 Security & Privacy

- All data stored locally in SQLite database
- No user data sent to third parties (except API calls to OpenRouter for AI features)
- API keys stored in `.env` file (never commit to git)
- Open source - review the code yourself

## 🛠️ Troubleshooting

**"Failed to fetch exchange rates"**
- Check your internet connection
- The free APIs may have rate limits; wait a minute and try again

**"LLM service unavailable"**
- Verify your OpenRouter API key in `.env`
- Check you have credits in your OpenRouter account
- Some features work without LLM (technical signals, portfolio, charts)

**"No historical data available"**
- Click "Fetch Historical Data" to populate the database
- First-time setup requires fetching data from APIs

**Database errors**
- Delete `data/trading.db` and reinitialize: `python -c "from database import init_db; init_db()"`

## 🚀 Advanced Configuration

### Using PostgreSQL Instead of SQLite
```bash
# Install psycopg2
pip install psycopg2-binary

# Update .env
DATABASE_URL=postgresql://user:password@localhost/trading_db
```

### Customizing Technical Indicators
Edit `backend/config.py`:
```python
MA_SHORT_PERIOD = 20  # Short-term moving average
MA_LONG_PERIOD = 50   # Long-term moving average
RSI_PERIOD = 14
```

### Adding More Currency Pairs
Edit `backend/config.py`:
```python
MAJOR_CURRENCY_PAIRS = [
    "EUR/USD", "USD/JPY", # ... add more
]
```

## 📊 Sample Workflows

### Workflow 1: Daily Market Check
1. Open platform → Dashboard
2. Check "Top Movers" for unusual activity
3. Switch to AI Analysis → "Generate Daily Summary"
4. Review economic calendar for upcoming events
5. Identify opportunities in Trading Signals tab

### Workflow 2: Analyzing a Specific Pair
1. Dashboard → Set pair (e.g., EUR/USD)
2. Load 60-day historical chart
3. Trading Signals → Generate signal with AI
4. Read AI Analysis for detailed breakdown
5. Check news for recent headlines about EUR and USD

### Workflow 3: Portfolio Management
1. Portfolio tab → Add your positions
2. Review portfolio summary (total value, P&L)
3. Check allocation chart for diversification
4. Generate signals for holdings to decide hold/sell
5. Update positions as needed

## 🤝 Contributing

This is an educational project. Feel free to:
- Fork and modify for your needs
- Add new technical indicators
- Integrate additional data sources
- Improve the UI/UX
- Add new analysis features

## 📝 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

- **Data Sources**: Frankfurter API, ExchangeRate.host, IMF
- **AI**: OpenRouter for LLM access
- **Charts**: Chart.js for visualizations
- **Inspiration**: The need for accessible, comprehensive forex analysis tools

## 📧 Support

For questions or issues:
1. Check the Troubleshooting section
2. Review the API documentation
3. Examine the code (it's well-commented!)

---

**Happy Trading! 📈💰**

Remember: The best investment you can make is in education. Use this tool to learn, practice, and understand the forex market before risking real capital.
