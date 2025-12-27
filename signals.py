"""
Signal Generator - Machine à états et génération de signaux
============================================================
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, NamedTuple
from enum import Enum
from dataclasses import dataclass, field
from loguru import logger

from config import config
from cointegration import CointegrationResult, CointegrationAnalyzer


class PositionState(Enum):
    """États possibles d'une position."""
    FLAT = "flat"
    LONG_SPREAD = "long_spread"    # Long asset1, Short asset2
    SHORT_SPREAD = "short_spread"  # Short asset1, Long asset2


class SignalType(Enum):
    """Types de signaux."""
    NO_SIGNAL = "no_signal"
    OPEN_LONG_SPREAD = "open_long_spread"
    OPEN_SHORT_SPREAD = "open_short_spread"
    CLOSE_LONG_SPREAD = "close_long_spread"
    CLOSE_SHORT_SPREAD = "close_short_spread"
    WARNING = "warning"  # z-score proche du stop (±2.5)
    STOP_LOSS = "stop_loss"
    TIME_EXIT = "time_exit"
    BREAKDOWN_EXIT = "breakdown_exit"
    SCALE_IN_LONG = "scale_in_long"
    SCALE_IN_SHORT = "scale_in_short"


@dataclass
class Signal:
    """Représentation d'un signal de trading."""
    signal_type: SignalType
    pair_id: str
    symbol1: str
    symbol2: str
    zscore: float
    hedge_ratio: float
    timestamp: datetime
    price1: Optional[float] = None
    price2: Optional[float] = None
    reason: str = ""
    scale_level: int = 0  # Niveau de scaling (1, 2, 3...)
    half_life: float = 10.0  # Half-life par défaut
    
    def to_dict(self) -> dict:
        return {
            "signal_type": self.signal_type.value,
            "pair_id": self.pair_id,
            "symbol1": self.symbol1,
            "symbol2": self.symbol2,
            "zscore": round(self.zscore, 3),
            "hedge_ratio": round(self.hedge_ratio, 4),
            "timestamp": self.timestamp.isoformat(),
            "price1": self.price1,
            "price2": self.price2,
            "reason": self.reason,
        }
    
    def format_message(self) -> str:
        """Formate le signal pour affichage/notification."""
        emoji_map = {
            SignalType.OPEN_LONG_SPREAD: "🟢",
            SignalType.OPEN_SHORT_SPREAD: "🔴",
            SignalType.CLOSE_LONG_SPREAD: "✅",
            SignalType.CLOSE_SHORT_SPREAD: "✅",
            SignalType.STOP_LOSS: "🛑",
            SignalType.TIME_EXIT: "⏰",
            SignalType.BREAKDOWN_EXIT: "⚠️",
            SignalType.SCALE_IN_LONG: "📈",
            SignalType.SCALE_IN_SHORT: "📉",
        }
        emoji = emoji_map.get(self.signal_type, "📊")
        
        lines = [
            f"{emoji} **{self.signal_type.value.upper()}**",
            f"Pair: {self.symbol1} / {self.symbol2}",
            f"Z-Score: {self.zscore:.2f}",
            f"Hedge Ratio: {self.hedge_ratio:.4f}",
        ]
        
        if self.price1 and self.price2:
            lines.append(f"Prices: {self.price1:.4f} / {self.price2:.4f}")
        
        if self.reason:
            lines.append(f"Reason: {self.reason}")
        
        lines.append(f"Time: {self.timestamp.strftime('%Y-%m-%d %H:%M')}")
        
        return "\n".join(lines)


@dataclass
class PairPosition:
    """État d'une position sur une paire."""
    pair_id: str
    symbol1: str
    symbol2: str
    state: PositionState = PositionState.FLAT
    entry_zscore: float = 0.0
    entry_hedge_ratio: float = 0.0
    entry_time: Optional[datetime] = None
    entry_price1: Optional[float] = None
    entry_price2: Optional[float] = None
    scale_level: int = 0
    half_life: float = 20.0
    breakdown_count: int = 0
    last_signal_time: Optional[datetime] = None


class SignalGenerator:
    """Générateur de signaux pour pairs trading."""
    
    def __init__(self):
        self.config = config.signal
        self.positions: Dict[str, PairPosition] = {}
        self.analyzer = CointegrationAnalyzer()
    
    def get_or_create_position(self, pair_id: str, symbol1: str, symbol2: str) -> PairPosition:
        """Récupère ou crée une position pour une paire."""
        if pair_id not in self.positions:
            self.positions[pair_id] = PairPosition(
                pair_id=pair_id,
                symbol1=symbol1,
                symbol2=symbol2
            )
        return self.positions[pair_id]
    
    def calculate_current_zscore(
        self,
        series1: pd.Series,
        series2: pd.Series,
        hedge_ratio: float,
        lookback: int = 20
    ) -> float:
        """Calcule le z-score actuel du spread."""
        spread = series1 - hedge_ratio * series2
        
        if len(spread) < lookback:
            lookback = len(spread)
        
        recent_spread = spread.iloc[-lookback:]
        mean = recent_spread.mean()
        std = recent_spread.std()
        
        if std == 0:
            return 0.0
        
        current_zscore = (spread.iloc[-1] - mean) / std
        return current_zscore
    
    def check_entry_conditions(
        self,
        position: PairPosition,
        current_zscore: float,
        coint_result: CointegrationResult
    ) -> Optional[Signal]:
        """Vérifie les conditions d'entrée."""
        
        if position.state != PositionState.FLAT:
            return None
        
        if not coint_result.is_cointegrated:
            return None
        
        now = datetime.now()
        
        # Cooldown check
        if position.last_signal_time:
            cooldown = timedelta(minutes=self.config.alert_cooldown_minutes)
            if now - position.last_signal_time < cooldown:
                return None
        
        # Entry conditions
        if current_zscore <= -self.config.zscore_entry:
            return Signal(
                signal_type=SignalType.OPEN_LONG_SPREAD,
                pair_id=position.pair_id,
                symbol1=position.symbol1,
                symbol2=position.symbol2,
                zscore=current_zscore,
                hedge_ratio=coint_result.hedge_ratio,
                timestamp=now,
                reason=f"Z-score {current_zscore:.2f} <= -{self.config.zscore_entry}",
                scale_level=1,
                half_life=coint_result.half_life
            )
        
        elif current_zscore >= self.config.zscore_entry:
            return Signal(
                signal_type=SignalType.OPEN_SHORT_SPREAD,
                pair_id=position.pair_id,
                symbol1=position.symbol1,
                symbol2=position.symbol2,
                zscore=current_zscore,
                hedge_ratio=coint_result.hedge_ratio,
                timestamp=now,
                reason=f"Z-score {current_zscore:.2f} >= {self.config.zscore_entry}",
                scale_level=1,
                half_life=coint_result.half_life
            )
        
        return None
    
    def check_exit_conditions(
        self,
        position: PairPosition,
        current_zscore: float,
        coint_result: Optional[CointegrationResult] = None
    ) -> Optional[Signal]:
        """Vérifie les conditions de sortie."""
        
        if position.state == PositionState.FLAT:
            return None
        
        now = datetime.now()
        
        # Stop-loss
        if abs(current_zscore) >= self.config.zscore_stop:
            return Signal(
                signal_type=SignalType.STOP_LOSS,
                pair_id=position.pair_id,
                symbol1=position.symbol1,
                symbol2=position.symbol2,
                zscore=current_zscore,
                hedge_ratio=position.entry_hedge_ratio,
                timestamp=now,
                reason=f"Stop-loss at z-score {current_zscore:.2f}"
            )
        
        # Time exit
        if position.entry_time:
            max_holding = position.half_life * self.config.max_holding_multiplier
            holding_days = (now - position.entry_time).days
            if holding_days > max_holding:
                return Signal(
                    signal_type=SignalType.TIME_EXIT,
                    pair_id=position.pair_id,
                    symbol1=position.symbol1,
                    symbol2=position.symbol2,
                    zscore=current_zscore,
                    hedge_ratio=position.entry_hedge_ratio,
                    timestamp=now,
                    reason=f"Max holding time exceeded ({holding_days} > {max_holding:.0f} days)"
                )
        
        # Mean reversion exit
        if position.state == PositionState.LONG_SPREAD:
            if current_zscore >= -self.config.zscore_exit:
                return Signal(
                    signal_type=SignalType.CLOSE_LONG_SPREAD,
                    pair_id=position.pair_id,
                    symbol1=position.symbol1,
                    symbol2=position.symbol2,
                    zscore=current_zscore,
                    hedge_ratio=position.entry_hedge_ratio,
                    timestamp=now,
                    reason=f"Mean reversion: z-score {current_zscore:.2f}"
                )
        
        elif position.state == PositionState.SHORT_SPREAD:
            if current_zscore <= self.config.zscore_exit:
                return Signal(
                    signal_type=SignalType.CLOSE_SHORT_SPREAD,
                    pair_id=position.pair_id,
                    symbol1=position.symbol1,
                    symbol2=position.symbol2,
                    zscore=current_zscore,
                    hedge_ratio=position.entry_hedge_ratio,
                    timestamp=now,
                    reason=f"Mean reversion: z-score {current_zscore:.2f}"
                )
        
        # Breakdown exit
        if coint_result and not coint_result.is_cointegrated:
            position.breakdown_count += 1
            if position.breakdown_count >= config.cointegration.breakdown_checks:
                return Signal(
                    signal_type=SignalType.BREAKDOWN_EXIT,
                    pair_id=position.pair_id,
                    symbol1=position.symbol1,
                    symbol2=position.symbol2,
                    zscore=current_zscore,
                    hedge_ratio=position.entry_hedge_ratio,
                    timestamp=now,
                    reason=f"Cointegration breakdown (p-value: {coint_result.pvalue:.3f})"
                )
        else:
            position.breakdown_count = 0
        
        return None
    
    def check_scale_in(
        self,
        position: PairPosition,
        current_zscore: float
    ) -> Optional[Signal]:
        """Vérifie les opportunités de scaling."""
        
        if not self.config.scale_in:
            return None
        
        if position.state == PositionState.FLAT:
            return None
        
        if position.scale_level >= len(self.config.scale_levels):
            return None
        
        next_level = position.scale_level
        next_threshold = self.config.scale_levels[next_level]
        now = datetime.now()
        
        if position.state == PositionState.LONG_SPREAD:
            if current_zscore <= -next_threshold:
                return Signal(
                    signal_type=SignalType.SCALE_IN_LONG,
                    pair_id=position.pair_id,
                    symbol1=position.symbol1,
                    symbol2=position.symbol2,
                    zscore=current_zscore,
                    hedge_ratio=position.entry_hedge_ratio,
                    timestamp=now,
                    reason=f"Scale-in level {next_level + 1} at z-score {current_zscore:.2f}",
                    scale_level=next_level + 1
                )
        
        elif position.state == PositionState.SHORT_SPREAD:
            if current_zscore >= next_threshold:
                return Signal(
                    signal_type=SignalType.SCALE_IN_SHORT,
                    pair_id=position.pair_id,
                    symbol1=position.symbol1,
                    symbol2=position.symbol2,
                    zscore=current_zscore,
                    hedge_ratio=position.entry_hedge_ratio,
                    timestamp=now,
                    reason=f"Scale-in level {next_level + 1} at z-score {current_zscore:.2f}",
                    scale_level=next_level + 1
                )
        
        return None
    
    def update_position_state(self, position: PairPosition, signal: Signal):
        """Met à jour l'état de la position après un signal."""
        
        if signal.signal_type in [SignalType.OPEN_LONG_SPREAD]:
            position.state = PositionState.LONG_SPREAD
            position.entry_zscore = signal.zscore
            position.entry_hedge_ratio = signal.hedge_ratio
            position.entry_time = signal.timestamp
            position.entry_price1 = signal.price1
            position.entry_price2 = signal.price2
            position.scale_level = 1
        
        elif signal.signal_type in [SignalType.OPEN_SHORT_SPREAD]:
            position.state = PositionState.SHORT_SPREAD
            position.entry_zscore = signal.zscore
            position.entry_hedge_ratio = signal.hedge_ratio
            position.entry_time = signal.timestamp
            position.entry_price1 = signal.price1
            position.entry_price2 = signal.price2
            position.scale_level = 1
        
        elif signal.signal_type in [
            SignalType.CLOSE_LONG_SPREAD,
            SignalType.CLOSE_SHORT_SPREAD,
            SignalType.STOP_LOSS,
            SignalType.TIME_EXIT,
            SignalType.BREAKDOWN_EXIT
        ]:
            position.state = PositionState.FLAT
            position.scale_level = 0
            position.breakdown_count = 0
        
        elif signal.signal_type in [SignalType.SCALE_IN_LONG, SignalType.SCALE_IN_SHORT]:
            position.scale_level = signal.scale_level
        
        position.last_signal_time = signal.timestamp
    
    def generate_signal(
        self,
        pair_id: str,
        symbol1: str,
        symbol2: str,
        series1: pd.Series,
        series2: pd.Series,
        coint_result: CointegrationResult,
        current_price1: Optional[float] = None,
        current_price2: Optional[float] = None
    ) -> Optional[Signal]:
        """
        Génère un signal pour une paire.
        
        Returns:
            Signal si une action est requise, None sinon
        """
        position = self.get_or_create_position(pair_id, symbol1, symbol2)
        position.half_life = coint_result.half_life
        
        # Lookback basé sur le half-life
        lookback = max(int(coint_result.half_life / 2), 10)
        
        current_zscore = self.calculate_current_zscore(
            series1, series2,
            coint_result.hedge_ratio,
            lookback
        )
        
        # Ordre de priorité: Exit > Scale-in > Entry
        signal = self.check_exit_conditions(position, current_zscore, coint_result)
        
        if signal is None:
            signal = self.check_scale_in(position, current_zscore)
        
        if signal is None:
            signal = self.check_entry_conditions(position, current_zscore, coint_result)
        
        if signal:
            signal.price1 = current_price1
            signal.price2 = current_price2
            self.update_position_state(position, signal)
            logger.info(f"Signal generated: {signal.signal_type.value} for {pair_id}")
        
        return signal
    
    def get_all_positions(self) -> List[PairPosition]:
        """Retourne toutes les positions actives."""
        return [p for p in self.positions.values() if p.state != PositionState.FLAT]
    
    def get_position_summary(self) -> Dict:
        """Retourne un résumé des positions."""
        active = self.get_all_positions()
        return {
            "total_pairs": len(self.positions),
            "active_positions": len(active),
            "long_spread": len([p for p in active if p.state == PositionState.LONG_SPREAD]),
            "short_spread": len([p for p in active if p.state == PositionState.SHORT_SPREAD]),
        }


if __name__ == "__main__":
    import sys
    logger.remove()
    logger.add(sys.stdout, level="INFO")
    
    # Test avec données simulées
    np.random.seed(42)
    n = 200
    
    x = np.cumsum(np.random.randn(n)) + 100
    y = 0.8 * x + np.cumsum(np.random.randn(n) * 0.3) + 50
    
    dates = pd.date_range("2024-01-01", periods=n)
    series1 = pd.Series(x, index=dates)
    series2 = pd.Series(y, index=dates)
    
    # Test cointegration
    from cointegration import CointegrationAnalyzer
    analyzer = CointegrationAnalyzer()
    coint_result = analyzer.test_engle_granger(series1, series2, "Asset1", "Asset2")
    
    print(f"Cointegrated: {coint_result.is_cointegrated}")
    print(f"Half-life: {coint_result.half_life:.1f}")
    
    # Test signal generator
    generator = SignalGenerator()
    
    signal = generator.generate_signal(
        pair_id="Asset1_Asset2",
        symbol1="Asset1",
        symbol2="Asset2",
        series1=series1,
        series2=series2,
        coint_result=coint_result,
        current_price1=series1.iloc[-1],
        current_price2=series2.iloc[-1]
    )
    
    if signal:
        print("\n=== Signal Generated ===")
        print(signal.format_message())
    else:
        print("\nNo signal generated")
    
    print("\n=== Position Summary ===")
    print(generator.get_position_summary())
