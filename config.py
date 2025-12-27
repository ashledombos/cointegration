"""
Configuration du système de Pairs Trading par Coïntégration
============================================================
Symboles FTMO avec mapping vers yfinance pour données historiques.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from dotenv import load_dotenv

load_dotenv()


# =============================================================================
# MAPPING FTMO -> YFINANCE
# =============================================================================
# Les symboles FTMO ne sont pas directement utilisables avec yfinance.
# Ce dictionnaire fait la correspondance.

FTMO_TO_YFINANCE: Dict[str, str] = {
    # -------------------------------------------------------------------------
    # FOREX (FTMO -> yfinance format "XXX=X")
    # -------------------------------------------------------------------------
    "AUDCAD": "AUDCAD=X",
    "AUDCHF": "AUDCHF=X",
    "AUDJPY": "AUDJPY=X",
    "AUDNZD": "AUDNZD=X",
    "AUDUSD": "AUDUSD=X",
    "CADCHF": "CADCHF=X",
    "CADJPY": "CADJPY=X",
    "CHFJPY": "CHFJPY=X",
    "EURAUD": "EURAUD=X",
    "EURCAD": "EURCAD=X",
    "EURCHF": "EURCHF=X",
    "EURCZK": "EURCZK=X",
    "EURGBP": "EURGBP=X",
    "EURHUF": "EURHUF=X",
    "EURJPY": "EURJPY=X",
    "EURNOK": "EURNOK=X",
    "EURNZD": "EURNZD=X",
    "EURPLN": "EURPLN=X",
    "EURUSD": "EURUSD=X",
    "GBPAUD": "GBPAUD=X",
    "GBPCAD": "GBPCAD=X",
    "GBPCHF": "GBPCHF=X",
    "GBPJPY": "GBPJPY=X",
    "GBPNZD": "GBPNZD=X",
    "GBPUSD": "GBPUSD=X",
    "NZDCAD": "NZDCAD=X",
    "NZDCHF": "NZDCHF=X",
    "NZDJPY": "NZDJPY=X",
    "NZDUSD": "NZDUSD=X",
    "USDCAD": "USDCAD=X",
    "USDCHF": "USDCHF=X",
    "USDCNH": "USDCNY=X",
    "USDHKD": "USDHKD=X",
    "USDHUF": "USDHUF=X",
    "USDILS": "USDILS=X",
    "USDJPY": "USDJPY=X",
    "USDMXN": "USDMXN=X",
    "USDNOK": "USDNOK=X",
    "USDPLN": "USDPLN=X",
    "USDSEK": "USDSEK=X",
    "USDSGD": "USDSGD=X",
    "USDZAR": "USDZAR=X",
    
    # -------------------------------------------------------------------------
    # INDICES (FTMO -> ETF équivalent)
    # -------------------------------------------------------------------------
    "US500.cash": "SPY",
    "US100.cash": "QQQ",
    "US30.cash": "DIA",
    "US2000.cash": "IWM",
    "GER40.cash": "EWG",
    "UK100.cash": "EWU",
    "FRA40.cash": "EWQ",
    "JP225.cash": "EWJ",
    "AUS200.cash": "EWA",
    "EU50.cash": "FEZ",
    "HK50.cash": "EWH",
    "SPN35.cash": "EWP",
    "N25.cash": "EWN",
    "DXY.cash": "UUP",
    
    # -------------------------------------------------------------------------
    # MÉTAUX
    # -------------------------------------------------------------------------
    "XAUUSD": "GC=F",
    "XAGUSD": "SI=F",
    "XAUEUR": "GC=F",
    "XAGEUR": "SI=F",
    "XAUAUD": "GC=F",
    "XAGAUD": "SI=F",
    "XPTUSD": "PL=F",
    "XPDUSD": "PA=F",
    "XCUUSD": "HG=F",
    
    # -------------------------------------------------------------------------
    # COMMODITIES
    # -------------------------------------------------------------------------
    "USOIL.cash": "CL=F",
    "UKOIL.cash": "BZ=F",
    "NATGAS.cash": "NG=F",
    "COCOA.c": "CC=F",
    "COFFEE.c": "KC=F",
    "CORN.c": "ZC=F",
    "COTTON.c": "CT=F",
    "SOYBEAN.c": "ZS=F",
    "SUGAR.c": "SB=F",
    "WHEAT.c": "ZW=F",
    "HEATOIL.c": "HO=F",
    
    # -------------------------------------------------------------------------
    # CRYPTO (FTMO -> yfinance format "XXX-USD")
    # -------------------------------------------------------------------------
    "BTCUSD": "BTC-USD",
    "ETHUSD": "ETH-USD",
    "LTCUSD": "LTC-USD",
    "XRPUSD": "XRP-USD",
    "ADAUSD": "ADA-USD",
    "DOTUSD": "DOT-USD",
    "SOLUSD": "SOL-USD",
    "BNBUSD": "BNB-USD",
    "DOGEUSD": "DOGE-USD",
    "AVAUSD": "AVAX-USD",
    "UNIUSD": "UNI-USD",
    "LNKUSD": "LINK-USD",
    "XMRUSD": "XMR-USD",
    "ETCUSD": "ETC-USD",
    "BCHUSD": "BCH-USD",
    "XTZUSD": "XTZ-USD",
    "ALGOUSD": "ALGO-USD",
    "AAVEUSD": "AAVE-USD",
    "NEOUSD": "NEO-USD",
    "DASHUSD": "DASH-USD",
    "ICPUSD": "ICP-USD",
    "GRTUSD": "GRT-USD",
    "IMXUSD": "IMX-USD",
    "GALUSD": "GAL-USD",
    "FETUSD": "FET-USD",
    "NERUSD": "NMR-USD",
    "SANUSD": "SAN-USD",
    "BARUSD": "BAR-USD",
    "MANUSD": "MANA-USD",
    "VECUSD": "VET-USD",
    
    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------
    "AAPL": "AAPL",
    "AMZN": "AMZN",
    "GOOG": "GOOGL",
    "MSFT": "MSFT",
    "META": "META",
    "NFLX": "NFLX",
    "NVDA": "NVDA",
    "TSLA": "TSLA",
    "BABA": "BABA",
    "BAC": "BAC",
    "PFE": "PFE",
    "T": "T",
    "V": "V",
    "WMT": "WMT",
    "ZM": "ZM",
    "RACE": "RACE",
    "LVMH": "MC.PA",
    "AIRF": "AF.PA",
    "ALVG": "ALV.DE",
    "BAYGn": "BAYN.DE",
    "DBKGn": "DBK.DE",
    "IBE": "IBE.MC",
    "VOWG_p": "VOW3.DE",
}

YFINANCE_TO_FTMO: Dict[str, str] = {v: k for k, v in FTMO_TO_YFINANCE.items()}


# =============================================================================
# UNIVERS PAR CLASSE D'ACTIFS (symboles FTMO)
# =============================================================================

FTMO_FOREX: List[str] = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "NZDUSD", "USDCAD",
    "EURGBP", "EURJPY", "EURCHF", "EURAUD", "EURNZD", "EURCAD",
    "GBPJPY", "GBPCHF", "GBPAUD", "GBPNZD", "GBPCAD",
    "AUDJPY", "AUDNZD", "AUDCAD", "AUDCHF",
    "NZDJPY", "NZDCAD", "NZDCHF",
    "CADJPY", "CADCHF", "CHFJPY",
    "USDMXN", "USDZAR", "USDNOK", "USDSEK", "USDPLN", "USDHUF",
    "EURNOK", "EURPLN", "EURHUF", "EURCZK",
]

FTMO_INDICES: List[str] = [
    "US500.cash", "US100.cash", "US30.cash", "US2000.cash",
    "GER40.cash", "UK100.cash", "FRA40.cash", "EU50.cash",
    "JP225.cash", "AUS200.cash", "HK50.cash",
    "SPN35.cash", "N25.cash",
]

FTMO_METALS: List[str] = [
    "XAUUSD", "XAGUSD", "XPTUSD", "XPDUSD", "XCUUSD",
]

FTMO_COMMODITIES: List[str] = [
    "USOIL.cash", "UKOIL.cash", "NATGAS.cash",
    "COCOA.c", "COFFEE.c", "CORN.c", "COTTON.c",
    "SOYBEAN.c", "SUGAR.c", "WHEAT.c",
]

FTMO_CRYPTO: List[str] = [
    "BTCUSD", "ETHUSD", "LTCUSD", "XRPUSD", "ADAUSD",
    "SOLUSD", "BNBUSD", "DOGEUSD", "AVAUSD", "DOTUSD",
    "UNIUSD", "LNKUSD", "BCHUSD", "ETCUSD",
]

FTMO_STOCKS: List[str] = [
    "AAPL", "AMZN", "GOOG", "MSFT", "META", "NFLX", "NVDA", "TSLA",
    "BABA", "BAC", "PFE", "V", "WMT",
]


# =============================================================================
# PAIRES PRÉ-DÉFINIES POUR COÏNTÉGRATION (symboles FTMO)
# =============================================================================

PREDEFINED_PAIRS: List[Tuple[str, str]] = [
    # --- INDICES US ---
    ("US500.cash", "US100.cash"),
    ("US500.cash", "US30.cash"),
    ("US100.cash", "US30.cash"),
    ("US500.cash", "US2000.cash"),
    
    # --- INDICES EUROPE ---
    ("GER40.cash", "FRA40.cash"),
    ("GER40.cash", "EU50.cash"),
    ("UK100.cash", "GER40.cash"),
    
    # --- FOREX ---
    ("EURUSD", "GBPUSD"),
    ("AUDUSD", "NZDUSD"),
    ("EURGBP", "EURJPY"),
    ("GBPJPY", "EURJPY"),
    ("AUDNZD", "AUDCAD"),
    
    # --- MÉTAUX ---
    ("XAUUSD", "XAGUSD"),
    ("XPTUSD", "XPDUSD"),
    
    # --- ENERGIE ---
    ("USOIL.cash", "UKOIL.cash"),
    
    # --- COMMODITIES AGRICOLES ---
    ("CORN.c", "WHEAT.c"),
    ("CORN.c", "SOYBEAN.c"),
    
    # --- CRYPTO ---
    ("BTCUSD", "ETHUSD"),
    ("ETHUSD", "SOLUSD"),
    
    # --- ACTIONS ---
    ("AAPL", "MSFT"),
    ("GOOG", "META"),
]


# =============================================================================
# CONFIGURATION DES MODULES
# =============================================================================

@dataclass
class DataConfig:
    primary_source: str = "yfinance"
    ccxt_exchange: str = "binance"
    timeframe: str = "1d"
    lookback_days: int = 365
    signal_timeframe: str = "4h"
    cache_dir: Path = Path("./data_cache")


@dataclass
class CointegrationConfig:
    pvalue_threshold: float = 0.05
    pvalue_exit_threshold: float = 0.10
    breakdown_checks: int = 3
    rolling_window: int = 252
    min_half_life: int = 5
    max_half_life: int = 50
    hedge_ratio_drift_threshold: float = 0.20


@dataclass
class SignalConfig:
    zscore_entry: float = 2.0
    zscore_exit: float = 1.0
    zscore_stop: float = 3.0
    scale_in: bool = True
    scale_levels: List[float] = field(default_factory=lambda: [2.0, 2.5, 3.0])
    scale_weights: List[float] = field(default_factory=lambda: [0.4, 0.35, 0.25])
    max_holding_multiplier: float = 2.0
    alert_cooldown_minutes: int = 5


@dataclass
class RiskConfig:
    risk_per_trade: float = 0.02
    max_active_pairs: int = 20
    daily_loss_limit: float = 0.03
    max_sector_concentration: float = 0.30
    kelly_fraction: float = 0.5


@dataclass
class AlertConfig:
    telegram_enabled: bool = True
    telegram_bot_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    telegram_chat_id: str = field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", ""))
    discord_enabled: bool = False
    discord_webhook_url: str = field(default_factory=lambda: os.getenv("DISCORD_WEBHOOK_URL", ""))
    ntfy_enabled: bool = True
    ntfy_topic: str = field(default_factory=lambda: os.getenv("NTFY_TOPIC", ""))
    ntfy_server: str = field(default_factory=lambda: os.getenv("NTFY_SERVER", "https://ntfy.sh"))


@dataclass
class TradingConfig:
    """Configuration du compte de trading FTMO."""
    account_size: float = field(default_factory=lambda: float(os.getenv("FTMO_ACCOUNT_SIZE", "100000")))
    risk_per_trade: float = field(default_factory=lambda: float(os.getenv("FTMO_RISK_PER_TRADE", "0.015")))
    max_daily_risk: float = field(default_factory=lambda: float(os.getenv("FTMO_MAX_DAILY_RISK", "0.04")))
    
    # Pip values approximatives pour les paires majeures (1 lot standard)
    # Ces valeurs sont en USD pour 1 pip de mouvement avec 1 lot
    pip_values: dict = field(default_factory=lambda: {
        # Forex (1 lot = 100,000 unités)
        "EURUSD": 10.0, "GBPUSD": 10.0, "AUDUSD": 10.0, "NZDUSD": 10.0,
        "USDCHF": 10.0, "USDCAD": 10.0, "USDJPY": 6.5,
        "EURJPY": 6.5, "GBPJPY": 6.5, "AUDJPY": 6.5, "CADJPY": 6.5, "NZDJPY": 6.5,
        "EURGBP": 12.5, "EURAUD": 6.5, "EURNZD": 6.0, "EURCHF": 10.5,
        "GBPAUD": 6.5, "GBPNZD": 6.0, "GBPCAD": 7.5, "GBPCHF": 10.5,
        "AUDNZD": 6.0, "AUDCAD": 7.5, "AUDCHF": 10.5,
        "NZDCAD": 7.5, "NZDCHF": 10.5, "CADCHF": 10.5,
        # Indices (valeur par point, varie selon broker)
        "US500.cash": 10.0, "US100.cash": 10.0, "US30.cash": 10.0,
        "UK100.cash": 10.0, "GER40.cash": 10.0, "FRA40.cash": 10.0,
        "EU50.cash": 10.0, "SPN35.cash": 10.0, "HK50.cash": 10.0,
        # Métaux (1 lot = 100 oz pour or, 5000 oz pour argent)
        "XAUUSD": 10.0, "XAGUSD": 50.0,
        # Crypto (varie énormément)
        "BTCUSD": 1.0, "ETHUSD": 1.0,
    })
    
    def get_pip_value(self, symbol: str) -> float:
        """Retourne la valeur du pip pour un symbole."""
        return self.pip_values.get(symbol, 10.0)  # Défaut 10 USD
    
    def calculate_position_size(self, symbol1: str, symbol2: str, hedge_ratio: float, spread_std: float) -> dict:
        """
        Calcule la taille de position basée sur le risque.
        
        Args:
            symbol1: Premier symbole
            symbol2: Second symbole
            hedge_ratio: Ratio de hedge
            spread_std: Écart-type du spread (en unités de prix)
        
        Returns:
            dict avec lots1, lots2, risk_amount
        """
        risk_amount = self.account_size * self.risk_per_trade
        
        # Le risque est basé sur 1 écart-type de mouvement du spread
        # Stop loss à z=3 quand entry à z=2 = 1 écart-type
        pip_value1 = self.get_pip_value(symbol1)
        pip_value2 = self.get_pip_value(symbol2)
        
        # Simplification: on considère le risque principalement sur la leg 1
        # car c'est généralement la plus grosse position
        if spread_std > 0 and pip_value1 > 0:
            lots1 = risk_amount / (spread_std * pip_value1 * 100)  # *100 car spread_std en prix
            lots1 = round(lots1, 2)
            lots1 = max(0.01, min(lots1, 50.0))  # Min 0.01, max 50 lots FTMO
        else:
            lots1 = 0.10  # Défaut conservateur
        
        lots2 = round(abs(lots1 * hedge_ratio), 2)
        lots2 = max(0.01, min(lots2, 50.0))
        
        return {
            "lots1": lots1,
            "lots2": lots2,
            "risk_amount": risk_amount,
            "risk_percent": self.risk_per_trade * 100
        }


@dataclass
class SchedulerConfig:
    zscore_check_interval: int = 5
    daily_recalibration_time: str = "06:00"
    weekly_scan_day: int = 6
    weekly_scan_time: str = "18:00"


@dataclass
class DatabaseConfig:
    db_path: Path = Path("./pairs_trading.db")
    backup_enabled: bool = True
    backup_dir: Path = Path("./backups")


@dataclass
class Config:
    data: DataConfig = field(default_factory=DataConfig)
    cointegration: CointegrationConfig = field(default_factory=CointegrationConfig)
    signal: SignalConfig = field(default_factory=SignalConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    alert: AlertConfig = field(default_factory=AlertConfig)
    trading: TradingConfig = field(default_factory=TradingConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    def validate(self) -> bool:
        errors = []
        if self.alert.telegram_enabled and not self.alert.telegram_bot_token:
            errors.append("TELEGRAM_BOT_TOKEN manquant")
        if self.alert.discord_enabled and not self.alert.discord_webhook_url:
            errors.append("DISCORD_WEBHOOK_URL manquant")
        if errors:
            for e in errors:
                print(f"⚠️  {e}")
            return False
        return True


config = Config()


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def ftmo_to_yfinance(ftmo_symbol: str) -> str:
    """Convertit un symbole FTMO en symbole yfinance."""
    return FTMO_TO_YFINANCE.get(ftmo_symbol, ftmo_symbol)


def yfinance_to_ftmo(yf_symbol: str) -> str:
    """Convertit un symbole yfinance en symbole FTMO."""
    return YFINANCE_TO_FTMO.get(yf_symbol, yf_symbol)


def get_all_ftmo_symbols() -> List[str]:
    """Retourne tous les symboles FTMO disponibles."""
    return list(FTMO_TO_YFINANCE.keys())


def get_yfinance_symbols(ftmo_symbols: List[str]) -> List[str]:
    """Convertit une liste de symboles FTMO en symboles yfinance."""
    return [ftmo_to_yfinance(s) for s in ftmo_symbols]


if __name__ == "__main__":
    print(f"Total FTMO symbols: {len(FTMO_TO_YFINANCE)}")
    print(f"Forex: {len(FTMO_FOREX)}")
    print(f"Indices: {len(FTMO_INDICES)}")
    print(f"Metals: {len(FTMO_METALS)}")
    print(f"Commodities: {len(FTMO_COMMODITIES)}")
    print(f"Crypto: {len(FTMO_CRYPTO)}")
    print(f"Stocks: {len(FTMO_STOCKS)}")
    print(f"\nPredefined pairs: {len(PREDEFINED_PAIRS)}")
    
    print("\n=== Test conversions ===")
    for ftmo in ["US500.cash", "EURUSD", "XAUUSD", "BTCUSD"]:
        yf = ftmo_to_yfinance(ftmo)
        print(f"  {ftmo} -> {yf}")
