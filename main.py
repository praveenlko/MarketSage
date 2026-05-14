import yfinance as yf
from fastapi import FastAPI, HTTPException
import pandas as pd

app = FastAPI()

def get_live_market_data():
    # Nifty 50 stocks ki list yfinance se live gainers nikalne ke liye
    symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "BHARTIARTL.NS", "LICI.NS"]
    data = yf.download(symbols, period="1d", interval="15m", group_by='ticker', threads=True)
    
    live_stats = []
    for s in symbols:
        try:
            close_price = data[s]['Close'].iloc[-1]
            open_price = data[s]['Open'].iloc[0]
            change = ((close_price - open_price) / open_price) * 100
            live_stats.append({"symbol": s.replace(".NS", ""), "price": round(close_price, 2), "change": round(change, 2)})
        except:
            continue
    
    # Sort for Gainers and Losers
    gainers = sorted(live_stats, key=lambda x: x['change'], reverse=True)[:5]
    losers = sorted(live_stats, key=lambda x: x['change'])[:5]
    return gainers, losers

@app.get("/predict/{symbol}")
def get_prediction(symbol: str):
    try:
        ticker_symbol = f"{symbol.upper()}.NS" if "." not in symbol else symbol.upper()
        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(period="60d", interval="1d")

        if data.empty:
            raise HTTPException(status_code=404, detail="Stock not found")

        # Dynamic AI Logic: RSI + Moving Average
        current_price = data['Close'].iloc[-1]
        ma20 = data['Close'].rolling(window=20).mean().iloc[-1]
        
        # RSI Calculation (Simplified)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))

        # Decision Engine
        if rsi < 35 and current_price > ma20 * 0.98:
            prediction = "Strong Buy (Sahi Hai ✅)"
            confidence = 88
        elif rsi > 70:
            prediction = "Overbought (Avoid ❌)"
            confidence = 75
        else:
            prediction = "Neutral / Hold"
            confidence = 60

        return {
            "symbol": ticker_symbol,
            "prediction": prediction,
            "confidence": f"{confidence}%",
            "entry": round(current_price, 2),
            "target": round(current_price * 1.04, 2), # 4% Logic
            "sl": round(current_price * 0.97, 2),     # 3% Logic
            "rsi": round(rsi, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market-summary")
def get_market_summary():
    gainers, losers = get_live_market_data()
    return {
        "top_gainers": gainers,
        "top_losers": losers
    }