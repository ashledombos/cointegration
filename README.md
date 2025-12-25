# 📊 Pairs Trading - Système de Signaux par Coïntégration

Système de génération de signaux pour le pairs trading basé sur la coïntégration statistique. Conçu pour FTMO et autres prop firms, avec alertes Telegram/Discord.

## 🎯 Fonctionnalités

- **Scan automatique** de l'univers d'instruments (forex, indices, commodities, crypto)
- **Tests de coïntégration** Engle-Granger et Johansen
- **Calcul du half-life** pour estimer le temps de mean reversion
- **Machine d'état** pour gérer les positions (entrées, sorties, stop-loss, scaling)
- **Alertes temps réel** via Telegram et/ou Discord
- **Validation périodique** de la coïntégration
- **Persistance SQLite** des paires, positions et historique

## 📁 Structure du Projet

```
pairs_trading/
├── config.py           # Configuration centralisée
├── data_fetcher.py     # Récupération des données (Dukascopy, yfinance, CCXT)
├── cointegration.py    # Tests statistiques et calculs
├── signals.py          # Machine d'état et génération de signaux
├── alerts.py           # Notifications Telegram/Discord
├── database.py         # Persistance SQLite
├── scanner.py          # Scan de l'univers pour trouver les paires
├── main.py             # Point d'entrée et scheduler
├── requirements.txt    # Dépendances Python
└── README.md           # Cette documentation
```

## 🚀 Installation

### 1. Cloner et installer les dépendances Python

```bash
cd pairs_trading
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2. Installer Dukascopy Node (optionnel, pour données historiques)

```bash
npm install -g dukascopy-node
```

### 3. Configurer les variables d'environnement

Créer un fichier `.env` :

```env
# Telegram (optionnel)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Discord (optionnel)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

## ⚙️ Configuration

Modifier `config.py` pour ajuster les paramètres :

```python
# Seuils de signal (z-score)
z_entry = 2.0      # Entrée à ±2σ
z_exit = 1.0       # Sortie à ±1σ (mean reversion)
z_stop = 3.0       # Stop-loss à ±3σ

# Coïntégration
pvalue_threshold = 0.05   # Seuil p-value
min_half_life = 5         # Half-life min (jours)
max_half_life = 50        # Half-life max (jours)

# Risk Management
risk_per_trade_pct = 1.5  # Risque par trade (% capital)
max_active_pairs = 20     # Max paires simultanées
```

## 📖 Utilisation

### Mode Monitoring Continu

```bash
python main.py
```

Le bot va :
1. Vérifier les z-scores toutes les 5 minutes
2. Valider la coïntégration quotidiennement (06:00 UTC)
3. Scanner de nouvelles paires chaque dimanche (18:00 UTC)

### Commandes Ponctuelles

```bash
# Scan complet de l'univers
python main.py --scan

# Valider les paires existantes
python main.py --validate

# Afficher le statut
python main.py --status

# Tester les alertes
python main.py --test-alerts

# Générer un rapport
python main.py --report
```

## 📊 Méthodologie

### 1. Test de Coïntégration

Le système utilise le test **Engle-Granger** (deux étapes) :
1. Régression OLS : `Y = α + β × X + ε`
2. Test ADF sur les résidus

Une paire est considérée coïntégrée si :
- p-value < 0.05
- Half-life entre 5 et 50 jours

### 2. Calcul du Spread

```
spread = price1 - hedge_ratio × price2
```

### 3. Z-Score

```
z-score = (spread - mean) / std
```

Le lookback pour mean/std est basé sur le half-life (typiquement half_life / 2).

### 4. Signaux

| Z-Score | Signal |
|---------|--------|
| z ≤ -2.0 | ENTRY LONG (acheter S1, vendre S2) |
| z ≥ +2.0 | ENTRY SHORT (vendre S1, acheter S2) |
| z → 0 | EXIT (mean reversion) |
| z ≤ -3.0 ou z ≥ +3.0 | STOP LOSS |

### 5. Scaling (optionnel)

Entrées progressives :
- 40% à z = ±2.0
- 35% à z = ±2.5
- 25% à z = ±3.0

## 📱 Format des Alertes

```
🟢 ENTRY_LONG - EURUSD_GBPUSD

📊 Z-Score: -2.15σ
💹 Spread: -0.00125 (μ=0.0, σ=0.00058)
📐 Hedge Ratio: 0.8523
⏱ Half-Life: 14.5 jours

💰 Prix actuels:
• EURUSD: 1.08500
• GBPUSD: 1.27340

🎯 Action: LONG EURUSD, SHORT GBPUSD
```

## 🗄️ Base de Données

SQLite avec 3 tables principales :
- `cointegrated_pairs` : Paires validées avec leurs paramètres
- `positions` : État des positions ouvertes
- `signal_history` : Historique de tous les signaux

## ⚠️ Avertissements

1. **Ce n'est PAS un système de trading automatique** - il génère uniquement des signaux
2. **Le pairs trading comporte des risques** - la coïntégration peut se casser soudainement
3. **Backtestez avant d'utiliser** - les performances passées ne garantissent pas les futures
4. **Respectez les règles de votre prop firm** - notamment les limites de drawdown

## 🔧 Dépannage

### Pas de données Dukascopy

```bash
# Vérifier l'installation
npx dukascopy-node --help

# Tester manuellement
npx dukascopy-node -i eurusd -from 2024-01-01 -to 2024-01-31 -t d1 -f csv
```

### Alertes non reçues

1. Vérifier les tokens dans `.env`
2. Pour Telegram : démarrer une conversation avec le bot d'abord
3. Tester avec `python main.py --test-alerts`

### Erreur de coïntégration

Si beaucoup de paires échouent, vérifier :
- Qualité des données (gaps, erreurs)
- Période de lookback suffisante (≥100 observations)
- Alignement des timestamps entre les séries

## 📚 Références

- Engle, R. F., & Granger, C. W. (1987). Co-integration and error correction
- Gatev, E., Goetzmann, W. N., & Rouwenhorst, K. G. (2006). Pairs trading
- [ArbirageLab Documentation](https://hudson-and-thames-arbitragelab.readthedocs-hosted.com/)

## 📄 Licence

MIT - Utilisation libre pour usage personnel et commercial.

---

**Développé pour le trading systématique sur prop firms (FTMO, Goat Funded Trader, etc.)**
