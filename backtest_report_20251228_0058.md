# 📊 Rapport de Backtest - Pairs Trading

Date: 2025-12-28 00:58

## Résumé Global

| Paire | Trades | Win Rate | PF | Expectancy | Max DD | Verdict |
|-------|--------|----------|-----|------------|--------|---------|
| US500.cash_US100.cash | 3 | 33% | 0.01 | -69.9% | 3.2% | ❌ Non viable |
| US500.cash_US30.cash | 1 | 100% | inf | +132.3% | 0.0% | ✅ Viable |
| US100.cash_US30.cash | 1 | 100% | inf | +117.9% | 0.0% | ✅ Viable |
| US500.cash_US2000.cash | 1 | 100% | inf | +121.5% | 0.0% | ✅ Viable |
| US100.cash_US2000.cash | 6 | 50% | 1.23 | +6.9% | 2.3% | ⚠️ Marginal |
| US30.cash_US2000.cash | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| GER40.cash_FRA40.cash | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| GER40.cash_EU50.cash | 3 | 0% | 0.00 | -57.4% | 1.8% | ❌ Non viable |
| FRA40.cash_EU50.cash | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| UK100.cash_GER40.cash | 1 | 100% | inf | +112.9% | 0.0% | ✅ Viable |
| UK100.cash_EU50.cash | 2 | 100% | inf | +114.6% | 0.0% | ✅ Viable |
| SPN35.cash_EU50.cash | 2 | 0% | 0.00 | -62.3% | 1.9% | ❌ Non viable |
| US500.cash_GER40.cash | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| US500.cash_UK100.cash | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| US100.cash_GER40.cash | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURUSD_EURGBP | 1 | 100% | inf | +33.1% | 0.0% | ✅ Viable |
| EURUSD_EURJPY | 1 | 100% | inf | +171.1% | 0.0% | ✅ Viable |
| EURUSD_EURCHF | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURUSD_EURAUD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURUSD_EURCAD | 1 | 100% | inf | +30.2% | 0.0% | ✅ Viable |
| EURUSD_EURNZD | 2 | 100% | inf | +30.7% | 0.0% | ✅ Viable |
| EURGBP_EURJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURGBP_EURCHF | 1 | 100% | inf | +3.9% | 0.0% | ✅ Viable |
| EURJPY_EURCHF | 1 | 100% | inf | +129.3% | 0.0% | ✅ Viable |
| EURAUD_EURNZD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURAUD_EURCAD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURNZD_EURCAD | 2 | 100% | inf | +56.5% | 0.0% | ✅ Viable |
| GBPUSD_GBPJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| GBPUSD_GBPCHF | 1 | 100% | inf | +10.9% | 0.0% | ✅ Viable |
| GBPUSD_GBPAUD | 1 | 100% | inf | +167.0% | 0.0% | ✅ Viable |
| GBPUSD_GBPCAD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| GBPJPY_GBPCHF | 3 | 100% | inf | +111.3% | 0.0% | ✅ Viable |
| GBPJPY_GBPAUD | 3 | 67% | 8.98 | +84.4% | 0.5% | ✅ Viable |
| GBPAUD_GBPNZD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| GBPAUD_GBPCAD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| GBPNZD_GBPCAD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| AUDUSD_NZDUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| AUDJPY_NZDJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| AUDCAD_NZDCAD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| AUDCHF_NZDCHF | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| AUDNZD_AUDCAD | 2 | 50% | 11.07 | +438.3% | 1.1% | ✅ Viable |
| AUDNZD_AUDCHF | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| AUDUSD_AUDCAD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| NZDUSD_NZDCAD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| USDJPY_EURJPY | 1 | 100% | inf | +170.6% | 0.0% | ✅ Viable |
| USDJPY_GBPJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| USDJPY_AUDJPY | 1 | 100% | inf | +36.5% | 0.0% | ✅ Viable |
| USDJPY_CADJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURJPY_GBPJPY | 1 | 0% | 0.00 | -68.5% | 1.0% | ❌ Non viable |
| EURJPY_AUDJPY | 1 | 100% | inf | +200.2% | 0.0% | ✅ Viable |
| GBPJPY_AUDJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| AUDJPY_CADJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| NZDJPY_CADJPY | 2 | 50% | 6.69 | +54.1% | 0.0% | ✅ Viable |
| USDCHF_EURCHF | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| USDCHF_GBPCHF | 1 | 100% | inf | +11.4% | 0.0% | ✅ Viable |
| EURCHF_GBPCHF | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURCHF_CHFJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| CADCHF_CHFJPY | 1 | 100% | inf | +51.4% | 0.0% | ✅ Viable |
| USDCAD_EURCAD | 1 | 100% | inf | +25.2% | 0.0% | ✅ Viable |
| USDCAD_GBPCAD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURCAD_GBPCAD | 1 | 0% | 0.00 | -0.1% | 0.0% | ❌ Non viable |
| CADJPY_CADCHF | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURUSD_GBPUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURAUD_GBPAUD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURNZD_GBPNZD | 2 | 50% | 1.46 | +18.6% | 1.2% | ⚠️ Marginal |
| XAUUSD_XAGUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| XPTUSD_XPDUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| XAUUSD_XPTUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| XAGUSD_XPTUSD | 1 | 100% | inf | +61.0% | 0.0% | ✅ Viable |
| USOIL.cash_UKOIL.cash | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| CORN.c_WHEAT.c | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| CORN.c_SOYBEAN.c | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| WHEAT.c_SOYBEAN.c | 1 | 100% | inf | +121.0% | 0.0% | ✅ Viable |
| COFFEE.c_COCOA.c | 1 | 0% | 0.00 | -25.8% | 0.0% | ❌ Non viable |
| SUGAR.c_COTTON.c | 1 | 100% | inf | +109.9% | 0.0% | ✅ Viable |
| BTCUSD_ETHUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| ETHUSD_SOLUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| BTCUSD_LTCUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| ETHUSD_ADAUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| SOLUSD_AVAUSD | 1 | 0% | 0.00 | -28.9% | 0.0% | ❌ Non viable |
| BNBUSD_ETHUSD | 7 | 29% | 0.95 | -2.9% | 3.0% | ❌ Non viable |
| DOTUSD_ADAUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| AAPL_MSFT | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| GOOG_META | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| AMZN_MSFT | 2 | 50% | 2.08 | +56.6% | 1.5% | ✅ Viable |
| NVDA_AMZN | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| NFLX_GOOG | 7 | 57% | 0.33 | -18.9% | 1.4% | ❌ Non viable |
| META_GOOG | 6 | 33% | 1.11 | +6.3% | 5.0% | ❌ Non viable |
| TSLA_NVDA | 1 | 100% | inf | +62.9% | 0.0% | ✅ Viable |

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

### UK100.cash_EU50.cash

- **Trades**: 2 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +114.58% par trade
- **Half-life moyen**: 3.1 jours
- **Max Drawdown**: 0.0%

### EURUSD_EURGBP

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +33.06% par trade
- **Half-life moyen**: 4.3 jours
- **Max Drawdown**: 0.0%

### EURUSD_EURJPY

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +171.06% par trade
- **Half-life moyen**: 3.4 jours
- **Max Drawdown**: 0.0%

### EURUSD_EURCAD

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +30.24% par trade
- **Half-life moyen**: 3.4 jours
- **Max Drawdown**: 0.0%

### EURUSD_EURNZD

- **Trades**: 2 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +30.73% par trade
- **Half-life moyen**: 4.2 jours
- **Max Drawdown**: 0.0%

### EURGBP_EURCHF

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +3.94% par trade
- **Half-life moyen**: 6.3 jours
- **Max Drawdown**: 0.0%

### EURJPY_EURCHF

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +129.32% par trade
- **Half-life moyen**: 6.6 jours
- **Max Drawdown**: 0.0%

### EURNZD_EURCAD

- **Trades**: 2 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +56.49% par trade
- **Half-life moyen**: 4.3 jours
- **Max Drawdown**: 0.0%

### GBPUSD_GBPCHF

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +10.85% par trade
- **Half-life moyen**: 4.5 jours
- **Max Drawdown**: 0.0%

### GBPUSD_GBPAUD

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +167.03% par trade
- **Half-life moyen**: 4.8 jours
- **Max Drawdown**: 0.0%

### GBPJPY_GBPCHF

- **Trades**: 3 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +111.28% par trade
- **Half-life moyen**: 3.8 jours
- **Max Drawdown**: 0.0%

### GBPJPY_GBPAUD

- **Trades**: 3 (Win rate: 67%)
- **Profit Factor**: 8.98
- **Expectancy**: +84.37% par trade
- **Half-life moyen**: 3.6 jours
- **Max Drawdown**: 0.5%

### AUDNZD_AUDCAD

- **Trades**: 2 (Win rate: 50%)
- **Profit Factor**: 11.07
- **Expectancy**: +438.35% par trade
- **Half-life moyen**: 4.7 jours
- **Max Drawdown**: 1.1%

### USDJPY_EURJPY

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +170.57% par trade
- **Half-life moyen**: 3.4 jours
- **Max Drawdown**: 0.0%

### USDJPY_AUDJPY

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +36.51% par trade
- **Half-life moyen**: 3.6 jours
- **Max Drawdown**: 0.0%

### EURJPY_AUDJPY

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +200.19% par trade
- **Half-life moyen**: 4.2 jours
- **Max Drawdown**: 0.0%

### NZDJPY_CADJPY

- **Trades**: 2 (Win rate: 50%)
- **Profit Factor**: 6.69
- **Expectancy**: +54.15% par trade
- **Half-life moyen**: 4.9 jours
- **Max Drawdown**: 0.0%

### USDCHF_GBPCHF

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +11.41% par trade
- **Half-life moyen**: 4.4 jours
- **Max Drawdown**: 0.0%

### CADCHF_CHFJPY

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +51.43% par trade
- **Half-life moyen**: 3.3 jours
- **Max Drawdown**: 0.0%

### USDCAD_EURCAD

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +25.21% par trade
- **Half-life moyen**: 3.4 jours
- **Max Drawdown**: 0.0%

### XAGUSD_XPTUSD

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +60.96% par trade
- **Half-life moyen**: 3.5 jours
- **Max Drawdown**: 0.0%

### WHEAT.c_SOYBEAN.c

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +120.97% par trade
- **Half-life moyen**: 3.9 jours
- **Max Drawdown**: 0.0%

### SUGAR.c_COTTON.c

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +109.85% par trade
- **Half-life moyen**: 4.8 jours
- **Max Drawdown**: 0.0%

### AMZN_MSFT

- **Trades**: 2 (Win rate: 50%)
- **Profit Factor**: 2.08
- **Expectancy**: +56.61% par trade
- **Half-life moyen**: 3.7 jours
- **Max Drawdown**: 1.5%

### TSLA_NVDA

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +62.87% par trade
- **Half-life moyen**: 4.2 jours
- **Max Drawdown**: 0.0%


## Paramètres

- Z-score entry: ±2.0
- Z-score exit: ±1.0
- Z-score stop: ±3.0

---
*Rapport généré par Pairs Trading Backtest v1.1.0*