# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2025-12-27

### Added
- Backtesting module (`backtest.py`) for historical strategy validation
- CLI commands: `python main.py backtest --pair GBPJPY,EURJPY` and `python main.py backtest --full`
- Automated Markdown report generation with performance metrics
- Metrics: win rate, profit factor, expectancy, max drawdown, Sharpe-like ratios
- Rolling cointegration recalibration during backtest (every 30 days)
- Trade-by-trade logging with entry/exit reasons

### Changed
- Version bumped to 1.1.0

## [1.0.0] - 2025-12-27

### Added
- Initial release
- Cointegration scanner for multiple universes (Forex, Indices, Commodities, Crypto, Stocks)
- FTMO symbol mapping (130+ instruments)
- Z-score monitoring with configurable thresholds (entry ±2.0, warning ±2.5, stop ±3.0)
- Multi-channel alerts: Telegram, Discord, Ntfy
- Position sizing based on FTMO account configuration
- Automatic log rotation via Loguru (10MB, 7 days retention, gzip compression)
- Systemd service with health check
- Daily recalibration at 06:00 UTC
- Weekly full scan on Sundays at 18:00 UTC
- Daily report at 21:00 UTC

### Configuration
- Support for FTMO Swing accounts (leverage 1:30)
- Configurable risk per trade (default 1.5%)
- Full instrument specifications (contract size, pip value, margin currency)

### Technical
- Engle-Granger cointegration test
- Half-life calculation via Ornstein-Uhlenbeck
- Rolling cointegration validation
- SQLite database for pairs and signals storage
