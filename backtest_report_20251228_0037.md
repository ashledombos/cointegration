# 📊 Rapport de Backtest - Pairs Trading

Date: 2025-12-28 00:37

## Résumé Global

| Paire | Trades | Win Rate | PF | Expectancy | Max DD | Verdict |
|-------|--------|----------|-----|------------|--------|---------|
| US500.cash_US100.cash | 3 | 33% | 0.01 | -69.9% | 3.2% | ❌ Non viable |
| US500.cash_US30.cash | 1 | 100% | inf | +132.3% | 0.0% | ✅ Viable |
| US100.cash_US30.cash | 1 | 100% | inf | +117.9% | 0.0% | ✅ Viable |
| US500.cash_US2000.cash | 1 | 100% | inf | +121.5% | 0.0% | ✅ Viable |
| GER40.cash_FRA40.cash | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| GER40.cash_EU50.cash | 3 | 0% | 0.00 | -57.4% | 1.8% | ❌ Non viable |
| UK100.cash_GER40.cash | 1 | 100% | inf | +112.9% | 0.0% | ✅ Viable |
| EURUSD_GBPUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| AUDUSD_NZDUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURGBP_EURJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| GBPJPY_EURJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| AUDNZD_AUDCAD | 2 | 50% | 11.07 | +438.3% | 1.1% | ✅ Viable |
| XAUUSD_XAGUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| XPTUSD_XPDUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| USOIL.cash_UKOIL.cash | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| CORN.c_WHEAT.c | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| CORN.c_SOYBEAN.c | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| BTCUSD_ETHUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| ETHUSD_SOLUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| AAPL_MSFT | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| GOOG_META | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |

## Paires Viables

### US500.cash_US30.cash

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +132.30% par trade
- **Half-life moyen**: 3.4 jours
- **Max Drawdown**: 0.0%

### US100.cash_US30.cash

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +117.94% par trade
- **Half-life moyen**: 3.2 jours
- **Max Drawdown**: 0.0%

### US500.cash_US2000.cash

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +121.45% par trade
- **Half-life moyen**: 3.2 jours
- **Max Drawdown**: 0.0%

### UK100.cash_GER40.cash

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +112.85% par trade
- **Half-life moyen**: 4.0 jours
- **Max Drawdown**: 0.0%

### AUDNZD_AUDCAD

- **Trades**: 2 (Win rate: 50%)
- **Profit Factor**: 11.07
- **Expectancy**: +438.35% par trade
- **Half-life moyen**: 4.7 jours
- **Max Drawdown**: 1.1%


## Paramètres

- Z-score entry: ±2.0
- Z-score exit: ±1.0
- Z-score stop: ±3.0

---
*Rapport généré par Pairs Trading Backtest v1.1.0*