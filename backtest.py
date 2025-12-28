"""
Backtesting Module - Pairs Trading par Coïntégration
=====================================================
Simulation historique des trades pour valider la stratégie.

Version: 1.1.0
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json

from loguru import logger
from statsmodels.tsa.stattools import coint, adfuller
import statsmodels.api as sm

from config import config
from data_fetcher import DataFetcher
from cointegration import CointegrationAnalyzer, CointegrationResult


@dataclass
class Trade:
    """Représentation d'un trade."""
    entry_date: datetime
    exit_date: Optional[datetime]
    pair_id: str
    symbol1: str
    symbol2: str
    direction: str  # "long_spread" ou "short_spread"
    entry_zscore: float
    exit_zscore: Optional[float]
    entry_spread: float
    exit_spread: Optional[float]
    hedge_ratio: float
    entry_spread_std: float = 1.0  # Spread std au moment de l'entrée (pour P&L)
    pnl_spread_units: Optional[float] = None  # P&L en unités de spread
    pnl_percent: Optional[float] = None  # P&L en % du risque
    exit_reason: Optional[str] = None  # "tp", "sl", "time", "breakdown"
    holding_days: Optional[int] = None
    
    @property
    def is_open(self) -> bool:
        return self.exit_date is None
    
    @property
    def is_winner(self) -> bool:
        if self.pnl_percent is None:
            return False
        return self.pnl_percent > 0


@dataclass
class BacktestResult:
    """Résultats du backtest."""
    pair_id: str
    symbol1: str
    symbol2: str
    start_date: datetime
    end_date: datetime
    
    # Paramètres utilisés
    zscore_entry: float
    zscore_exit: float
    zscore_stop: float
    max_holding_days: int
    
    # Métriques de base
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    
    # P&L
    total_pnl_percent: float = 0.0
    avg_pnl_percent: float = 0.0
    max_win_percent: float = 0.0
    max_loss_percent: float = 0.0
    
    # Ratios
    win_rate: float = 0.0
    profit_factor: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    expectancy: float = 0.0  # E = WR × AvgWin - (1-WR) × AvgLoss
    
    # Drawdown
    max_drawdown_percent: float = 0.0
    
    # Timing
    avg_holding_days: float = 0.0
    max_holding_days_actual: int = 0
    
    # Exits breakdown
    exits_tp: int = 0
    exits_sl: int = 0
    exits_time: int = 0
    exits_breakdown: int = 0
    
    # Cointegration
    avg_half_life: float = 0.0
    cointegration_periods: int = 0  # Périodes où la paire était coïntégrée
    
    # Liste des trades
    trades: List[Trade] = field(default_factory=list)
    
    # Equity curve
    equity_curve: List[float] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire (sans les trades détaillés)."""
        return {
            "pair_id": self.pair_id,
            "symbol1": self.symbol1,
            "symbol2": self.symbol2,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": round(self.win_rate * 100, 1),
            "profit_factor": round(self.profit_factor, 2),
            "expectancy": round(self.expectancy, 2),
            "total_pnl_percent": round(self.total_pnl_percent, 1),
            "avg_pnl_percent": round(self.avg_pnl_percent, 2),
            "max_win_percent": round(self.max_win_percent, 1),
            "max_loss_percent": round(self.max_loss_percent, 1),
            "max_drawdown_percent": round(self.max_drawdown_percent, 1),
            "avg_holding_days": round(self.avg_holding_days, 1),
            "exits_tp": self.exits_tp,
            "exits_sl": self.exits_sl,
            "exits_time": self.exits_time,
            "avg_half_life": round(self.avg_half_life, 1),
        }


class PairsBacktester:
    """Backtester pour le pairs trading."""
    
    def __init__(
        self,
        zscore_entry: float = 1.5,
        zscore_exit: float = 1.0,
        zscore_stop: float = 3.0,
        max_holding_multiplier: float = 2.0,
        lookback_days: int = 365,
        cointegration_lookback: int = 120,  # Fenêtre pour test cointegration (plus courte)
        min_half_life: int = 3,  # Plus permissif
        max_half_life: int = 60,  # Plus permissif
        recalibration_days: int = 14,  # Recalibrer plus souvent
        pvalue_threshold: float = 0.05,
    ):
        self.zscore_entry = zscore_entry
        self.zscore_exit = zscore_exit
        self.zscore_stop = zscore_stop
        self.max_holding_multiplier = max_holding_multiplier
        self.lookback_days = lookback_days
        self.cointegration_lookback = cointegration_lookback
        self.min_half_life = min_half_life
        self.max_half_life = max_half_life
        self.recalibration_days = recalibration_days
        self.pvalue_threshold = pvalue_threshold
        
        self.fetcher = DataFetcher()
        self.analyzer = CointegrationAnalyzer()
    
    def _test_cointegration(
        self,
        series1: pd.Series,
        series2: pd.Series,
        symbol1: str = "Asset1",
        symbol2: str = "Asset2"
    ) -> CointegrationResult:
        """
        Test de coïntégration avec les paramètres du backtest.
        Utilise min_half_life et max_half_life du backtester, pas de la config globale.
        """
        # Test de coïntégration statsmodels
        score, pvalue, _ = coint(series1, series2)
        
        # Calcul du hedge ratio via OLS
        X = sm.add_constant(series2)
        model = sm.OLS(series1, X).fit()
        hedge_ratio = model.params.iloc[1] if len(model.params) > 1 else model.params.iloc[0]
        
        # Calcul du spread
        spread = series1 - hedge_ratio * series2
        
        # Half-life de mean reversion (Ornstein-Uhlenbeck)
        spread_lag = spread.shift(1).dropna()
        spread_diff = spread.diff().dropna()
        
        # Aligner les séries
        spread_lag = spread_lag.iloc[1:]
        spread_diff = spread_diff.iloc[1:]
        
        if len(spread_lag) > 10:
            X_hl = sm.add_constant(spread_lag)
            model_hl = sm.OLS(spread_diff, X_hl).fit()
            lambda_param = model_hl.params.iloc[1] if len(model_hl.params) > 1 else -0.1
            
            if lambda_param < 0:
                half_life = -np.log(2) / lambda_param
            else:
                half_life = 999  # Pas de mean reversion
        else:
            half_life = 999
        
        # Utiliser les paramètres du BACKTESTER, pas de la config globale
        is_cointegrated = (
            pvalue < self.pvalue_threshold and
            self.min_half_life <= half_life <= self.max_half_life
        )
        
        return CointegrationResult(
            symbol1=symbol1,
            symbol2=symbol2,
            is_cointegrated=is_cointegrated,
            pvalue=pvalue,
            hedge_ratio=hedge_ratio,
            half_life=half_life,
            spread_mean=spread.mean(),
            spread_std=spread.std(),
            test_method="engle_granger",
            adf_statistic=0  # Non utilisé ici
        )
    
    def run_backtest(
        self,
        symbol1: str,
        symbol2: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        initial_capital: float = 100000,
        risk_per_trade: float = 0.015,
    ) -> BacktestResult:
        """
        Lance un backtest sur une paire.
        
        Args:
            symbol1: Premier symbole
            symbol2: Second symbole
            start_date: Date de début (défaut: lookback_days avant aujourd'hui)
            end_date: Date de fin (défaut: aujourd'hui)
            initial_capital: Capital initial
            risk_per_trade: Risque par trade (ex: 0.015 = 1.5%)
        
        Returns:
            BacktestResult avec toutes les métriques
        """
        pair_id = f"{symbol1}_{symbol2}"
        logger.info(f"Starting backtest for {pair_id}")
        
        # Dates par défaut
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=self.lookback_days * 2)
        
        # Calculer lookback_days pour le fetcher
        total_days = (end_date - start_date).days + 30  # Marge pour le lookback interne
        
        # Yahoo limite 4h/1h à 730 jours, donc on utilise daily pour backtest long
        # C'est aussi plus approprié pour du pairs trading (moins de bruit)
        timeframe = "1d"
        
        # Récupérer les données via fetch_single
        logger.info(f"Fetching data ({total_days} days, timeframe={timeframe})")
        df1 = self.fetcher.fetch_single(symbol1, lookback_days=total_days, timeframe=timeframe)
        df2 = self.fetcher.fetch_single(symbol2, lookback_days=total_days, timeframe=timeframe)
        
        if df1 is None or df2 is None:
            logger.error(f"Could not fetch data for {pair_id}")
            return self._empty_result(pair_id, symbol1, symbol2, start_date, end_date)
        
        if len(df1) < 100 or len(df2) < 100:
            logger.error(f"Insufficient data for {pair_id}: {len(df1)} / {len(df2)} bars")
            return self._empty_result(pair_id, symbol1, symbol2, start_date, end_date)
        
        # Aligner les données
        df = pd.DataFrame({
            "price1": df1["close"],
            "price2": df2["close"]
        }).dropna()
        
        if len(df) < 200:
            logger.error(f"Not enough aligned data points: {len(df)}")
            return self._empty_result(pair_id, symbol1, symbol2, start_date, end_date)
        
        logger.info(f"Data aligned: {len(df)} bars from {df.index[0]} to {df.index[-1]}")
        
        # Lancer la simulation
        result = self._simulate(
            df=df,
            pair_id=pair_id,
            symbol1=symbol1,
            symbol2=symbol2,
            initial_capital=initial_capital,
            risk_per_trade=risk_per_trade,
        )
        
        return result
    
    def _simulate(
        self,
        df: pd.DataFrame,
        pair_id: str,
        symbol1: str,
        symbol2: str,
        initial_capital: float,
        risk_per_trade: float,
    ) -> BacktestResult:
        """Simulation principale du backtest."""
        
        trades: List[Trade] = []
        current_trade: Optional[Trade] = None
        equity = initial_capital
        equity_curve = [equity]
        peak_equity = equity
        max_drawdown = 0.0
        
        half_lives = []
        cointegration_count = 0
        
        # Paramètres de fenêtre (en barres daily)
        lookback = min(self.cointegration_lookback, len(df) // 3)  # Fenêtre pour cointegration
        recalib_bars = self.recalibration_days  # 1 barre = 1 jour en daily
        
        # Variables de cointegration (recalculées périodiquement)
        hedge_ratio = None
        spread_mean = None
        spread_std = None
        half_life = None
        last_calibration = 0
        is_cointegrated = False
        entry_spread_std = None  # Garder le spread_std à l'entrée pour calcul P&L correct
        
        # Itérer sur les données (en laissant assez de lookback)
        for i in range(lookback, len(df)):
            current_time = df.index[i]
            price1 = df["price1"].iloc[i]
            price2 = df["price2"].iloc[i]
            
            # Recalibrer la cointegration périodiquement
            if i - last_calibration >= recalib_bars or hedge_ratio is None:
                window = df.iloc[i - lookback:i]
                coint_result = self._test_cointegration(
                    window["price1"],
                    window["price2"],
                    symbol1=symbol1,
                    symbol2=symbol2
                )
                
                if coint_result.is_cointegrated:
                    is_cointegrated = True
                    cointegration_count += 1
                    hedge_ratio = coint_result.hedge_ratio
                    half_life = coint_result.half_life
                    half_lives.append(half_life)
                    
                    # Calculer spread stats sur la fenêtre
                    spread = window["price1"] - hedge_ratio * window["price2"]
                    spread_mean = spread.mean()
                    spread_std = spread.std()
                else:
                    is_cointegrated = False
                    
                    # Si on a une position ouverte et breakdown, fermer
                    if current_trade is not None:
                        current_trade = self._close_trade(
                            trade=current_trade,
                            exit_date=current_time,
                            exit_spread=price1 - (hedge_ratio or 1) * price2,
                            exit_zscore=0,  # N/A
                            exit_reason="breakdown",
                            spread_std=spread_std or 1,
                        )
                        trades.append(current_trade)
                        equity += current_trade.pnl_percent * initial_capital * risk_per_trade
                        current_trade = None
                
                last_calibration = i
            
            # Si pas coïntégré, skip
            if not is_cointegrated or hedge_ratio is None or spread_std is None:
                equity_curve.append(equity)
                continue
            
            # Calculer spread et z-score actuels
            current_spread = price1 - hedge_ratio * price2
            zscore = (current_spread - spread_mean) / spread_std
            
            # Max holding days basé sur half-life (en barres daily = jours)
            max_holding_bars = int(half_life * self.max_holding_multiplier)
            
            # Gestion des positions
            if current_trade is None:
                # Pas de position - chercher une entrée
                if zscore <= -self.zscore_entry:
                    # Entry LONG spread (acheter spread = acheter S1, vendre S2)
                    current_trade = Trade(
                        entry_date=current_time,
                        exit_date=None,
                        pair_id=pair_id,
                        symbol1=symbol1,
                        symbol2=symbol2,
                        direction="long_spread",
                        entry_zscore=zscore,
                        exit_zscore=None,
                        entry_spread=current_spread,
                        exit_spread=None,
                        hedge_ratio=hedge_ratio,
                        entry_spread_std=spread_std,  # Capturer le spread_std à l'entrée
                    )
                elif zscore >= self.zscore_entry:
                    # Entry SHORT spread
                    current_trade = Trade(
                        entry_date=current_time,
                        exit_date=None,
                        pair_id=pair_id,
                        symbol1=symbol1,
                        symbol2=symbol2,
                        direction="short_spread",
                        entry_zscore=zscore,
                        exit_zscore=None,
                        entry_spread=current_spread,
                        exit_spread=None,
                        hedge_ratio=hedge_ratio,
                        entry_spread_std=spread_std,  # Capturer le spread_std à l'entrée
                    )
            else:
                # Position ouverte - chercher une sortie
                bars_held = i - df.index.get_loc(current_trade.entry_date)
                exit_reason = None
                
                if current_trade.direction == "long_spread":
                    # Long spread: TP quand z remonte vers 0, SL si descend encore
                    if zscore >= -self.zscore_exit:
                        exit_reason = "tp"
                    elif zscore <= -self.zscore_stop:
                        exit_reason = "sl"
                else:
                    # Short spread: TP quand z descend vers 0, SL si monte encore
                    if zscore <= self.zscore_exit:
                        exit_reason = "tp"
                    elif zscore >= self.zscore_stop:
                        exit_reason = "sl"
                
                # Time exit
                if bars_held >= max_holding_bars:
                    exit_reason = "time"
                
                if exit_reason:
                    current_trade = self._close_trade(
                        trade=current_trade,
                        exit_date=current_time,
                        exit_spread=current_spread,
                        exit_zscore=zscore,
                        exit_reason=exit_reason,
                        spread_std=spread_std,
                    )
                    trades.append(current_trade)
                    
                    # Update equity
                    pnl = current_trade.pnl_percent * initial_capital * risk_per_trade
                    equity += pnl
                    
                    current_trade = None
            
            # Track equity et drawdown
            equity_curve.append(equity)
            if equity > peak_equity:
                peak_equity = equity
            drawdown = (peak_equity - equity) / peak_equity
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Fermer position ouverte à la fin
        if current_trade is not None:
            current_trade = self._close_trade(
                trade=current_trade,
                exit_date=df.index[-1],
                exit_spread=df["price1"].iloc[-1] - hedge_ratio * df["price2"].iloc[-1],
                exit_zscore=0,
                exit_reason="end",
                spread_std=spread_std or 1,
            )
            trades.append(current_trade)
        
        # Calculer les métriques
        result = self._calculate_metrics(
            trades=trades,
            pair_id=pair_id,
            symbol1=symbol1,
            symbol2=symbol2,
            start_date=df.index[0].to_pydatetime(),
            end_date=df.index[-1].to_pydatetime(),
            equity_curve=equity_curve,
            max_drawdown=max_drawdown,
            half_lives=half_lives,
            cointegration_count=cointegration_count,
        )
        
        return result
    
    def _close_trade(
        self,
        trade: Trade,
        exit_date: datetime,
        exit_spread: float,
        exit_zscore: float,
        exit_reason: str,
        spread_std: float,
    ) -> Trade:
        """Ferme un trade et calcule le P&L."""
        trade.exit_date = exit_date
        trade.exit_spread = exit_spread
        trade.exit_zscore = exit_zscore
        trade.exit_reason = exit_reason
        
        # P&L en unités de spread
        spread_change = exit_spread - trade.entry_spread
        if trade.direction == "short_spread":
            spread_change = -spread_change
        
        trade.pnl_spread_units = spread_change
        
        # P&L en % du risque (utiliser le spread_std à l'ENTRÉE pour cohérence)
        # On risque 1 std de spread (z=2 entry, z=3 stop = 1 std de risque)
        # Donc P&L% = spread_change / entry_spread_std
        ref_std = trade.entry_spread_std if trade.entry_spread_std > 0 else spread_std
        trade.pnl_percent = spread_change / ref_std if ref_std > 0 else 0
        
        # Holding days
        if isinstance(trade.entry_date, pd.Timestamp):
            trade.holding_days = (exit_date - trade.entry_date).days
        else:
            trade.holding_days = (exit_date - trade.entry_date).days
        
        return trade
    
    def _calculate_metrics(
        self,
        trades: List[Trade],
        pair_id: str,
        symbol1: str,
        symbol2: str,
        start_date: datetime,
        end_date: datetime,
        equity_curve: List[float],
        max_drawdown: float,
        half_lives: List[float],
        cointegration_count: int,
    ) -> BacktestResult:
        """Calcule toutes les métriques du backtest."""
        
        result = BacktestResult(
            pair_id=pair_id,
            symbol1=symbol1,
            symbol2=symbol2,
            start_date=start_date,
            end_date=end_date,
            zscore_entry=self.zscore_entry,
            zscore_exit=self.zscore_exit,
            zscore_stop=self.zscore_stop,
            max_holding_days=int(self.max_holding_multiplier * (np.mean(half_lives) if half_lives else 20)),
            trades=trades,
            equity_curve=equity_curve,
            max_drawdown_percent=max_drawdown * 100,
            avg_half_life=np.mean(half_lives) if half_lives else 0,
            cointegration_periods=cointegration_count,
        )
        
        if not trades:
            return result
        
        # Métriques de base
        result.total_trades = len(trades)
        result.winning_trades = sum(1 for t in trades if t.is_winner)
        result.losing_trades = result.total_trades - result.winning_trades
        
        # Win rate
        result.win_rate = result.winning_trades / result.total_trades if result.total_trades > 0 else 0
        
        # P&L
        pnls = [t.pnl_percent for t in trades if t.pnl_percent is not None]
        if pnls:
            result.total_pnl_percent = sum(pnls) * 100  # En %
            result.avg_pnl_percent = np.mean(pnls) * 100
            result.max_win_percent = max(pnls) * 100
            result.max_loss_percent = min(pnls) * 100
        
        # Avg win / Avg loss
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]
        result.avg_win = np.mean(wins) * 100 if wins else 0
        result.avg_loss = np.mean(losses) * 100 if losses else 0
        
        # Profit factor
        gross_profit = sum(wins) if wins else 0
        gross_loss = abs(sum(losses)) if losses else 0
        result.profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Expectancy (en % par trade)
        result.expectancy = (
            result.win_rate * result.avg_win + 
            (1 - result.win_rate) * result.avg_loss
        )
        
        # Timing
        holding_days = [t.holding_days for t in trades if t.holding_days is not None]
        if holding_days:
            result.avg_holding_days = np.mean(holding_days)
            result.max_holding_days_actual = max(holding_days)
        
        # Exit breakdown
        result.exits_tp = sum(1 for t in trades if t.exit_reason == "tp")
        result.exits_sl = sum(1 for t in trades if t.exit_reason == "sl")
        result.exits_time = sum(1 for t in trades if t.exit_reason == "time")
        result.exits_breakdown = sum(1 for t in trades if t.exit_reason == "breakdown")
        
        return result
    
    def _empty_result(
        self,
        pair_id: str,
        symbol1: str,
        symbol2: str,
        start_date: datetime,
        end_date: datetime,
    ) -> BacktestResult:
        """Retourne un résultat vide."""
        return BacktestResult(
            pair_id=pair_id,
            symbol1=symbol1,
            symbol2=symbol2,
            start_date=start_date,
            end_date=end_date,
            zscore_entry=self.zscore_entry,
            zscore_exit=self.zscore_exit,
            zscore_stop=self.zscore_stop,
            max_holding_days=0,
        )


def run_multi_pair_backtest(
    pairs: List[Tuple[str, str]],
    lookback_days: int = 730,  # 2 ans
    **kwargs
) -> Dict[str, BacktestResult]:
    """
    Lance un backtest sur plusieurs paires.
    
    Returns:
        Dict[pair_id, BacktestResult]
    """
    backtester = PairsBacktester(lookback_days=lookback_days, **kwargs)
    results = {}
    
    for symbol1, symbol2 in pairs:
        pair_id = f"{symbol1}_{symbol2}"
        logger.info(f"\n{'='*60}")
        logger.info(f"Backtesting {pair_id}")
        logger.info(f"{'='*60}")
        
        result = backtester.run_backtest(symbol1, symbol2)
        results[pair_id] = result
        
        # Afficher résumé
        print_backtest_summary(result)
    
    return results


def print_backtest_summary(result: BacktestResult):
    """Affiche un résumé formaté du backtest."""
    
    print(f"\n{'='*60}")
    print(f"BACKTEST RESULTS: {result.pair_id}")
    print(f"{'='*60}")
    print(f"Period: {result.start_date.date()} → {result.end_date.date()}")
    print(f"Half-life moyen: {result.avg_half_life:.1f} jours")
    print()
    
    if result.total_trades == 0:
        print("❌ Aucun trade généré")
        return
    
    # Métriques principales
    print(f"📊 TRADES")
    print(f"   Total: {result.total_trades}")
    print(f"   Winners: {result.winning_trades} ({result.win_rate*100:.1f}%)")
    print(f"   Losers: {result.losing_trades}")
    print()
    
    print(f"💰 PERFORMANCE")
    print(f"   Total P&L: {result.total_pnl_percent:+.1f}%")
    print(f"   Avg P&L/trade: {result.avg_pnl_percent:+.2f}%")
    print(f"   Profit Factor: {result.profit_factor:.2f}")
    print(f"   Expectancy: {result.expectancy:+.2f}% par trade")
    print()
    
    print(f"📉 RISQUE")
    print(f"   Max Drawdown: {result.max_drawdown_percent:.1f}%")
    print(f"   Max Win: {result.max_win_percent:+.1f}%")
    print(f"   Max Loss: {result.max_loss_percent:.1f}%")
    print()
    
    print(f"⏱️ TIMING")
    print(f"   Avg Holding: {result.avg_holding_days:.1f} jours")
    print(f"   Max Holding: {result.max_holding_days_actual} jours")
    print()
    
    print(f"🚪 EXITS")
    print(f"   TP (mean reversion): {result.exits_tp}")
    print(f"   SL (divergence): {result.exits_sl}")
    print(f"   Time: {result.exits_time}")
    print(f"   Breakdown: {result.exits_breakdown}")
    print()
    
    # Verdict
    print(f"{'='*60}")
    if result.profit_factor >= 1.5 and result.win_rate >= 0.5 and result.expectancy > 0:
        print("✅ VERDICT: Stratégie VIABLE")
    elif result.profit_factor >= 1.2 and result.expectancy > 0:
        print("⚠️ VERDICT: Stratégie MARGINALE - à optimiser")
    else:
        print("❌ VERDICT: Stratégie NON VIABLE sur cette paire")
    print(f"{'='*60}")


def generate_backtest_report(
    results: Dict[str, BacktestResult],
    output_path: str = "backtest_report.md"
) -> str:
    """Génère un rapport Markdown du backtest."""
    
    lines = [
        "# 📊 Rapport de Backtest - Pairs Trading",
        "",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Résumé Global",
        "",
        "| Paire | Trades | Win Rate | PF | Expectancy | Max DD | Verdict |",
        "|-------|--------|----------|-----|------------|--------|---------|",
    ]
    
    viable_pairs = []
    
    for pair_id, result in results.items():
        if result.total_trades == 0:
            verdict = "❌ No trades"
        elif result.profit_factor >= 1.5 and result.win_rate >= 0.5:
            verdict = "✅ Viable"
            viable_pairs.append(pair_id)
        elif result.profit_factor >= 1.2 and result.expectancy > 0:
            verdict = "⚠️ Marginal"
        else:
            verdict = "❌ Non viable"
        
        lines.append(
            f"| {pair_id} | {result.total_trades} | "
            f"{result.win_rate*100:.0f}% | {result.profit_factor:.2f} | "
            f"{result.expectancy:+.1f}% | {result.max_drawdown_percent:.1f}% | {verdict} |"
        )
    
    lines.extend([
        "",
        "## Paires Viables",
        "",
    ])
    
    if viable_pairs:
        for pair_id in viable_pairs:
            r = results[pair_id]
            lines.extend([
                f"### {pair_id}",
                "",
                f"- **Trades**: {r.total_trades} (Win rate: {r.win_rate*100:.0f}%)",
                f"- **Profit Factor**: {r.profit_factor:.2f}",
                f"- **Expectancy**: {r.expectancy:+.2f}% par trade",
                f"- **Half-life moyen**: {r.avg_half_life:.1f} jours",
                f"- **Max Drawdown**: {r.max_drawdown_percent:.1f}%",
                "",
            ])
    else:
        lines.append("*Aucune paire viable trouvée avec les paramètres actuels.*")
    
    lines.extend([
        "",
        "## Paramètres",
        "",
        f"- Z-score entry: ±{results[list(results.keys())[0]].zscore_entry}" if results else "",
        f"- Z-score exit: ±{results[list(results.keys())[0]].zscore_exit}" if results else "",
        f"- Z-score stop: ±{results[list(results.keys())[0]].zscore_stop}" if results else "",
        "",
        "---",
        "*Rapport généré par Pairs Trading Backtest v1.1.0*",
    ])
    
    content = "\n".join(lines)
    
    # Sauvegarder
    Path(output_path).write_text(content)
    logger.info(f"Report saved to {output_path}")
    
    return content


# CLI
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Backtest Pairs Trading Strategy")
    parser.add_argument("--pair", type=str, help="Single pair to test (e.g., GBPJPY,EURJPY)")
    parser.add_argument("--all", action="store_true", help="Test all predefined pairs")
    parser.add_argument("--days", type=int, default=730, help="Lookback days (default: 730)")
    parser.add_argument("--output", type=str, default="backtest_report.md", help="Output report path")
    
    args = parser.parse_args()
    
    # Configure logging
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}"
    )
    
    if args.pair:
        # Single pair
        symbols = args.pair.split(",")
        if len(symbols) != 2:
            print("Error: --pair must be in format SYMBOL1,SYMBOL2")
            exit(1)
        
        backtester = PairsBacktester(lookback_days=args.days)
        result = backtester.run_backtest(symbols[0], symbols[1])
        print_backtest_summary(result)
        
    elif args.all:
        # All predefined pairs
        from config import PREDEFINED_PAIRS
        
        pairs = [(p["symbol1"], p["symbol2"]) for p in PREDEFINED_PAIRS]
        results = run_multi_pair_backtest(pairs, lookback_days=args.days)
        generate_backtest_report(results, args.output)
        
        print(f"\n📄 Report saved to {args.output}")
    else:
        # Default: test a few example pairs
        test_pairs = [
            ("GBPJPY", "EURJPY"),
            ("AUDJPY", "NZDJPY"),
            ("US500.cash", "US100.cash"),
        ]
        results = run_multi_pair_backtest(test_pairs, lookback_days=args.days)
        generate_backtest_report(results, args.output)
