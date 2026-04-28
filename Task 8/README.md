# Stock Price App - Task 1

A Flask-based web application for tracking real-time stock prices with dynamic charts and comparison features.

## Features

- **Real-time Stock Data**: Search for any stock symbol and get current price, change, and market data
- **Interactive Charts**: View price history with 1M, 3M, 6M, and 1Y time periods
- **Stock Comparison**: Compare multiple stocks side by side
- **Favorites**: Save favorite stocks (stored in browser)
- **Responsive Design**: Beautiful UI that works on desktop and mobile
- **Market Statistics**: View PE ratio, market cap, volume, 52-week highs/lows

## Setup

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation

1. Navigate to the Task 1 folder:
```bash
cd "Task 1"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Flask app:
```bash
python app.py
```

4. Open your browser and go to:
```
http://localhost:5000
```

## How to Use

1. **Search**: Enter a stock symbol (e.g., AAPL, GOOGL, MSFT) in the search box
2. **View Data**: See real-time price, change percentage, and key metrics
3. **View Charts**: Click on time period buttons to view historical price charts
4. **Save Favorites**: Click the star icon to save stocks to your favorites

## Example Stock Symbols

- **AAPL** - Apple
- **GOOGL** - Google (Alphabet)
- **MSFT** - Microsoft
- **AMZN** - Amazon
- **TSLA** - Tesla
- **FB** - Meta (Facebook)
- **NVDA** - NVIDIA

## API Endpoints

- `GET /` - Home page
- `GET /api/stock/<symbol>` - Get current stock data
- `GET /api/stock-history/<symbol>` - Get historical price data
- `POST /api/compare` - Compare multiple stocks

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js
- **UI Framework**: Bootstrap 5
- **Data Source**: yfinance (free stock data)

## Notes

- Stock data is fetched from Yahoo Finance via yfinance library
- No API key required
- All data is real-time and updated
- Favorites are saved in browser's local storage
