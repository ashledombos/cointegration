"""
Main Orchestrator - Système de Pairs Trading par Coïntégration
================================================================
Point d'entrée principal avec scheduling des tâches.
"""

import asyncio
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pathlib import Path

from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from config import config, PREDEFINED_PAIRS
from data_fetcher import DataFetcher
from cointegration import CointegrationAnalyzer
from signals import SignalGenerator, Signal
from database import Database, db
from alerts import AlertManager, send_signal_sync
from scanner import PairsScanner, generate_scan_report


class PairsTradingSystem:
    """Système principal de pairs trading."""
    
    def __init__(self):
        self.fetcher = DataFetcher()
        self.analyzer = CointegrationAnalyzer()
        self.signal_generator = SignalGenerator()
        self.scanner = PairsScanner(self.fetcher, db)
        self.alert_manager = AlertManager()
        self.scheduler: Optional[AsyncIOScheduler] = None
        
        logger.info("Pairs Trading System initialized")
    
    async def check_pair_signal(self, pair_id: str) -> Optional[Signal]:
        """Vérifie les signaux pour une paire spécifique."""
        pair = db.get_pair(pair_id)
        if not pair or not pair.is_active:
            return None
        
        # Fetch recent data
        pair_data = self.fetcher.fetch_pair(
            pair.symbol1,
            pair.symbol2,
            lookback_days=60,  # 2 mois pour z-score
            timeframe=config.data.signal_timeframe
        )
        
        if pair_data is None:
            logger.warning(f"No data for {pair_id}")
            return None
        
        # Get latest cointegration result
        coint_result = self.analyzer.test_engle_granger(
            pair_data["close_1"],
            pair_data["close_2"],
            pair.symbol1,
            pair.symbol2
        )
        
        # Get current prices
        prices = self.fetcher.get_latest_prices([pair.symbol1, pair.symbol2])
        
        # Generate signal
        signal = self.signal_generator.generate_signal(
            pair_id=pair_id,
            symbol1=pair.symbol1,
            symbol2=pair.symbol2,
            series1=pair_data["close_1"],
            series2=pair_data["close_2"],
            coint_result=coint_result,
            current_price1=prices.get(pair.symbol1),
            current_price2=prices.get(pair.symbol2)
        )
        
        return signal
    
    async def check_all_pairs(self):
        """Vérifie les signaux pour toutes les paires actives."""
        active_pairs = db.get_active_pairs()
        
        if not active_pairs:
            logger.warning("No active pairs to check")
            return []
        
        logger.info(f"Checking {len(active_pairs)} active pairs...")
        
        signals_generated = []
        zscore_summary = []  # Pour le résumé
        
        for pair in active_pairs:
            try:
                # Fetch data
                pair_data = self.fetcher.fetch_pair(
                    pair.symbol1,
                    pair.symbol2,
                    lookback_days=60,
                    timeframe=config.data.signal_timeframe
                )
                
                if pair_data is None:
                    logger.warning(f"No data for {pair.pair_id}")
                    continue
                
                # Get cointegration result
                coint_result = self.analyzer.test_engle_granger(
                    pair_data["close_1"],
                    pair_data["close_2"],
                    pair.symbol1,
                    pair.symbol2
                )
                
                if coint_result:
                    # Calculate spread and z-score
                    spread = self.analyzer.calculate_spread(
                        pair_data["close_1"],
                        pair_data["close_2"],
                        coint_result.hedge_ratio
                    )
                    zscore_series = self.analyzer.calculate_zscore(spread)
                    current_zscore = zscore_series.iloc[-1] if len(zscore_series) > 0 else 0.0
                    
                    zscore_summary.append({
                        "pair": pair.pair_id,
                        "zscore": current_zscore,
                        "half_life": coint_result.half_life
                    })
                
                # Generate signal if threshold crossed
                prices = self.fetcher.get_latest_prices([pair.symbol1, pair.symbol2])
                signal = self.signal_generator.generate_signal(
                    pair_id=pair.pair_id,
                    symbol1=pair.symbol1,
                    symbol2=pair.symbol2,
                    series1=pair_data["close_1"],
                    series2=pair_data["close_2"],
                    coint_result=coint_result,
                    current_price1=prices.get(pair.symbol1),
                    current_price2=prices.get(pair.symbol2)
                )
                
                if signal:
                    signals_generated.append(signal)
                    
                    # Save to database
                    db.save_signal(
                        pair_id=signal.pair_id,
                        signal_type=signal.signal_type.value,
                        symbol1=signal.symbol1,
                        symbol2=signal.symbol2,
                        zscore=signal.zscore,
                        hedge_ratio=signal.hedge_ratio,
                        timestamp=signal.timestamp,
                        price1=signal.price1,
                        price2=signal.price2,
                        reason=signal.reason
                    )
                    
                    # Send alert
                    await self.alert_manager.send_signal(signal)
                    
            except Exception as e:
                logger.error(f"Error checking {pair.pair_id}: {e}")
        
        # Log z-score summary
        if zscore_summary:
            # Sort by absolute z-score (closest to entry threshold first)
            zscore_summary.sort(key=lambda x: abs(abs(x["zscore"]) - config.signal.zscore_entry))
            
            logger.info("=" * 50)
            logger.info("Z-SCORE SUMMARY (sorted by proximity to entry)")
            logger.info("-" * 50)
            
            for item in zscore_summary:
                z = item["zscore"]
                pair = item["pair"]
                
                # Status indicator
                if z <= -config.signal.zscore_entry:
                    status = "🟢 LONG"
                elif z >= config.signal.zscore_entry:
                    status = "🔴 SHORT"
                elif abs(z) >= config.signal.zscore_entry * 0.8:  # Within 80% of entry
                    status = "⚠️  WATCH"
                else:
                    status = "⚪ neutral"
                
                logger.info(f"  {pair:25} z={z:+6.2f}  {status}")
            
            logger.info("=" * 50)
        
        if signals_generated:
            logger.info(f"🔔 Generated {len(signals_generated)} signal(s)!")
            for s in signals_generated:
                logger.info(f"   → {s.signal_type.value}: {s.pair_id}")
        
        return signals_generated
    
    async def daily_recalibration(self):
        """Recalibration quotidienne: validation des paires et mise à jour des hedge ratios."""
        logger.info("=== Starting Daily Recalibration ===")
        
        # Validate active pairs
        validated, breakdowns = self.scanner.validate_active_pairs()
        
        # Send notification
        message = (
            f"📊 *Daily Recalibration Complete*\n"
            f"• Validated: {validated} pairs\n"
            f"• Breakdowns: {breakdowns} pairs\n"
            f"• Active pairs: {len(db.get_active_pairs())}"
        )
        await self.alert_manager.send_message(message)
        
        logger.info("Daily recalibration complete")
    
    async def weekly_scan(self):
        """Scan hebdomadaire pour nouvelles paires."""
        logger.info("=== Starting Weekly Scan ===")
        
        # Scan predefined pairs
        results = {"predefined": self.scanner.scan_predefined_pairs()}
        
        # Generate report
        report = generate_scan_report(results)
        
        # Send notification
        message = (
            f"📈 *Weekly Scan Complete*\n"
            f"• Pairs scanned: {results['predefined'].pairs_scanned}\n"
            f"• Cointegrated found: {results['predefined'].cointegrated_found}\n"
            f"• New pairs: {results['predefined'].new_pairs}"
        )
        await self.alert_manager.send_message(message)
        
        logger.info("Weekly scan complete")
        return results
    
    async def send_daily_report(self):
        """Envoie le rapport quotidien."""
        stats = db.get_statistics()
        position_summary = self.signal_generator.get_position_summary()
        recent_signals = db.get_recent_signals(hours=24)
        
        # Top pairs by z-score (would need current z-scores)
        top_pairs = self.scanner.get_top_pairs(5)
        
        report = {
            "active_pairs": stats["active_pairs"],
            "open_positions": position_summary["active_positions"],
            "long_spread": position_summary["long_spread"],
            "short_spread": position_summary["short_spread"],
            "signals_today": len(recent_signals),
            "entries_today": len([s for s in recent_signals if "open" in s.signal_type.lower()]),
            "exits_today": len([s for s in recent_signals if "close" in s.signal_type.lower() or "exit" in s.signal_type.lower()]),
            "top_zscore_pairs": top_pairs[:5]
        }
        
        await self.alert_manager.send_daily_report(report)
        logger.info("Daily report sent")
    
    def setup_scheduler(self):
        """Configure le scheduler APScheduler."""
        self.scheduler = AsyncIOScheduler()
        
        # Z-score check every N minutes
        self.scheduler.add_job(
            self.check_all_pairs,
            IntervalTrigger(minutes=config.scheduler.zscore_check_interval),
            id="zscore_check",
            name="Z-Score Check",
            replace_existing=True
        )
        
        # Daily recalibration
        hour, minute = config.scheduler.daily_recalibration_time.split(":")
        self.scheduler.add_job(
            self.daily_recalibration,
            CronTrigger(hour=int(hour), minute=int(minute)),
            id="daily_recalibration",
            name="Daily Recalibration",
            replace_existing=True
        )
        
        # Weekly scan
        hour, minute = config.scheduler.weekly_scan_time.split(":")
        self.scheduler.add_job(
            self.weekly_scan,
            CronTrigger(
                day_of_week=config.scheduler.weekly_scan_day,
                hour=int(hour),
                minute=int(minute)
            ),
            id="weekly_scan",
            name="Weekly Scan",
            replace_existing=True
        )
        
        # Daily report (end of day)
        self.scheduler.add_job(
            self.send_daily_report,
            CronTrigger(hour=21, minute=0),  # 21:00 UTC
            id="daily_report",
            name="Daily Report",
            replace_existing=True
        )
        
        logger.info("Scheduler configured")
    
    async def run(self):
        """Lance le système."""
        logger.info("Starting Pairs Trading System...")
        
        # Initial checks
        if not config.validate():
            logger.error("Invalid configuration")
            return
        
        # Setup scheduler
        self.setup_scheduler()
        self.scheduler.start()
        
        # Send startup notification
        await self.alert_manager.send_message(
            "🚀 *Pairs Trading System Started*\n"
            f"• Active pairs: {len(db.get_active_pairs())}\n"
            f"• Check interval: {config.scheduler.zscore_check_interval} min\n"
            f"• Z-score entry: ±{config.signal.zscore_entry}"
        )
        
        # Run initial check
        await self.check_all_pairs()
        
        # Keep running
        logger.info("System running. Press Ctrl+C to stop.")
        try:
            while True:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.scheduler.shutdown()


async def run_once():
    """Exécute une vérification unique (mode one-shot)."""
    system = PairsTradingSystem()
    signals = await system.check_all_pairs()
    return signals


def cli():
    """Interface ligne de commande."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pairs Trading Cointegration System")
    parser.add_argument(
        "command",
        choices=["run", "scan", "check", "report", "init"],
        help="Command to execute"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Scan all possible combinations (not just predefined pairs)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logger.remove()
    level = "DEBUG" if args.debug else "INFO"
    logger.add(
        sys.stdout,
        level=level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}"
    )
    logger.add(
        "logs/pairs_trading.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG"
    )
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    if args.command == "run":
        # Run main system
        system = PairsTradingSystem()
        asyncio.run(system.run())
    
    elif args.command == "scan":
        scanner = PairsScanner()
        
        if args.full:
            # Full scan of all universes
            print("Starting FULL scan of all universes...")
            print("This may take 10-30 minutes depending on network speed.\n")
            results = scanner.scan_all_universes()
            
            total_scanned = sum(r.pairs_scanned for r in results.values())
            total_coint = sum(r.cointegrated_found for r in results.values())
            total_new = sum(r.new_pairs for r in results.values())
            
            print(f"\n{'='*50}")
            print(f"FULL SCAN COMPLETE")
            print(f"{'='*50}")
            for universe, result in results.items():
                if result.cointegrated_found > 0:
                    print(f"  {universe}: {result.cointegrated_found} cointegrated / {result.pairs_scanned} scanned")
            print(f"{'='*50}")
            print(f"TOTAL: {total_coint} cointegrated / {total_scanned} scanned")
            print(f"NEW PAIRS: {total_new}")
        else:
            # Predefined pairs only
            result = scanner.scan_predefined_pairs()
            print(f"\nScan complete:")
            print(f"  Scanned: {result.pairs_scanned}")
            print(f"  Cointegrated: {result.cointegrated_found}")
            print(f"  New: {result.new_pairs}")
        
        # Show top pairs
        print("\nTop pairs:")
        for p in scanner.get_top_pairs(10):
            print(f"  {p['pair_id']}: p={p['pvalue']:.3f}, HL={p['half_life']:.1f}")
    
    elif args.command == "check":
        # Run single check
        signals = asyncio.run(run_once())
        if signals:
            print(f"\nGenerated {len(signals)} signals:")
            for s in signals:
                print(f"  {s.signal_type.value}: {s.pair_id} (z={s.zscore:.2f})")
        else:
            print("\nNo signals generated")
    
    elif args.command == "report":
        # Show current status
        stats = db.get_statistics()
        print("\n=== Pairs Trading Status ===")
        print(f"Total pairs: {stats['total_pairs']}")
        print(f"Active pairs: {stats['active_pairs']}")
        print(f"Open positions: {stats['open_positions']}")
        print(f"Total signals: {stats['total_signals']}")
        
        print("\n=== Top Active Pairs ===")
        scanner = PairsScanner()
        for p in scanner.get_top_pairs(10):
            print(f"  {p['pair_id']}: p={p['pvalue']:.3f}, HR={p['hedge_ratio']:.3f}, HL={p['half_life']:.1f}")
    
    elif args.command == "init":
        # Initialize with predefined pairs
        print("Initializing system with predefined pairs...")
        scanner = PairsScanner()
        result = scanner.scan_predefined_pairs()
        print(f"\nInitialization complete:")
        print(f"  Cointegrated pairs found: {result.cointegrated_found}")
        print("\nSystem ready. Run 'python main.py run' to start monitoring.")


if __name__ == "__main__":
    cli()
