#!/bin/bash
# =============================================================================
# Installation du service Pairs Trading Bot
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER=$(whoami)

echo "=== Installation du bot Pairs Trading ==="
echo "Dossier: $SCRIPT_DIR"
echo "User: $USER"
echo ""

# Créer le dossier logs
mkdir -p "$SCRIPT_DIR/logs"

# Rendre les scripts exécutables
chmod +x "$SCRIPT_DIR/run_bot.sh"
chmod +x "$SCRIPT_DIR/health_check.sh"

# Vérifier le .env
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "⚠️  Fichier .env manquant!"
    echo "   Copie .env.example vers .env et configure-le"
    exit 1
fi

# Vérifier NTFY_TOPIC
source "$SCRIPT_DIR/.env"
if [ -z "$NTFY_TOPIC" ]; then
    echo "⚠️  NTFY_TOPIC non configuré dans .env"
    echo "   Les alertes d'erreur ne fonctionneront pas"
    read -p "Continuer quand même? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Mettre à jour le fichier service avec le bon user
sed -i "s/User=raphael/User=$USER/" "$SCRIPT_DIR/cointegration.service"
sed -i "s/Group=raphael/Group=$USER/" "$SCRIPT_DIR/cointegration.service"
sed -i "s|/home/raphael/dev/cointegration|$SCRIPT_DIR|g" "$SCRIPT_DIR/cointegration.service"

echo ""
echo "=== Installation du service systemd ==="

# Copier le service
sudo cp "$SCRIPT_DIR/cointegration.service" /etc/systemd/system/

# Recharger systemd
sudo systemctl daemon-reload

# Activer le service
sudo systemctl enable cointegration

echo ""
echo "=== Configuration du health check (cron) ==="

# Ajouter le cron pour health check (toutes les heures)
CRON_CMD="0 * * * * $SCRIPT_DIR/health_check.sh >> $SCRIPT_DIR/logs/health.log 2>&1"

# Vérifier si le cron existe déjà
if ! crontab -l 2>/dev/null | grep -q "health_check.sh"; then
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo "✅ Cron health check ajouté"
else
    echo "ℹ️  Cron health check déjà présent"
fi

echo ""
echo "=== Installation terminée ==="
echo ""
echo "Commandes utiles:"
echo "  sudo systemctl start cointegration    # Démarrer"
echo "  sudo systemctl stop cointegration     # Arrêter"
echo "  sudo systemctl status cointegration   # Status"
echo "  journalctl -u cointegration -f        # Logs temps réel"
echo "  tail -f $SCRIPT_DIR/logs/bot.log      # Logs fichier"
echo ""
echo "Pour démarrer maintenant:"
echo "  sudo systemctl start cointegration"
