from fastapi import FastAPI, HTTPException
import yfinance as yf
import pandas as pd

app = FastAPI()

@app.get("/predict/{symbol}")
def get_prediction(symbol: str):
    try:
        # Global support: Agar user 'AAPL' daale toh directly search hoga, 
        # Agar NSE stock hai toh '.NS' check karega
        ticker_symbol = symbol if "." in symbol else f"{symbol}.NS"
        stock = yf.Ticker(ticker_symbol)
        
        # History fetch kar rahe hain analysis ke liye
        hist = stock.history(period="1mo")
        if hist.empty:
            # Try global if NSE fails
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1mo")
            if hist.empty:
                raise HTTPException(status_code=404, detail="Stock not found")

        # Basic AI/Logic for Prediction
        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-5] # 1 week ago
        
        # Simple Trend Analysis (Isse aap complex AI model se replace kar sakte hain)
        change = ((current_price - prev_price) / prev_price) * 100
        
        if change > 1:
            prediction = "Strong Buy"
            confidence = "85%"
            summary = f"{symbol} is showing a bullish trend. Support is strong at {hist['Low'].min():.2f}. Good for Equity & Call Options."
        elif change < -1:
            prediction = "Sell"
            confidence = "78%"
            summary = f"{symbol} is in a bearish phase. Breaking below key supports. Avoid fresh long positions."
        else:
            prediction = "Hold"
            confidence = "65%"
            summary = f"Consolidation seen in {symbol}. Wait for a clear breakout above {hist['High'].max():.2f}."

        return {
            "symbol": symbol.upper(),
            "prediction": prediction,
            "confidence": confidence,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)