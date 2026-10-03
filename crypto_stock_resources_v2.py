from mcp.server.mcpserver import MCPServer
import requests
import yfinance as yf
from pathlib import Path


# ============================================================
# CREATE MCP SERVER
# ============================================================

mcp = MCPServer("crypto-stock")


# ============================================================
# TOOLS
# ============================================================

@mcp.tool()
def get_crypto_price(crypto: str) -> str:
    """
    Get the current USD price of a cryptocurrency.

    Examples:
    bitcoin, btc
    ethereum, eth
    solana, sol
    cardano, ada
    ripple, xrp
    dogecoin, doge
    """

    coin_id = crypto.strip().lower()

    aliases = {
        "btc": "bitcoin",
        "eth": "ethereum",
        "sol": "solana",
        "ada": "cardano",
        "xrp": "ripple",
        "doge": "dogecoin"
    }

    coin_id = aliases.get(coin_id, coin_id)

    url = "https://api.coingecko.com/api/v3/simple/price"

    try:

        response = requests.get(
            url,
            params={
                "ids": coin_id,
                "vs_currencies": "usd"
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if coin_id not in data:
            return f"Cryptocurrency '{crypto}' not found."

        return f"{coin_id} price: ${data[coin_id]['usd']} USD"

    except Exception as e:
        return str(e)


@mcp.tool()
def get_stock_price(symbol: str) -> str:
    """
    Get the latest stock price.

    Examples:
    AAPL
    MSFT
    NVDA
    GOOGL
    """

    try:

        ticker = yf.Ticker(symbol.upper())

        hist = ticker.history(period="1d")

        if hist.empty:
            return f"Stock '{symbol}' not found"

        price = round(hist["Close"].iloc[-1], 2)

        return f"{symbol.upper()} stock price: {price}"

    except Exception as e:
        return str(e)


# ============================================================
# RESOURCE 1
# STATIC RESOURCE
# ============================================================

@mcp.resource(
    "market://supported-assets",
    name="supported_assets",
    title="Supported Market Assets",
    description="List of supported stocks and cryptocurrencies",
    mime_type="text/plain"
)
def supported_assets() -> str:

    return """
SUPPORTED CRYPTOCURRENCIES
==========================

BTC  - Bitcoin
ETH  - Ethereum
SOL  - Solana
ADA  - Cardano
XRP  - Ripple
DOGE - Dogecoin


SUPPORTED STOCKS
================

AAPL  - Apple
MSFT  - Microsoft
NVDA  - NVIDIA
GOOGL - Alphabet
AMZN  - Amazon
META  - Meta
TSLA  - Tesla
"""


# ============================================================
# RESOURCE 2
# TEXT FILE RESOURCE
# ============================================================

@mcp.resource(
    "file://market-guide",
    name="market_guide",
    title="Market Analysis Guide",
    description="Market analysis guidelines stored in a text file",
    mime_type="text/plain"
)
def market_guide() -> str:

    file_path = Path(__file__).parent / "market_guide.txt"

    try:

        return file_path.read_text(encoding="utf-8")

    except FileNotFoundError:

        return "market_guide.txt was not found."


# ============================================================
# RESOURCE 3
# DYNAMIC RESOURCE
# ============================================================

@mcp.resource(
    "market://asset/{symbol}",
    name="asset_information",
    title="Asset Information",
    description="Get basic information about a market asset",
    mime_type="text/plain"
)
def asset_information(symbol: str) -> str:

    symbol = symbol.upper()

    assets = {

        "BTC": "Bitcoin - Cryptocurrency",
        "ETH": "Ethereum - Cryptocurrency",
        "SOL": "Solana - Cryptocurrency",
        "ADA": "Cardano - Cryptocurrency",
        "XRP": "Ripple - Cryptocurrency",
        "DOGE": "Dogecoin - Cryptocurrency",

        "AAPL": "Apple Inc. - Technology Stock",
        "MSFT": "Microsoft - Technology Stock",
        "NVDA": "NVIDIA - Semiconductor Stock",
        "GOOGL": "Alphabet - Technology Stock",
        "AMZN": "Amazon - E-commerce and Cloud Stock",
        "META": "Meta Platforms - Technology Stock",
        "TSLA": "Tesla - Electric Vehicle Stock"
    }

    if symbol not in assets:

        return f"No information available for {symbol}."

    return f"""
Asset: {symbol}

Description:
{assets[symbol]}

Use the appropriate MCP tool to retrieve
the current market price.
"""


# ============================================================
# PROMPT 1
# MARKET ANALYSIS
# ============================================================

@mcp.prompt(
    name="analyze_market",
    title="Analyze Market",
    description="Analyze a stock or cryptocurrency"
)
def analyze_market(
    symbol: str,
    asset_type: str = "stock"
) -> str:

    if asset_type.lower() == "crypto":

        return f"""
Analyze the cryptocurrency {symbol}.

Follow these steps:

1. Retrieve the current price using
   get_crypto_price.

2. Read the market analysis guide resource.

3. Analyze the cryptocurrency using the
   guidelines from the resource.

4. Discuss important market factors.

5. Discuss key risks.

6. Clearly separate current market data
   from general analysis.

Do not invent current market data.
"""

    return f"""
Analyze the stock {symbol}.

Follow these steps:

1. Retrieve the latest price using
   get_stock_price.

2. Read the market analysis guide resource.

3. Analyze the stock using the guidelines
   from the resource.

4. Discuss important market factors.

5. Discuss key risks.

6. Clearly separate current market data
   from general analysis.

Do not invent current market data.
"""


# ============================================================
# PROMPT 2
# STOCK RESEARCH
# ============================================================

@mcp.prompt(
    name="research_stock",
    title="Research Stock",
    description="Perform structured research on a stock"
)
def research_stock(symbol: str) -> str:

    return f"""
Perform structured research on the stock {symbol}.

Use the following workflow:

1. Read the market analysis guide resource.
2. Read the asset information resource for {symbol}.
3. Use get_stock_price to retrieve the latest price.
4. Explain what the company does.
5. Discuss important market factors.
6. Identify potential risks.
7. Present the result in a structured format.

Important:

- Do not invent current data.
- Clearly identify data retrieved from tools.
- Separate factual information from analysis.
"""


# ============================================================
# PROMPT 3
# CRYPTO RISK ANALYSIS
# ============================================================

@mcp.prompt(
    name="crypto_risk_analysis",
    title="Crypto Risk Analysis",
    description="Analyze the risks associated with a cryptocurrency"
)
def crypto_risk_analysis(symbol: str) -> str:

    return f"""
Perform a risk analysis for cryptocurrency {symbol}.

Steps:

1. Retrieve the current price using
   get_crypto_price.

2. Read the market analysis guide resource.

3. Read the asset information resource.

4. Analyze:

   - Price volatility
   - Market conditions
   - Adoption
   - Technology
   - Regulatory considerations
   - Liquidity
   - Major risks

5. Provide a concise summary.

Do not invent current market information.
Clearly distinguish retrieved data from analysis.
"""


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    mcp.run()