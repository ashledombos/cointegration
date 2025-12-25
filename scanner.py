"""
Pairs Scanner - Détection de nouvelles paires coïntégrées
==========================================================
"""

import numpy as np
import pandas as pd
from itertools import combinations
from datetime import datetime
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from loguru import logger

from config import (
    config, 
    FOREX_UNIVERSE, INDICES_UNIVERSE, COMMODITIES_UNIVERSE,
    SECTORS_UNIVERSE, CRYPTO_UNIVERSE, PREDEFINED_PAIRS
)
from data_fetcher import DataFetcher
from cointegration import CointegrationAnalyzer, CointegrationResult
from database import Database, db


@dataclass
class ScanResult:
    """Résultat d'un scan de paires."""
    timestamp: datetime
    pairs_scanned: int
    cointegrated_found: int
    new_pairs: int
    breakdown_detected: int
    results: List[CointegrationResult]


class PairsScanner:
    """Scanner pour détecter les paires coïntégrées."""
    
    def __init__(
        self,
        fetcher: Optional[DataFetcher] = None,
        database: Optional[Database] = None
    ):
        self.fetcher = fetcher or DataFetcher()
        self.db = database or db
        self.analyzer = CointegrationAnalyzer()
    
    def scan_universe(
        self,
        symbols: List[str],
        lookback_days: int = 365,
        max_pairs: int = 100,
        skip_existing: bool = True
    ) -> ScanResult:
        """
        Scanne un univers de symboles pour trouver des paires coïntégrées.
        
        Args:
            symbols: Liste des symboles à scanner
            lookback_days: Historique à utiliser
            max_pairs: Nombre max de paires à tester
            skip_existing: Ignorer les paires déjà actives
        """
        logger.info(f"Scanning {len(symbols)} symbols...")
        
        # Fetch all data
        data = self.fetcher.fetch_multiple(symbols, lookback_days)
        available_symbols = list(data.keys())
        
        if len(available_symbols) < 2:
            logger.warning("Not enough symbols with data")
            return ScanResult(
                timestamp=datetime.now(),
                pairs_scanned=0,
                cointegrated_found=0,
                new_pairs=0,
                breakdown_detected=0,
                results=[]
            )
        
        # Generate pairs
        all_pairs = list(combinations(available_symbols, 2))
        
        # Limit pairs to test
        if len(all_pairs) > max_pairs:
            logger.info(f"Limiting to {max_pairs} pairs (from {len(all_pairs)})")
            np.random.seed(42)
            indices = np.random.choice(len(all_pairs), max_pairs, replace=False)
            pairs_to_test = [all_pairs[i] for i in indices]
        else:
            pairs_to_test = all_pairs
        
        # Get existing active pairs
        existing_pairs = set()
        if skip_existing:
            for pair in self.db.get_active_pairs():
                existing_pairs.add(pair.pair_id)
        
        # Test pairs
        results = []
        cointegrated = []
        new_pairs = 0
        
        for sym1, sym2 in pairs_to_test:
            pair_id = f"{sym1}_{sym2}"
            
            if pair_id in existing_pairs:
                continue
            
            # Align data
            df1 = data[sym1]
            df2 = data[sym2]
            
            combined = pd.DataFrame({
                "close_1": df1["close"],
                "close_2": df2["close"]
            }).dropna()
            
            if len(combined) < 100:
                continue
            
            # Test cointegration
            try:
                result = self.analyzer.test_engle_granger(
                    combined["close_1"],
                    combined["close_2"],
                    sym1, sym2
                )
                results.append(result)
                
                if result.is_cointegrated:
                    cointegrated.append(result)
                    
                    # Check if new
                    if pair_id not in existing_pairs:
                        new_pairs += 1
                        
                        # Save to database
                        self.db.save_pair(
                            pair_id=pair_id,
                            symbol1=sym1,
                            symbol2=sym2,
                            hedge_ratio=result.hedge_ratio,
                            half_life=result.half_life,
                            pvalue=result.pvalue,
                            spread_mean=result.spread_mean,
                            spread_std=result.spread_std,
                            test_method=result.test_method
                        )
                        logger.info(f"New cointegrated pair: {pair_id} (p={result.pvalue:.3f}, HL={result.half_life:.1f})")
            
            except Exception as e:
                logger.debug(f"Error testing {pair_id}: {e}")
        
        logger.info(f"Scan complete: {len(cointegrated)}/{len(results)} cointegrated, {new_pairs} new")
        
        return ScanResult(
            timestamp=datetime.now(),
            pairs_scanned=len(results),
            cointegrated_found=len(cointegrated),
            new_pairs=new_pairs,
            breakdown_detected=0,
            results=cointegrated
        )
    
    def scan_predefined_pairs(
        self,
        pairs: Optional[List[Tuple[str, str]]] = None,
        lookback_days: int = 365
    ) -> ScanResult:
        """Scanne une liste de paires pré-définies."""
        pairs = pairs or PREDEFINED_PAIRS
        
        logger.info(f"Scanning {len(pairs)} predefined pairs...")
        
        results = []
        cointegrated = []
        new_pairs = 0
        
        for sym1, sym2 in pairs:
            pair_id = f"{sym1}_{sym2}"
            
            # Fetch pair data
            pair_data = self.fetcher.fetch_pair(sym1, sym2, lookback_days)
            
            if pair_data is None:
                continue
            
            # Test cointegration
            try:
                result = self.analyzer.test_engle_granger(
                    pair_data["close_1"],
                    pair_data["close_2"],
                    sym1, sym2
                )
                results.append(result)
                
                if result.is_cointegrated:
                    cointegrated.append(result)
                    
                    # Save/update in database
                    existing = self.db.get_pair(pair_id)
                    if not existing:
                        new_pairs += 1
                    
                    self.db.save_pair(
                        pair_id=pair_id,
                        symbol1=sym1,
                        symbol2=sym2,
                        hedge_ratio=result.hedge_ratio,
                        half_life=result.half_life,
                        pvalue=result.pvalue,
                        spread_mean=result.spread_mean,
                        spread_std=result.spread_std,
                        test_method=result.test_method
                    )
                    logger.info(f"✓ {pair_id}: p={result.pvalue:.3f}, HR={result.hedge_ratio:.3f}, HL={result.half_life:.1f}")
                else:
                    logger.info(f"✗ {pair_id}: p={result.pvalue:.3f} (not cointegrated)")
            
            except Exception as e:
                logger.error(f"Error testing {pair_id}: {e}")
        
        return ScanResult(
            timestamp=datetime.now(),
            pairs_scanned=len(results),
            cointegrated_found=len(cointegrated),
            new_pairs=new_pairs,
            breakdown_detected=0,
            results=cointegrated
        )
    
    def validate_active_pairs(self, lookback_days: int = 365) -> Tuple[int, int]:
        """
        Valide toutes les paires actives et détecte les breakdowns.
        
        Returns:
            (validated_count, breakdown_count)
        """
        active_pairs = self.db.get_active_pairs()
        logger.info(f"Validating {len(active_pairs)} active pairs...")
        
        validated = 0
        breakdowns = 0
        
        for pair in active_pairs:
            pair_data = self.fetcher.fetch_pair(
                pair.symbol1, 
                pair.symbol2, 
                lookback_days
            )
            
            if pair_data is None:
                logger.warning(f"No data for {pair.pair_id}")
                continue
            
            try:
                result = self.analyzer.test_engle_granger(
                    pair_data["close_1"],
                    pair_data["close_2"],
                    pair.symbol1, pair.symbol2
                )
                
                # Check for breakdown
                is_breakdown, reason = self.analyzer.check_breakdown(
                    result, 
                    pair.hedge_ratio
                )
                
                if is_breakdown:
                    self.db.increment_breakdown_count(pair.pair_id)
                    
                    # Check if exceeds threshold
                    updated_pair = self.db.get_pair(pair.pair_id)
                    if updated_pair.breakdown_count >= config.cointegration.breakdown_checks:
                        self.db.deactivate_pair(pair.pair_id, reason)
                        breakdowns += 1
                        logger.warning(f"Breakdown: {pair.pair_id} - {reason}")
                else:
                    # Reset breakdown count and update
                    self.db.reset_breakdown_count(pair.pair_id)
                    self.db.save_pair(
                        pair_id=pair.pair_id,
                        symbol1=pair.symbol1,
                        symbol2=pair.symbol2,
                        hedge_ratio=result.hedge_ratio,
                        half_life=result.half_life,
                        pvalue=result.pvalue,
                        spread_mean=result.spread_mean,
                        spread_std=result.spread_std
                    )
                    validated += 1
            
            except Exception as e:
                logger.error(f"Error validating {pair.pair_id}: {e}")
        
        logger.info(f"Validation complete: {validated} valid, {breakdowns} breakdowns")
        return validated, breakdowns
    
    def scan_all_universes(self, lookback_days: int = 365) -> Dict[str, ScanResult]:
        """Scanne tous les univers configurés."""
        results = {}
        
        # Predefined pairs
        logger.info("=== Scanning Predefined Pairs ===")
        results["predefined"] = self.scan_predefined_pairs(lookback_days=lookback_days)
        
        # Forex
        logger.info("=== Scanning Forex ===")
        results["forex"] = self.scan_universe(
            FOREX_UNIVERSE, 
            lookback_days=lookback_days,
            max_pairs=50
        )
        
        # Indices
        logger.info("=== Scanning Indices ===")
        results["indices"] = self.scan_universe(
            INDICES_UNIVERSE,
            lookback_days=lookback_days,
            max_pairs=50
        )
        
        # Commodities
        logger.info("=== Scanning Commodities ===")
        results["commodities"] = self.scan_universe(
            COMMODITIES_UNIVERSE,
            lookback_days=lookback_days,
            max_pairs=20
        )
        
        # Sectors (intra-sector pairs)
        for sector_name, symbols in SECTORS_UNIVERSE.items():
            logger.info(f"=== Scanning Sector: {sector_name} ===")
            results[f"sector_{sector_name}"] = self.scan_universe(
                symbols,
                lookback_days=lookback_days,
                max_pairs=30
            )
        
        # Summary
        total_scanned = sum(r.pairs_scanned for r in results.values())
        total_coint = sum(r.cointegrated_found for r in results.values())
        total_new = sum(r.new_pairs for r in results.values())
        
        logger.info(f"=== SCAN SUMMARY ===")
        logger.info(f"Total pairs scanned: {total_scanned}")
        logger.info(f"Total cointegrated: {total_coint}")
        logger.info(f"Total new pairs: {total_new}")
        
        return results
    
    def get_top_pairs(self, n: int = 20) -> List[Dict]:
        """Retourne les N meilleures paires actives."""
        pairs = self.db.get_active_pairs()
        
        # Score basé sur p-value et half-life
        scored = []
        for p in pairs:
            # Score = faible p-value + half-life proche de 20 jours
            pvalue_score = 1 - p.pvalue
            halflife_score = 1 - abs(p.half_life - 20) / 50
            score = (pvalue_score * 0.6) + (halflife_score * 0.4)
            
            scored.append({
                "pair_id": p.pair_id,
                "symbol1": p.symbol1,
                "symbol2": p.symbol2,
                "pvalue": p.pvalue,
                "hedge_ratio": p.hedge_ratio,
                "half_life": p.half_life,
                "score": score
            })
        
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:n]


def generate_scan_report(results: Dict[str, ScanResult]) -> str:
    """Génère un rapport textuel des résultats de scan."""
    lines = [
        "=" * 50,
        "PAIRS TRADING SCAN REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 50,
        ""
    ]
    
    for universe, result in results.items():
        lines.extend([
            f"### {universe.upper()} ###",
            f"Pairs scanned: {result.pairs_scanned}",
            f"Cointegrated: {result.cointegrated_found}",
            f"New pairs: {result.new_pairs}",
            ""
        ])
        
        if result.results:
            lines.append("Top pairs:")
            for r in sorted(result.results, key=lambda x: x.pvalue)[:5]:
                lines.append(f"  - {r.symbol1}/{r.symbol2}: p={r.pvalue:.3f}, HL={r.half_life:.1f}")
            lines.append("")
    
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    logger.remove()
    logger.add(sys.stdout, level="INFO")
    
    scanner = PairsScanner()
    
    # Scan predefined pairs
    print("\n=== Scanning Predefined Pairs ===")
    result = scanner.scan_predefined_pairs()
    
    print(f"\nResults:")
    print(f"  Scanned: {result.pairs_scanned}")
    print(f"  Cointegrated: {result.cointegrated_found}")
    print(f"  New: {result.new_pairs}")
    
    # Show top pairs
    print("\n=== Top Pairs ===")
    top = scanner.get_top_pairs(10)
    for p in top:
        print(f"  {p['pair_id']}: p={p['pvalue']:.3f}, HR={p['hedge_ratio']:.3f}, HL={p['half_life']:.1f}")
