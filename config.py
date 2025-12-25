"""
Configuration du système de Pairs Trading par Coïntégration
============================================================
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


@dataclass
class DataConfig:
    """Configuration des sources de données."""
    primary_source: str = "yfinance"
    ccxt_exchange: str = "binance"
    timeframe: str = "1d"
    lookback_days: int = 365
    signal_timeframe: str = "4h"
    cache_dir: Path = Path("./data_cache")


@dataclass
class CointegrationConfig:
    """Paramètres des tests de coïntégration."""
    pvalue_threshold: float = 0.05
    pvalue_exit_threshold: float = 0.10
    breakdown_checks: int = 3
    rolling_window: int = 252
    min_half_life: int = 5
    max_half_life: int = 50
    hedge_ratio_drift_threshold: float = 0.20


@dataclass
class SignalConfig:
    """Paramètres de génération des signaux."""
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
    """Paramètres de gestion du risque."""
    risk_per_trade: float = 0.02
    max_active_pairs: int = 20
    daily_loss_limit: float = 0.03
    max_sector_concentration: float = 0.30
    kelly_fraction: float = 0.5


@dataclass
class AlertConfig:
    """Configuration des alertes."""
    telegram_enabled: bool = True
    telegram_bot_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    telegram_chat_id: str = field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", ""))
    discord_enabled: bool = False
    discord_webhook_url: str = field(default_factory=lambda: os.getenv("DISCORD_WEBHOOK_URL", ""))


@dataclass
class SchedulerConfig:
    """Configuration du scheduler."""
    zscore_check_interval: int = 5
    daily_recalibration_time: str = "06:00"
    weekly_scan_day: int = 6
    weekly_scan_time: str = "18:00"


@dataclass
class DatabaseConfig:
    """Configuration de la base de données."""
    db_path: Path = Path("./pairs_trading.db")
    backup_enabled: bool = True
    backup_dir: Path = Path("./backups")


# =============================================================================
# UNIVERS D'INSTRUMENTS
# =============================================================================

FOREX_UNIVERSE: List[str] = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X",
    "AUDUSD=X", "NZDUSD=X", "USDCAD=X",
    "EURGBP=X", "EURJPY=X", "EURCHF=X",
    "GBPJPY=X", "GBPCHF=X",
    "AUDNZD=X", "AUDCAD=X", "NZDCAD=X",
]

INDICES_UNIVERSE: List[str] = [
    "SPY", "QQQ", "DIA", "IWM",
    "EWG", "EWU", "EWQ",
    "EWJ", "FXI", "EWH",
]

COMMODITIES_UNIVERSE: List[str] = [
    "GLD", "SLV", "USO", "BNO", "UNG", "CPER",
]

SECTORS_UNIVERSE: Dict[str, List[str]] = {
    "tech": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "AMD", "INTC"],
    "finance": ["JPM", "BAC", "GS", "MS", "C", "WFC"],
    "energy": ["XOM", "CVX", "COP", "SLB", "EOG"],
    "healthcare": ["JNJ", "PFE", "UNH", "MRK", "ABBV"],
}

CRYPTO_UNIVERSE: List[str] = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT",
    "XRP/USDT", "ADA/USDT", "DOGE/USDT", "AVAX/USDT",
    "DOT/USDT", "LINK/USDT", "MATIC/USDT", "LTC/USDT",
]

PREDEFINED_PAIRS: List[tuple] = [
    ("EURUSD=X", "GBPUSD=X"),
    ("AUDUSD=X", "NZDUSD=X"),
    ("GLD", "SLV"),
    ("USO", "BNO"),
    ("SPY", "QQQ"),
    ("SPY", "IWM"),
    ("XOM", "CVX"),
    ("JPM", "BAC"),
]


@dataclass
class Config:
    """Configuration globale."""
    data: DataConfig = field(default_factory=DataConfig)
    cointegration: CointegrationConfig = field(default_factory=CointegrationConfig)
    signal: SignalConfig = field(default_factory=SignalConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    alert: AlertConfig = field(default_factory=AlertConfig)
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
