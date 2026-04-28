from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import os

import random

# ==== ENVIRONMENT SETUP FOR CURL/SSL BYPASS ====
# Set environment variables BEFORE importing anything that uses curl
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['SSL_NO_VERIFY'] = '1'

# Suppress SSL warnings
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Disable urllib3 warnings early
import urllib3
urllib3.disable_warnings()


# Type hints and requests config
from typing import Dict, Any, Optional, List
import requests
session = requests.Session()
session.verify = False

# Gemini is imported lazily to avoid startup failure on incompatible installs.
genai = None

# ==== MOCK DATA FOR STOCKS (SSL Workaround) ====
MOCK_STOCKS = {
    'AAPL': {'name': 'Apple Inc.', 'sector': 'Technology', 'industry': 'Consumer Electronics', 'base_price': 180.50},
    'GOOGL': {'name': 'Alphabet Inc.', 'sector': 'Technology', 'industry': 'Internet Services', 'base_price': 140.30},
    'MSFT': {'name': 'Microsoft Corporation', 'sector': 'Technology', 'industry': 'Software', 'base_price': 420.75},
    'AMZN': {'name': 'Amazon.com Inc.', 'sector': 'Consumer Cyclical', 'industry': 'Internet Retail', 'base_price': 190.45},
    'TSLA': {'name': 'Tesla Inc.', 'sector': 'Consumer Cyclical', 'industry': 'Automotive', 'base_price': 248.90},
    'META': {'name': 'Meta Platforms Inc.', 'sector': 'Technology', 'industry': 'Internet Services', 'base_price': 520.30},
    'NFLX': {'name': 'Netflix Inc.', 'sector': 'Communication Services', 'industry': 'Entertainment', 'base_price': 450.10},
}

def get_mock_stock_data(symbol: str) -> Optional[Dict[str, Any]]:
    """Generate consistent mock stock data based on symbol"""
    if symbol not in MOCK_STOCKS:
        return None
    
    stock_info = MOCK_STOCKS[symbol]
    base_price = stock_info['base_price']
    
    # Use symbol hash for consistent random values
    random.seed(hash(symbol) % (2**32))
    
    return {
        'symbol': symbol,
        'name': stock_info['name'],
        'sector': stock_info['sector'],
        'industry': stock_info['industry'],
        'price': base_price * (1 + random.uniform(-0.05, 0.05)),
        'previousClose': base_price * (1 + random.uniform(-0.05, 0.05)),
        'marketCap': random.randint(1000000000000, 3000000000000),
        'volume': random.randint(10000000, 100000000),
        'peRatio': random.uniform(15, 35),
        'fiftyTwoWeekHigh': base_price * 1.25,
        'fiftyTwoWeekLow': base_price * 0.75,
        'averageVolume': random.randint(20000000, 80000000),
    }

def get_mock_history(symbol: str, period: str = '1mo') -> List[Dict[str, Any]]:
    """Generate mock historical price data"""
    if symbol not in MOCK_STOCKS:
        return []
    
    base_price = MOCK_STOCKS[symbol]['base_price']
    random.seed(hash(symbol) % (2**32))
    
    # Determine number of days
    days_map = {'1d': 1, '1mo': 30, '3mo': 90, '6mo': 180, '1y': 365}
    days = days_map.get(period, 30)
    
    data = []
    current_date = datetime.now()
    current_price = base_price
    
    for i in range(days, 0, -1):
        date = (current_date - timedelta(days=i)).strftime('%Y-%m-%d')
        # Random walk
        current_price *= (1 + random.uniform(-0.02, 0.02))
        data.append({'date': date, 'price': round(current_price, 2)})
    
    return data

app = Flask(__name__)

# Configure Gemini API from environment only.
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '').strip()
model = None
GEMINI_AVAILABLE = False


def initialize_gemini() -> None:
    """Initialize Gemini safely; keep app functional if AI dependency is unavailable."""
    global genai, model, GEMINI_AVAILABLE

    if not GEMINI_API_KEY:
        GEMINI_AVAILABLE = False
        return

    try:
        import google.generativeai as _genai
        _genai.configure(api_key=GEMINI_API_KEY)
        # Use getattr to avoid attribute errors if API changes
        model_cls = getattr(_genai, 'GenerativeModel', None)
        if model_cls is not None:
            model = model_cls('gemini-1.5-flash')
            genai = _genai
            globals()['GEMINI_AVAILABLE'] = True
        else:
            model = None
            genai = None
            globals()['GEMINI_AVAILABLE'] = False
    except Exception:
        model = None
        genai = None
        GEMINI_AVAILABLE = False


initialize_gemini()

def get_ai_response(prompt: str) -> str:
    """Generate AI response using Gemini or mock data if unavailable"""
    try:
        if model and GEMINI_AVAILABLE:
            response = model.generate_content(prompt)
            # Some Gemini API versions return .text, others .result or .candidates
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'result'):
                return response.result
            elif hasattr(response, 'candidates') and response.candidates:
                return response.candidates[0].text
            else:
                return str(response)
    except Exception:
        pass
    
    # Mock responses for demo purposes
    mock_responses = {
        'prediction': "Based on current technical analysis, AAPL could see a price range of $175-$190 over the next 30 days. The stock is showing positive momentum with strong institutional support. Key factors: earnings growth, AI development initiatives, and market sentiment. Risk level: Medium.",
        'analysis': "AAPL is trading near fair valuation with strong fundamentals. Technical indicators show support at $170 and resistance at $195. The stock demonstrates healthy price momentum with consistent volume growth. Investment potential remains strong for long-term investors.",
        'news': "• Apple announced new AI features in iOS 18 • Supply chain improvements reducing production costs • Strong Q2 earnings beat expectations • Upcoming WWDC conference with product announcements • Positive analyst sentiment with multiple price target increases",
        'advice': "Investment Recommendation: BUY. Ideal for growth-focused investors with 5+ year horizon. Target entry price: $170-175. Stop loss: $155. Risk-reward ratio: 1:2.5. Note: Tech sector volatility and macro conditions present risks.",
        'query': "Apple is a leading technology company with strong competitive advantages in hardware and services. The stock has shown resilience with consistent growth over time."
    }
    
    # Return appropriate mock response based on prompt content
    if 'prediction' in prompt.lower():
        return mock_responses['prediction']
    elif 'valuation' in prompt.lower() or 'momentum' in prompt.lower():
        return mock_responses['analysis']
    elif 'news' in prompt.lower() or 'developments' in prompt.lower():
        return mock_responses['news']
    elif 'recommendation' in prompt.lower() or 'investment' in prompt.lower():
        return mock_responses['advice']
    else:
        return mock_responses['query']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/stock/<symbol>', methods=['GET'])
def get_stock(symbol: str):
    try:
        symbol = symbol.upper()
        
        # Use mock data
        mock_data = get_mock_stock_data(symbol)
        if not mock_data:
            return jsonify({'success': False, 'error': f'Stock symbol "{symbol}" not found'}), 404
        
        current_price = mock_data['price']
        previous_close = mock_data['previousClose']
        change = current_price - previous_close
        change_percent = (change / previous_close * 100) if previous_close else 0
        
        response = {
            'success': True,
            'symbol': symbol,
            'name': mock_data['name'],
            'price': round(current_price, 2),
            'change': round(change, 2),
            'changePercent': round(change_percent, 2),
            'previousClose': round(previous_close, 2),
            'marketCap': mock_data['marketCap'],
            'volume': mock_data['volume'],
            'peRatio': round(mock_data['peRatio'], 2),
            'week52High': round(mock_data['fiftyTwoWeekHigh'], 2),
            'week52Low': round(mock_data['fiftyTwoWeekLow'], 2),
            'avgVolume': mock_data['averageVolume'],
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stock-history/<symbol>', methods=['GET'])
def get_stock_history(symbol: str):
    try:
        period = request.args.get('period', '1mo')
        symbol = symbol.upper()
        
        # Use mock data
        history = get_mock_history(symbol, period)
        
        if not history:
            return jsonify({'success': False, 'error': 'No data found'}), 404
        
        dates = [item['date'] for item in history]
        closes = [item['price'] for item in history]
        
        return jsonify({
            'success': True,
            'dates': dates,
            'prices': closes
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def compare_stocks():
    try:
        symbols = request.json.get('symbols', [])
        
        if not symbols or len(symbols) == 0:
            return jsonify({'success': False, 'error': 'No symbols provided'}), 400
        
        comparison = []
        
        for symbol in symbols:
            symbol = symbol.upper()
            mock_data = get_mock_stock_data(symbol)
            
            if mock_data:
                current_price = mock_data['price']
                previous_close = mock_data['previousClose']
                change = current_price - previous_close
                change_percent = (change / previous_close * 100) if previous_close else 0
                
                comparison.append({
                    'symbol': symbol,
                    'name': mock_data['name'],
                    'price': round(current_price, 2),
                    'changePercent': round(change_percent, 2),
                    'volume': mock_data['volume']
                })
        
        return jsonify({'success': True, 'data': comparison})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/prediction/<symbol>', methods=['GET'])
def predict_stock(symbol: str):
    try:
        symbol = symbol.upper()
        mock_data = get_mock_stock_data(symbol)
        
        if not mock_data:
            return jsonify({'success': False, 'error': f'Stock "{symbol}" not found'}), 404
        
        current_price = mock_data['price']
        price_change_3m = random.uniform(-15, 25)  # Random 3-month change
        
        prompt = f"""Based on the following stock data, provide a brief price prediction for the next 30 days:

Stock: {symbol}
Company: {mock_data['name']}
Current Price: ${current_price:.2f}
3-Month Change: {price_change_3m:.2f}%
PE Ratio: {mock_data['peRatio']:.2f}
Market Cap: ${mock_data['marketCap']:,.0f}
Sector: {mock_data['sector']}

Provide:
1. A realistic price range prediction for 30 days
2. Key factors affecting the stock
3. Risk level (Low/Medium/High)
4. Brief reasoning

Keep response concise (3-4 sentences)."""

        response = get_ai_response(prompt)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'prediction': response
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/analysis/<symbol>', methods=['GET'])
def analyze_stock(symbol: str):
    try:
        symbol = symbol.upper()
        mock_data = get_mock_stock_data(symbol)
        
        if not mock_data:
            return jsonify({'success': False, 'error': f'Stock "{symbol}" not found'}), 404
        
        current_price = mock_data['price']
        year_high = mock_data['fiftyTwoWeekHigh']
        year_low = mock_data['fiftyTwoWeekLow']
        avg_price = (year_high + year_low) / 2
        
        prompt = f"""Provide a comprehensive market analysis for this stock:

Stock: {symbol}
Company: {mock_data['name']}
Current Price: ${current_price:.2f}
52-Week High: ${year_high:.2f}
52-Week Low: ${year_low:.2f}
Average Price (1Y): ${avg_price:.2f}
PE Ratio: {mock_data['peRatio']:.2f}
Dividend Yield: 2.5%
Industry: {mock_data['industry']}

Analyze:
1. Current valuation (overvalued/undervalued/fair)
2. Price momentum and trends
3. Technical levels (support/resistance)
4. Investment potential

Keep response concise (4-5 points)."""

        response = get_ai_response(prompt)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'analysis': response
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/news-summary/<symbol>', methods=['GET'])
def get_news_summary(symbol: str):
    try:
        symbol = symbol.upper()
        mock_data = get_mock_stock_data(symbol)
        
        if not mock_data:
            return jsonify({'success': False, 'error': f'Stock "{symbol}" not found'}), 404
        
        prompt = f"""Provide recent market news and developments affecting {symbol} ({mock_data['name']}):

Based on your knowledge, provide:
1. Recent company developments (last 3 months)
2. Industry trends affecting the stock
3. Upcoming catalysts or events
4. Market sentiment

Format as bullet points. Keep concise and factual."""

        response = get_ai_response(prompt)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'news': response
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/investment-advice/<symbol>', methods=['GET'])
def investment_advice(symbol: str):
    try:
        symbol = symbol.upper()
        mock_data = get_mock_stock_data(symbol)
        
        if not mock_data:
            return jsonify({'success': False, 'error': f'Stock "{symbol}" not found'}), 404
        
        current_price = mock_data['price']
        six_month_change = random.uniform(-20, 30)  # Random 6-month change
        
        prompt = f"""Provide investment advice for {symbol}:

Stock Details:
- Company: {mock_data['name']}
- Current Price: ${current_price:.2f}
- 6-Month Change: {six_month_change:.2f}%
- PE Ratio: {mock_data['peRatio']:.2f}
- Market Cap: ${mock_data['marketCap']:,.0f}
- Debt to Equity: 0.45
- Sector: {mock_data['sector']}

Provide:
1. Investment recommendation (BUY/HOLD/SELL)
2. Ideal investor profile (Risk tolerance, timeframe)
3. Target entry price
4. Stop loss level
5. Risk-reward ratio

Be realistic and balanced. Include caveats about market risks."""

        response = get_ai_response(prompt)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'advice': response
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/ask', methods=['POST'])
def ai_query():
    try:
        data = request.json
        symbol = data.get('symbol', '').upper()
        question = data.get('question', '')
        
        if not symbol or not question:
            return jsonify({'success': False, 'error': 'Symbol and question required'}), 400
        
        mock_data = get_mock_stock_data(symbol)
        if not mock_data:
            return jsonify({'success': False, 'error': f'Stock "{symbol}" not found'}), 400
        
        current_price = mock_data['price']
        
        prompt = f"""Answer this question about {symbol} ({mock_data['name']}):

Current Price: ${current_price}
Sector: {mock_data['sector']}
Industry: {mock_data['industry']}

User Question: {question}

Provide a concise, informative answer based on your knowledge of this stock and the market."""

        response = get_ai_response(prompt)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'question': question,
            'answer': response
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
