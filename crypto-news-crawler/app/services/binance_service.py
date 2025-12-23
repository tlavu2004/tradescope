"""
app/services/binance_service.py

Service for fetching cryptocurrency price/market data from Binance API.
(Part 2: Price Collection & Analysis)
"""

from typing import Dict, List, Optional


class BinanceService:
    """Handles Binance API interactions for price and OHLCV data."""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.api_key = api_key
        self.api_secret = api_secret
        # Could use: from binance.client import Client
        # self.client = Client(api_key, api_secret)
    
    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """Fetch current price for a symbol (e.g., BTCUSDT).
        
        Args:
            symbol: Trading pair (BTCUSDT, ETHUSDT, ...)
            
        Returns:
            Current price or None if error.
        """
        # TODO: Implement Binance API call
        # resp = self.client.get_symbol_info(symbol)
        # return float(resp['price'])
        pass
    
    def get_klines(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 100,
    ) -> List[Dict]:
        """Fetch candlestick data (OHLCV) from Binance.
        
        Args:
            symbol: Trading pair (BTCUSDT, ETHUSDT, ...)
            interval: Kline interval (1m, 5m, 1h, 1d, ...)
            limit: Number of candles to fetch
            
        Returns:
            List of candle dicts with open, high, low, close, volume, etc.
        """
        # TODO: Implement Binance API call
        # klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
        # return [parse_kline(k) for k in klines]
        pass
    
    def get_24hr_ticker(self, symbol: str) -> Optional[Dict]:
        """Get 24h price stats (high, low, volume, etc.)."""
        # TODO: Implement
        pass


def get_binance_service() -> BinanceService:
    """Factory function to create BinanceService instance."""
    # Could load API key from config or environment
    return BinanceService()
