"""
Cointegration Analysis Module
==============================
Tests de coïntégration, calcul du hedge ratio et half-life.
"""

import numpy as np
import pandas as pd
from typing import Optional, Tuple, Dict, NamedTuple
from dataclasses import dataclass
from loguru import logger

from statsmodels.tsa.stattools import coint, adfuller
from statsmodels.regression.linear_model import OLS
from statsmodels.tsa.vector_ar.vecm import coint_johansen
import statsmodels.api as sm

from config import config


@dataclass
class CointegrationResult:
    """Résultat d'un test de coïntégration."""
    symbol1: str
    symbol2: str
    is_cointegrated: bool
    pvalue: float
    hedge_ratio: float
    half_life: float
    spread_mean: float
    spread_std: float
    test_method: str  # 'engle_granger' ou 'johansen'
    adf_statistic: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "symbol1": self.symbol1,
            "symbol2": self.symbol2,
            "is_cointegrated": self.is_cointegrated,
            "pvalue": round(self.pvalue, 4),
            "hedge_ratio": round(self.hedge_ratio, 4),
            "half_life": round(self.half_life, 2),
            "spread_mean": round(self.spread_mean, 4),
            "spread_std": round(self.spread_std, 4),
            "test_method": self.test_method,
        }


class CointegrationAnalyzer:
    """Analyseur de coïntégration pour pairs trading."""
    
    def __init__(self):
        self.config = config.cointegration
    
    def test_engle_granger(
        self, 
        series1: pd.Series, 
        series2: pd.Series,
        symbol1: str = "Asset1",
        symbol2: str = "Asset2"
    ) -> CointegrationResult:
        """
        Test de coïntégration Engle-Granger (deux étapes).
        
        1. Régression OLS: series1 = α + β * series2 + ε
        2. Test ADF sur les résidus
        """
        # Test de coïntégration statsmodels
        score, pvalue, _ = coint(series1, series2)
        
        # Calcul du hedge ratio via OLS
        hedge_ratio = self._calculate_hedge_ratio_ols(series1, series2)
        
        # Calcul du spread
        spread = series1 - hedge_ratio * series2
        
        # Half-life de mean reversion
        half_life = self._calculate_half_life(spread)
        
        # Statistique ADF sur le spread
        adf_result = adfuller(spread.dropna())
        
        is_cointegrated = (
            pvalue < self.config.pvalue_threshold and
            self.config.min_half_life <= half_life <= self.config.max_half_life
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
            adf_statistic=adf_result[0]
        )
    
    def test_johansen(
        self,
        series1: pd.Series,
        series2: pd.Series,
        symbol1: str = "Asset1",
        symbol2: str = "Asset2",
        det_order: int = 0,
        k_ar_diff: int = 1
    ) -> CointegrationResult:
        """
        Test de Johansen pour coïntégration.
        
        Avantages vs Engle-Granger:
        - Symétrique (pas de variable dépendante)
        - Détecte les relations multiples
        - Fournit directement les hedge ratios
        """
        data = np.column_stack([series1.values, series2.values])
        
        try:
            result = coint_johansen(data, det_order=det_order, k_ar_diff=k_ar_diff)
            
            # Valeurs critiques pour trace statistic (90%, 95%, 99%)
            trace_stat = result.lr1[0]
            critical_values = result.cvt[0]  # 90%, 95%, 99%
            
            # p-value approximative basée sur les valeurs critiques
            if trace_stat > critical_values[2]:  # > 99%
                pvalue = 0.01
            elif trace_stat > critical_values[1]:  # > 95%
                pvalue = 0.05
            elif trace_stat > critical_values[0]:  # > 90%
                pvalue = 0.10
            else:
                pvalue = 0.20
            
            # Hedge ratio depuis l'eigenvector
            evec = result.evec[:, 0]
            hedge_ratio = -evec[1] / evec[0]
            
            # Spread et half-life
            spread = series1 - hedge_ratio * series2
            half_life = self._calculate_half_life(spread)
            
            is_cointegrated = (
                pvalue < self.config.pvalue_threshold and
                self.config.min_half_life <= half_life <= self.config.max_half_life
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
                test_method="johansen"
            )
            
        except Exception as e:
            logger.error(f"Johansen test error: {e}")
            # Fallback sur Engle-Granger
            return self.test_engle_granger(series1, series2, symbol1, symbol2)
    
    def _calculate_hedge_ratio_ols(self, series1: pd.Series, series2: pd.Series) -> float:
        """Calcule le hedge ratio via régression OLS."""
        X = sm.add_constant(series2)
        model = OLS(series1, X).fit()
        return model.params.iloc[1]
    
    def _calculate_hedge_ratio_tls(self, series1: pd.Series, series2: pd.Series) -> float:
        """
        Calcule le hedge ratio via Total Least Squares (orthogonal regression).
        Plus robuste quand les deux séries ont du bruit.
        """
        X = np.column_stack([series1.values, series2.values])
        X_centered = X - X.mean(axis=0)
        
        # SVD pour TLS
        _, _, Vt = np.linalg.svd(X_centered)
        
        # Le hedge ratio est le ratio des composantes du vecteur singulier
        hedge_ratio = -Vt[-1, 0] / Vt[-1, 1]
        return hedge_ratio
    
    def _calculate_half_life(self, spread: pd.Series) -> float:
        """
        Calcule le half-life de mean reversion.
        
        Modèle: Δspread(t) = λ * spread(t-1) + ε
        Half-life: τ = -ln(2) / λ
        """
        spread_lag = spread.shift(1)
        spread_diff = spread - spread_lag
        
        # Nettoyer les NaN
        df = pd.DataFrame({"diff": spread_diff, "lag": spread_lag}).dropna()
        
        if len(df) < 20:
            return float('inf')
        
        # Régression
        X = sm.add_constant(df["lag"])
        model = OLS(df["diff"], X).fit()
        lambda_coef = model.params.iloc[1]
        
        if lambda_coef >= 0:
            return float('inf')  # Pas de mean reversion
        
        half_life = -np.log(2) / lambda_coef
        return half_life
    
    def calculate_spread(
        self,
        series1: pd.Series,
        series2: pd.Series,
        hedge_ratio: float
    ) -> pd.Series:
        """Calcule le spread entre deux séries."""
        return series1 - hedge_ratio * series2
    
    def calculate_zscore(
        self,
        spread: pd.Series,
        lookback: Optional[int] = None
    ) -> pd.Series:
        """
        Calcule le z-score du spread.
        
        Args:
            spread: Série du spread
            lookback: Fenêtre pour la moyenne/std (si None, utilise tout l'historique)
        """
        if lookback:
            rolling_mean = spread.rolling(window=lookback).mean()
            rolling_std = spread.rolling(window=lookback).std()
        else:
            rolling_mean = spread.mean()
            rolling_std = spread.std()
        
        zscore = (spread - rolling_mean) / rolling_std
        return zscore
    
    def rolling_cointegration_test(
        self,
        series1: pd.Series,
        series2: pd.Series,
        window: int = 252,
        symbol1: str = "Asset1",
        symbol2: str = "Asset2"
    ) -> pd.DataFrame:
        """
        Test de coïntégration rolling pour détecter les breakdowns.
        
        Returns:
            DataFrame avec colonnes: pvalue, hedge_ratio, half_life, is_valid
        """
        results = []
        
        for i in range(window, len(series1)):
            s1_window = series1.iloc[i-window:i]
            s2_window = series2.iloc[i-window:i]
            
            try:
                result = self.test_engle_granger(s1_window, s2_window, symbol1, symbol2)
                results.append({
                    "date": series1.index[i],
                    "pvalue": result.pvalue,
                    "hedge_ratio": result.hedge_ratio,
                    "half_life": result.half_life,
                    "is_valid": result.is_cointegrated
                })
            except Exception as e:
                logger.debug(f"Rolling test error at {i}: {e}")
                continue
        
        return pd.DataFrame(results).set_index("date")
    
    def check_breakdown(
        self,
        result: CointegrationResult,
        previous_hedge_ratio: float
    ) -> Tuple[bool, str]:
        """
        Vérifie si une relation de coïntégration est en breakdown.
        
        Returns:
            (is_breakdown, reason)
        """
        # P-value trop haute
        if result.pvalue > self.config.pvalue_exit_threshold:
            return True, f"P-value breakdown: {result.pvalue:.3f}"
        
        # Hedge ratio drift
        if previous_hedge_ratio != 0:
            drift = abs(result.hedge_ratio - previous_hedge_ratio) / abs(previous_hedge_ratio)
            if drift > self.config.hedge_ratio_drift_threshold:
                return True, f"Hedge ratio drift: {drift:.1%}"
        
        # Half-life hors limites
        if result.half_life < self.config.min_half_life:
            return True, f"Half-life trop court: {result.half_life:.1f}"
        if result.half_life > self.config.max_half_life:
            return True, f"Half-life trop long: {result.half_life:.1f}"
        
        return False, ""


def analyze_pair(
    df: pd.DataFrame,
    symbol1: str,
    symbol2: str,
    method: str = "engle_granger"
) -> CointegrationResult:
    """
    Fonction utilitaire pour analyser une paire.
    
    Args:
        df: DataFrame avec colonnes 'close_1' et 'close_2'
        symbol1, symbol2: Noms des symboles
        method: 'engle_granger' ou 'johansen'
    """
    analyzer = CointegrationAnalyzer()
    
    if method == "johansen":
        return analyzer.test_johansen(
            df["close_1"], df["close_2"],
            symbol1, symbol2
        )
    else:
        return analyzer.test_engle_granger(
            df["close_1"], df["close_2"],
            symbol1, symbol2
        )


if __name__ == "__main__":
    import sys
    logger.remove()
    logger.add(sys.stdout, level="INFO")
    
    # Test avec données simulées
    np.random.seed(42)
    n = 500
    
    # Créer deux séries coïntégrées
    x = np.cumsum(np.random.randn(n)) + 100
    y = 0.8 * x + np.cumsum(np.random.randn(n) * 0.3) + 50
    
    series1 = pd.Series(x, index=pd.date_range("2023-01-01", periods=n))
    series2 = pd.Series(y, index=pd.date_range("2023-01-01", periods=n))
    
    analyzer = CointegrationAnalyzer()
    
    # Test Engle-Granger
    result_eg = analyzer.test_engle_granger(series1, series2, "Asset1", "Asset2")
    print("\n=== Engle-Granger Test ===")
    print(f"Coïntégrées: {result_eg.is_cointegrated}")
    print(f"P-value: {result_eg.pvalue:.4f}")
    print(f"Hedge ratio: {result_eg.hedge_ratio:.4f}")
    print(f"Half-life: {result_eg.half_life:.1f} jours")
    
    # Test Johansen
    result_joh = analyzer.test_johansen(series1, series2, "Asset1", "Asset2")
    print("\n=== Johansen Test ===")
    print(f"Coïntégrées: {result_joh.is_cointegrated}")
    print(f"P-value: {result_joh.pvalue:.4f}")
    print(f"Hedge ratio: {result_joh.hedge_ratio:.4f}")
    print(f"Half-life: {result_joh.half_life:.1f} jours")
