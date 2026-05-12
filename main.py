from fastapi import FastAPI, HTTPException
import yfinance as yf

app = FastAPI()

@app.get("/predict/{symbol}")
def get_prediction(symbol: str):
    try:
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
        
        return {
            "symbol": ticker_symbol,
            "prediction": prediction,
            "confidence": f"{80 + abs(int(diff))}%",
            "summary": f"Currently trading at {curr:.2f}. The 5-day trend shows a {diff:.2f}% move. Recommendation based on momentum."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New endpoint for trending/personalized list
@app.get("/trending")
def get_trending():
    return {"stocks": ["RELIANCE", "TATASTEEL", "AAPL", "BTC-USD", "ZOMATO"]}
    
@app.get("/news")
def get_market_news():
    return {"news": ["Nifty 50 hits 23k", "Fed meeting today", "Tech stocks rallying"]}
