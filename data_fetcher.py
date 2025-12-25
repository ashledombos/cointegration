"""
Data Fetcher - Récupération des données historiques
====================================================
Supporte: yfinance, CCXT (crypto), avec cache local.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
from loguru import logger
import hashlib
import json

try:
    import yfinance as yf
except ImportError:
    yf = None

try:
    import ccxt
except ImportError:
    ccxt = None

from config import config


class DataCache:
    """Cache local pour les données historiques."""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> dict:
        if self.metadata_file.exists():
            return json.loads(self.metadata_file.read_text())
        return {}
    
    def _save_metadata(self):
        self.metadata_file.write_text(json.dumps(self.metadata, indent=2))
    
    def _get_cache_key(self, symbol: str, timeframe: str) -> str:
        return hashlib.md5(f"{symbol}_{timeframe}".encode()).hexdigest()[:12]
    
    def get(self, symbol: str, timeframe: str, max_age_hours: int = 24) -> Optional[pd.DataFrame]:
        key = self._get_cache_key(symbol, timeframe)
        cache_file = self.cache_dir / f"{key}.parquet"
        
        if key in self.metadata:
            cached_time = datetime.fromisoformat(self.metadata[key]["timestamp"])
            age_hours = (datetime.now() - cached_time).total_seconds() / 3600
            
            if age_hours < max_age_hours and cache_file.exists():
                logger.debug(f"Cache hit: {symbol}")
                return pd.read_parquet(cache_file)
        return None
    
    def set(self, symbol: str, timeframe: str, data: pd.DataFrame):
        key = self._get_cache_key(symbol, timeframe)
        cache_file = self.cache_dir / f"{key}.parquet"
        
        data.to_parquet(cache_file)
        self.metadata[key] = {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": datetime.now().isoformat(),
            "rows": len(data)
        }
        self._save_metadata()


class YFinanceFetcher:
    """Récupération via yfinance."""
    
    def __init__(self):
        if yf is None:
            raise ImportError("yfinance requis: pip install yfinance")
    
    def fetch(
        self, 
        symbol: str, 
        start_date: datetime,
        end_date: datetime,
        timeframe: str = "1d"
    ) -> Optional[pd.DataFrame]:
        try:
            interval_map = {
                "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
                "1h": "1h", "4h": "1h", "1d": "1d", "1w": "1wk"
            }
            interval = interval_map.get(timeframe, "1d")
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date, interval=interval, auto_adjust=True)
            
            if df.empty:
                logger.warning(f"Pas de données pour {symbol}")
                return None
            
            df = df.rename(columns={
                "Open": "open", "High": "high", 
                "Low": "low", "Close": "close", "Volume": "volume"
            })
            df = df[["open", "high", "low", "close", "volume"]]
            
            if timeframe == "4h":
                df = self._aggregate_to_4h(df)
            
            df.index = pd.to_datetime(df.index)
            df.index = df.index.tz_localize(None)
            
            logger.info(f"Fetched {symbol}: {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Erreur fetch {symbol}: {e}")
            return None
    
    def _aggregate_to_4h(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.resample("4h").agg({
            "open": "first", "high": "max",
            "low": "min", "close": "last", "volume": "sum"
        }).dropna()


class CCXTFetcher:
    """Récupération via CCXT (crypto)."""
    
    def __init__(self, exchange_id: str = "binance"):
        if ccxt is None:
            raise ImportError("ccxt requis: pip install ccxt")
        
        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class({
            "enableRateLimit": True,
            "options": {"defaultType": "spot"}
        })
    
    def fetch(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        timeframe: str = "1d"
    ) -> Optional[pd.DataFrame]:
        try:
            tf_map = {
                "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
                "1h": "1h", "4h": "4h", "1d": "1d", "1w": "1w"
            }
            ccxt_tf = tf_map.get(timeframe, "1d")
            since = int(start_date.timestamp() * 1000)
            
            all_data = []
            while since < int(end_date.timestamp() * 1000):
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=ccxt_tf, since=since, limit=1000)
                if not ohlcv:
                    break
                all_data.extend(ohlcv)
                since = ohlcv[-1][0] + 1
            
            if not all_data:
                return None
            
            df = pd.DataFrame(all_data, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df = df.set_index("timestamp")
            df = df[(df.index >= start_date) & (df.index <= end_date)]
            
            logger.info(f"Fetched {symbol}: {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Erreur fetch {symbol}: {e}")
            return None


class DataFetcher:
    """Interface unifiée pour la récupération de données."""
    
    def __init__(self):
        self.cache = DataCache(config.data.cache_dir)
        self.yf_fetcher = YFinanceFetcher() if yf else None
        self.ccxt_fetcher = None
        
        if config.data.primary_source == "ccxt" and ccxt:
            self.ccxt_fetcher = CCXTFetcher(config.data.ccxt_exchange)
    
    def _detect_source(self, symbol: str) -> str:
        if "/" in symbol:
            return "ccxt"
        return "yfinance"
    
    def fetch_single(
        self,
        symbol: str,
        lookback_days: Optional[int] = None,
        timeframe: Optional[str] = None,
        use_cache: bool = True
    ) -> Optional[pd.DataFrame]:
        lookback = lookback_days or config.data.lookback_days
        tf = timeframe or config.data.timeframe
        
        if use_cache:
            cached = self.cache.get(symbol, tf)
            if cached is not None:
                return cached
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback)
        
        source = self._detect_source(symbol)
        
        if source == "ccxt" and self.ccxt_fetcher:
            df = self.ccxt_fetcher.fetch(symbol, start_date, end_date, tf)
        elif self.yf_fetcher:
            df = self.yf_fetcher.fetch(symbol, start_date, end_date, tf)
        else:
            logger.error(f"Aucune source pour {symbol}")
            return None
        
        if df is not None and use_cache:
            self.cache.set(symbol, tf, df)
        
        return df
    
    def fetch_multiple(
        self,
        symbols: List[str],
        lookback_days: Optional[int] = None,
        timeframe: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        results = {}
        for symbol in symbols:
            df = self.fetch_single(symbol, lookback_days, timeframe)
            if df is not None:
                results[symbol] = df
        
        logger.info(f"Fetched {len(results)}/{len(symbols)} symbols")
        return results
    
    def fetch_pair(
        self,
        symbol1: str,
        symbol2: str,
        lookback_days: Optional[int] = None,
        timeframe: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        df1 = self.fetch_single(symbol1, lookback_days, timeframe)
        df2 = self.fetch_single(symbol2, lookback_days, timeframe)
        
        if df1 is None or df2 is None:
            return None
        
        combined = pd.DataFrame({
            "close_1": df1["close"],
            "close_2": df2["close"]
        }).dropna()
        
        if len(combined) < 50:
            logger.warning(f"Données insuffisantes: {symbol1}/{symbol2}")
            return None
        
        combined.attrs["symbol1"] = symbol1
        combined.attrs["symbol2"] = symbol2
        
        return combined
    
    def get_latest_prices(self, symbols: List[str]) -> Dict[str, float]:
        prices = {}
        for symbol in symbols:
            df = self.fetch_single(symbol, lookback_days=5, use_cache=False)
            if df is not None and not df.empty:
                prices[symbol] = df["close"].iloc[-1]
        return prices


if __name__ == "__main__":
    import sys
    logger.remove()
    logger.add(sys.stdout, level="INFO")
    
    fetcher = DataFetcher()
    
    # Test
    df = fetcher.fetch_single("SPY", lookback_days=365)
    if df is not None:
        print(f"SPY: {len(df)} rows")
        print(df.tail())
