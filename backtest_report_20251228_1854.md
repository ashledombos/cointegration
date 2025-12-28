# 📊 Rapport de Backtest - Pairs Trading

Date: 2025-12-28 18:54

## Résumé Global

| Paire | Trades | Win Rate | PF | Expectancy | Max DD | Verdict |
|-------|--------|----------|-----|------------|--------|---------|
| US500.cash_US100.cash | 3 | 33% | 0.01 | -69.9% | 3.2% | ❌ Non viable |
| US500.cash_US30.cash | 2 | 100% | inf | +91.6% | 0.0% | ✅ Viable |
| US100.cash_US30.cash | 1 | 100% | inf | +117.9% | 0.0% | ✅ Viable |
| US500.cash_US2000.cash | 2 | 50% | 3.21 | +23.6% | 0.0% | ✅ Viable |
| US100.cash_US2000.cash | 7 | 57% | 1.69 | +17.8% | 2.3% | ✅ Viable |
| US30.cash_US2000.cash | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| GER40.cash_FRA40.cash | 1 | 100% | inf | +146.2% | 0.0% | ✅ Viable |
| GER40.cash_EU50.cash | 4 | 25% | 0.34 | -48.5% | 3.1% | ❌ Non viable |
| FRA40.cash_EU50.cash | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| UK100.cash_GER40.cash | 1 | 100% | inf | +100.4% | 0.0% | ✅ Viable |
| UK100.cash_EU50.cash | 2 | 100% | inf | +40.7% | 0.0% | ✅ Viable |
| SPN35.cash_EU50.cash | 3 | 33% | 0.42 | -33.0% | 2.5% | ❌ Non viable |
| US500.cash_GER40.cash | 2 | 50% | 13.88 | +27.6% | 0.0% | ✅ Viable |
| US500.cash_UK100.cash | 1 | 100% | inf | +16.6% | 0.0% | ✅ Viable |
| US100.cash_GER40.cash | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURUSD_EURGBP | 2 | 100% | inf | +77.4% | 0.0% | ✅ Viable |
| EURUSD_EURJPY | 1 | 100% | inf | +105.1% | 0.0% | ✅ Viable |
| EURUSD_EURCHF | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURUSD_EURAUD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURUSD_EURCAD | 1 | 0% | 0.00 | -55.9% | 0.8% | ❌ Non viable |
| EURUSD_EURNZD | 2 | 100% | inf | +30.7% | 0.0% | ✅ Viable |
| EURGBP_EURJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURGBP_EURCHF | 2 | 100% | inf | +43.6% | 0.0% | ✅ Viable |
| EURJPY_EURCHF | 1 | 100% | inf | +102.0% | 0.0% | ✅ Viable |
| EURAUD_EURNZD | 1 | 100% | inf | +43.3% | 0.0% | ✅ Viable |
| EURAUD_EURCAD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURNZD_EURCAD | 2 | 100% | inf | +56.5% | 0.0% | ✅ Viable |
| GBPUSD_GBPJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| GBPUSD_GBPCHF | 1 | 0% | 0.00 | -65.2% | 0.0% | ❌ Non viable |
| GBPUSD_GBPAUD | 1 | 100% | inf | +167.0% | 0.0% | ✅ Viable |
| GBPUSD_GBPCAD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| GBPJPY_GBPCHF | 3 | 100% | inf | +70.2% | 0.0% | ✅ Viable |
| GBPJPY_GBPAUD | 3 | 67% | 8.98 | +84.4% | 0.5% | ✅ Viable |
| GBPAUD_GBPNZD | 1 | 100% | inf | +157.3% | 0.0% | ✅ Viable |
| GBPAUD_GBPCAD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| GBPNZD_GBPCAD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| AUDUSD_NZDUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| AUDJPY_NZDJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| AUDCAD_NZDCAD | 1 | 0% | 0.00 | -0.2% | 0.0% | ❌ Non viable |
| AUDCHF_NZDCHF | 1 | 100% | inf | +90.4% | 0.0% | ✅ Viable |
| AUDNZD_AUDCAD | 2 | 50% | 11.07 | +438.3% | 1.1% | ✅ Viable |
| AUDNZD_AUDCHF | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| AUDUSD_AUDCAD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| NZDUSD_NZDCAD | 1 | 100% | inf | +128.7% | 0.0% | ✅ Viable |
| USDJPY_EURJPY | 1 | 100% | inf | +105.0% | 0.0% | ✅ Viable |
| USDJPY_GBPJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| USDJPY_AUDJPY | 2 | 50% | 0.60 | -6.5% | 0.5% | ❌ Non viable |
| USDJPY_CADJPY | 1 | 100% | inf | +122.6% | 0.0% | ✅ Viable |
| EURJPY_GBPJPY | 1 | 0% | 0.00 | -162.2% | 2.4% | ❌ Non viable |
| EURJPY_AUDJPY | 3 | 67% | 10.65 | +83.9% | 0.4% | ✅ Viable |
| GBPJPY_AUDJPY | 2 | 100% | inf | +64.3% | 0.0% | ✅ Viable |
| AUDJPY_CADJPY | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| NZDJPY_CADJPY | 3 | 67% | 18.38 | +369.6% | 0.0% | ✅ Viable |
| USDCHF_EURCHF | 1 | 100% | inf | +41.3% | 0.0% | ✅ Viable |
| USDCHF_GBPCHF | 2 | 50% | 1.49 | +15.8% | 0.0% | ⚠️ Marginal |
| EURCHF_GBPCHF | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURCHF_CHFJPY | 1 | 0% | 0.00 | -74.1% | 0.0% | ❌ Non viable |
| CADCHF_CHFJPY | 2 | 100% | inf | +1.5% | 0.0% | ✅ Viable |
| USDCAD_EURCAD | 1 | 0% | 0.00 | -54.4% | 0.8% | ❌ Non viable |
| USDCAD_GBPCAD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURCAD_GBPCAD | 1 | 0% | 0.00 | -81.0% | 0.0% | ❌ Non viable |
| CADJPY_CADCHF | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURUSD_GBPUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| EURAUD_GBPAUD | 1 | 100% | inf | +88.9% | 0.0% | ✅ Viable |
| EURNZD_GBPNZD | 2 | 50% | 1.46 | +18.6% | 1.2% | ⚠️ Marginal |
| XAUUSD_XAGUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| XPTUSD_XPDUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| XAUUSD_XPTUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| XAGUSD_XPTUSD | 1 | 100% | inf | +24.7% | 0.0% | ✅ Viable |
| XAUUSD_XAUEUR | 15 | 33% | 0.50 | -1022.9% | 48.4% | ❌ Non viable |
| XAGUSD_XAGEUR | 12 | 33% | 32.38 | +232.6% | 1.4% | ⚠️ Marginal |
| XAGAUD_XAGUSD | 12 | 33% | 32.38 | +232.6% | 1.4% | ⚠️ Marginal |
| USOIL.cash_UKOIL.cash | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| NATGAS.cash_USOIL.cash | 3 | 33% | 2.17 | +15.8% | 0.6% | ⚠️ Marginal |
| CORN.c_WHEAT.c | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| CORN.c_SOYBEAN.c | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| WHEAT.c_SOYBEAN.c | 1 | 100% | inf | +121.0% | 0.0% | ✅ Viable |
| COFFEE.c_COCOA.c | 1 | 0% | 0.00 | -25.8% | 0.0% | ❌ Non viable |
| SUGAR.c_COTTON.c | 1 | 100% | inf | +86.5% | 0.0% | ✅ Viable |
| BTCUSD_ETHUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| BTCUSD_BNBUSD | 6 | 50% | 0.67 | -14.8% | 3.7% | ❌ Non viable |
| BTCUSD_SOLUSD | 6 | 33% | 0.30 | -37.5% | 4.3% | ❌ Non viable |
| BTCUSD_XRPUSD | 1 | 100% | inf | +53.3% | 0.0% | ✅ Viable |
| ETHUSD_SOLUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| ETHUSD_BNBUSD | 3 | 33% | 0.54 | -18.7% | 1.6% | ❌ Non viable |
| ETHUSD_ADAUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| BTCUSD_LTCUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| SOLUSD_AVAUSD | 1 | 0% | 0.00 | -104.8% | 0.0% | ❌ Non viable |
| DOTUSD_ADAUSD | 1 | 100% | inf | +5.5% | 0.0% | ✅ Viable |
| XLMUSD_XRPUSD | 1 | 0% | 0.00 | -10.6% | 0.2% | ❌ Non viable |
| LNKUSD_ETHUSD | 1 | 0% | 0.00 | -13.8% | 0.0% | ❌ Non viable |
| UNIUSD_ETHUSD | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| AAPL_MSFT | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| GOOG_META | 1 | 100% | inf | +88.3% | 0.0% | ✅ Viable |
| AMZN_MSFT | 6 | 67% | 1.68 | +27.8% | 2.1% | ✅ Viable |
| NVDA_AMZN | 1 | 0% | 0.00 | -19.7% | 0.0% | ❌ Non viable |
| NFLX_GOOG | 7 | 57% | 0.33 | -18.9% | 1.4% | ❌ Non viable |
| META_GOOG | 6 | 33% | 0.75 | -21.0% | 7.4% | ❌ Non viable |
| TSLA_NVDA | 2 | 100% | inf | +83.7% | 0.0% | ✅ Viable |
| LVMH_RACE | 5 | 40% | 0.47 | -24.9% | 3.3% | ❌ Non viable |
| ALVG_BAYGn | 0 | 0% | 0.00 | +0.0% | 0.0% | ❌ No trades |
| DBKGn_BAC | 2 | 50% | 1.88 | +38.3% | 0.0% | ✅ Viable |

## Paires Viables

### US500.cash_US30.cash

- **Trades**: 2 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +91.62% par trade
- **Half-life moyen**: 3.4 jours
- **Max Drawdown**: 0.0%

### US100.cash_US30.cash

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +117.94% par trade
- **Half-life moyen**: 3.2 jours
- **Max Drawdown**: 0.0%

### US500.cash_US2000.cash

- **Trades**: 2 (Win rate: 50%)
- **Profit Factor**: 3.21
- **Expectancy**: +23.65% par trade
- **Half-life moyen**: 3.2 jours
- **Max Drawdown**: 0.0%

### US100.cash_US2000.cash

- **Trades**: 7 (Win rate: 57%)
- **Profit Factor**: 1.69
- **Expectancy**: +17.83% par trade
- **Half-life moyen**: 3.6 jours
- **Max Drawdown**: 2.3%

### GER40.cash_FRA40.cash

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +146.20% par trade
- **Half-life moyen**: 3.5 jours
- **Max Drawdown**: 0.0%

### UK100.cash_GER40.cash

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +100.44% par trade
- **Half-life moyen**: 4.0 jours
- **Max Drawdown**: 0.0%

### UK100.cash_EU50.cash

- **Trades**: 2 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +40.70% par trade
- **Half-life moyen**: 3.1 jours
- **Max Drawdown**: 0.0%

### US500.cash_GER40.cash

- **Trades**: 2 (Win rate: 50%)
- **Profit Factor**: 13.88
- **Expectancy**: +27.60% par trade
- **Half-life moyen**: 4.4 jours
- **Max Drawdown**: 0.0%

### US500.cash_UK100.cash

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +16.59% par trade
- **Half-life moyen**: 4.5 jours
- **Max Drawdown**: 0.0%

### EURUSD_EURGBP

- **Trades**: 2 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +77.40% par trade
- **Half-life moyen**: 4.3 jours
- **Max Drawdown**: 0.0%

### EURUSD_EURJPY

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +105.13% par trade
- **Half-life moyen**: 3.4 jours
- **Max Drawdown**: 0.0%

### EURUSD_EURNZD

- **Trades**: 2 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +30.73% par trade
- **Half-life moyen**: 4.2 jours
- **Max Drawdown**: 0.0%

### EURGBP_EURCHF

- **Trades**: 2 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +43.65% par trade
- **Half-life moyen**: 6.3 jours
- **Max Drawdown**: 0.0%

### EURJPY_EURCHF

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +101.99% par trade
- **Half-life moyen**: 6.6 jours
- **Max Drawdown**: 0.0%

### EURAUD_EURNZD

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +43.26% par trade
- **Half-life moyen**: 11.2 jours
- **Max Drawdown**: 0.0%

### EURNZD_EURCAD

- **Trades**: 2 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +56.49% par trade
- **Half-life moyen**: 4.3 jours
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
- **Expectancy**: +70.23% par trade
- **Half-life moyen**: 3.8 jours
- **Max Drawdown**: 0.0%

### GBPJPY_GBPAUD

- **Trades**: 3 (Win rate: 67%)
- **Profit Factor**: 8.98
- **Expectancy**: +84.37% par trade
- **Half-life moyen**: 3.6 jours
- **Max Drawdown**: 0.5%

### GBPAUD_GBPNZD

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +157.30% par trade
- **Half-life moyen**: 7.4 jours
- **Max Drawdown**: 0.0%

### AUDCHF_NZDCHF

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +90.41% par trade
- **Half-life moyen**: 5.4 jours
- **Max Drawdown**: 0.0%

### AUDNZD_AUDCAD

- **Trades**: 2 (Win rate: 50%)
- **Profit Factor**: 11.07
- **Expectancy**: +438.35% par trade
- **Half-life moyen**: 4.7 jours
- **Max Drawdown**: 1.1%

### NZDUSD_NZDCAD

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +128.66% par trade
- **Half-life moyen**: 3.7 jours
- **Max Drawdown**: 0.0%

### USDJPY_EURJPY

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +104.98% par trade
- **Half-life moyen**: 3.4 jours
- **Max Drawdown**: 0.0%

### USDJPY_CADJPY

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +122.58% par trade
- **Half-life moyen**: 4.4 jours
- **Max Drawdown**: 0.0%

### EURJPY_AUDJPY

- **Trades**: 3 (Win rate: 67%)
- **Profit Factor**: 10.65
- **Expectancy**: +83.86% par trade
- **Half-life moyen**: 4.2 jours
- **Max Drawdown**: 0.4%

### GBPJPY_AUDJPY

- **Trades**: 2 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +64.35% par trade
- **Half-life moyen**: 3.4 jours
- **Max Drawdown**: 0.0%

### NZDJPY_CADJPY

- **Trades**: 3 (Win rate: 67%)
- **Profit Factor**: 18.38
- **Expectancy**: +369.59% par trade
- **Half-life moyen**: 4.9 jours
- **Max Drawdown**: 0.0%

### USDCHF_EURCHF

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +41.26% par trade
- **Half-life moyen**: 3.7 jours
- **Max Drawdown**: 0.0%

### CADCHF_CHFJPY

- **Trades**: 2 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +1.55% par trade
- **Half-life moyen**: 3.3 jours
- **Max Drawdown**: 0.0%

### EURAUD_GBPAUD

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +88.87% par trade
- **Half-life moyen**: 3.2 jours
- **Max Drawdown**: 0.0%

### XAGUSD_XPTUSD

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +24.67% par trade
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
- **Expectancy**: +86.53% par trade
- **Half-life moyen**: 4.8 jours
- **Max Drawdown**: 0.0%

### BTCUSD_XRPUSD

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +53.34% par trade
- **Half-life moyen**: 6.2 jours
- **Max Drawdown**: 0.0%

### DOTUSD_ADAUSD

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +5.55% par trade
- **Half-life moyen**: 4.2 jours
- **Max Drawdown**: 0.0%

### GOOG_META

- **Trades**: 1 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +88.32% par trade
- **Half-life moyen**: 5.6 jours
- **Max Drawdown**: 0.0%

### AMZN_MSFT

- **Trades**: 6 (Win rate: 67%)
- **Profit Factor**: 1.68
- **Expectancy**: +27.76% par trade
- **Half-life moyen**: 3.7 jours
- **Max Drawdown**: 2.1%

### TSLA_NVDA

- **Trades**: 2 (Win rate: 100%)
- **Profit Factor**: inf
- **Expectancy**: +83.67% par trade
- **Half-life moyen**: 4.2 jours
- **Max Drawdown**: 0.0%

### DBKGn_BAC

- **Trades**: 2 (Win rate: 50%)
- **Profit Factor**: 1.88
- **Expectancy**: +38.28% par trade
- **Half-life moyen**: 4.4 jours
- **Max Drawdown**: 0.0%


## Paramètres

- Z-score entry: ±1.5
- Z-score exit: ±1.0
- Z-score stop: ±3.0

---
*Rapport généré par Pairs Trading Backtest v1.1.0*