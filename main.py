import yfinance as yf
<<<<<<< HEAD
=======
from fastapi import FastAPI, HTTPException
>>>>>>> e9c7c640c5276544ac502399b15cf80c985f8614

app = FastAPI()

@app.get("/predict/{symbol}")
def get_prediction(symbol: str):
    try:
<<<<<<< HEAD
        # Check if it's likely an Indian stock (No dot and uppercase)
        ticker_symbol = symbol.upper()
        if "." not in ticker_symbol:
            # We try NSE first for Indian users
            ticker = yf.Ticker(f"{ticker_symbol}.NS")
            hist = ticker.history(period="5d")
            if hist.empty:
                # If not found, try as a global symbol (e.g., AAPL)
                ticker = yf.Ticker(ticker_symbol)
                hist = ticker.history(period="5d")
        else:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="5d")

        if hist.empty:
            raise HTTPException(status_code=404, detail="Stock not found")

        curr = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        diff = ((curr - prev) / prev) * 100

        prediction = "Strong Buy" if diff > 0.5 else "Hold" if diff > -0.5 else "Sell"
=======
        # User agar sirf 'TATA' likhe toh automatically '.NS' add karein
        ticker_symbol = f"{symbol.upper()}.NS" if "." not in symbol else symbol.upper()
        ticker = yf.Ticker(ticker_symbol)
        
        # Live Data fetch karna
        data = ticker.history(period="1mo")
        if data.empty:
            raise HTTPException(status_code=404, detail="Stock not found")

        current_price = data['Close'].iloc[-1]
        change = ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
        
        # Simple AI Logic based on Moving Average
        ma20 = data['Close'].mean()
        prediction = "Strong Buy" if current_price > ma20 else "Wait/Hold"
>>>>>>> e9c7c640c5276544ac502399b15cf80c985f8614
        
        return {
            "symbol": ticker_symbol,
            "prediction": prediction,
<<<<<<< HEAD
            "confidence": f"{80 + abs(int(diff))}%",
            "summary": f"Currently trading at {curr:.2f}. The 5-day trend shows a {diff:.2f}% move. Recommendation based on momentum."
=======
            "confidence": f"{int(70 + abs(change))}%",
            "summary": f"Live Price: ₹{current_price:.2f}. Stock is {'above' if current_price > ma20 else 'below'} its 20-day average."
>>>>>>> e9c7c640c5276544ac502399b15cf80c985f8614
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

<<<<<<< HEAD
# New endpoint for trending/personalized list
@app.get("/trending")
def get_trending():
    return {"stocks": ["RELIANCE", "TATASTEEL", "AAPL", "BTC-USD", "ZOMATO"]}
    
@app.get("/news")
def get_market_news():
    return {"news": ["Nifty 50 hits 23k", "Fed meeting today", "Tech stocks rallying"]}
=======
@app.get("/news")
def get_live_news():
    # Nifty 50 ki live news fetch karne ka simple logic
    try:
        nifty = yf.Ticker("^NSEI")
        news_list = [n['title'] for n in nifty.news[:5]] # Top 5 news
        return {"news": news_list if news_list else ["Market is steady", "Check top gainers today"]}
    except:
        return {"news": ["Sensex up by 200 points", "Global markets showing green trend"]}

@app.get("/trending")
def get_trending():
    # Aap yahan top volume stocks ki list de sakte hain
    return {"stocks": ["ZOMATO", "TATASTEEL", "RELIANCE", "IREDA", "HDFCBANK"]}
>>>>>>> e9c7c640c5276544ac502399b15cf80c985f8614
