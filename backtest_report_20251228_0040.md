# 📊 Rapport de Backtest - Pairs Trading

Date: 2025-12-28 00:40

## Résumé Global

| Paire | Trades | Win Rate | PF | Expectancy | Max DD | Verdict |
|-------|--------|----------|-----|------------|--------|---------|
| US500.cash_US100.cash | 3 | 33% | 0.01 | -69.9% | 3.2% | ❌ Non viable |
| EURGBP_EURJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| GBPJPY_EURJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| AUDUSD_CHFJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| NZDCHF_EURCZK | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| AUDJPY_CADJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURCHF_EURCZK | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| USDCHF_USDPLN | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| NZDCAD_CHFJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURCHF_NZDCHF | 1 | 0% | 0.00 | -17.3% | 0.0% | ❌ Non viable |
| FRA40.cash_SPN35.cash | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| FRA40.cash_JP225.cash | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| UK100.cash_FRA40.cash | 2 | 100% | inf | +22.5% | 0.0% | ✅ Viable |
| EU50.cash_HK50.cash | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| UK100.cash_SPN35.cash | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| FRA40.cash_N25.cash | 2 | 50% | 7.40 | +321.8% | 1.4% | ✅ Viable |
| COTTON.c_XCUUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |

## Paires Viables

### UK100.cash_FRA40.cash

- **Trades**: 2 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +22.51% par trade
- **Half-life moyen**: 3.2 jours
- **Max Drawdown**: 0.0%

### FRA40.cash_N25.cash

- **Trades**: 2 (Win rate: 50%)
- **Profit Factor**: 7.40
- **Expectancy**: +321.81% par trade
- **Half-life moyen**: 3.5 jours
- **Max Drawdown**: 1.4%


## Paramètres

- Z-score entry: ±2.0
- Z-score exit: ±1.0
- Z-score stop: ±3.0

---
*Rapport généré par Pairs Trading Backtest v1.1.0*