import requests
import yfinance as yf 
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("crypto-stock-price", host="0.0.0.0",port=8000)

@mcp.tool()
def get_crypto_price(crypto:str)->str:
    """
    Get the current USD price of a cryptocurrency.

    Pass the CoinGecko coin *id* (lowercase full name), not the ticker symbol:
    - bitcoin   (not BTC)
    - ethereum  (not ETH)
    - solana
    - dogecoin
    """
    
    coin_id = crypto.strip().lower()
    
    aliases = {
        "btc":"bitcoint",
        "eth":"ethereum",
        "sol":"solana",
        "ada":"cardano",
        "xrp":"ripple"
        
    }
    coin_id = aliases.get(coin_id, coin_id)
    
    url = "https://api.coingecko.com/api/v3/simple/price"
    
    try:
        response = requests.get(
            url,
            params = {"ids":coin_id,"vs_currencies":"usd"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if coin_id not in data:
            return (
                f"Cryptocurrency '{crypto}' not found."
            )
        return f"{coin_id} price: ${data[coin_id]['usd']} USD"
    except Exception as e:
        return str(e)
    
@mcp.tool()
def get_stock_price(symbol:str) ->str:
    """
    Get the latest stock price
    
    Examples 
    APPL, NVDA, MSFT, GOOGL
    
    """
    
    try:
        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period = "1d")
        
        if hist.empty:
            return f"Stock '{symbol}' not found"
        
        price = round(hist["Close"].iloc[-1],2)
        
        return f"{symbol.upper()} stock price :{price}"
    
    except Exception as e:
        return str(e)
    
if __name__=="__main__":
    mcp.run(transport="streamable-http")