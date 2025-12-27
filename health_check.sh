#!/bin/bash
# =============================================================================
# Health Check - Vérifie que le bot tourne et alerte sinon
# À lancer via cron toutes les heures
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

source .env 2>/dev/null || true

send_alert() {
    local title="$1"
    local message="$2"
    local priority="${3:-high}"
    
    if [ -n "$NTFY_TOPIC" ]; then
        curl -s \
            -H "Title: $title" \
            -H "Priority: $priority" \
            -H "Tags: warning" \
            -d "$message" \
            "${NTFY_SERVER:-https://ntfy.sh}/$NTFY_TOPIC" > /dev/null 2>&1
    fi
}

# Vérifier si le service est actif
if ! systemctl is-active --quiet cointegration; then
    send_alert \
        "⚠️ Bot Down!" \
        "Cointegration bot is not running!\nAttempting restart..." \
        "urgent"
    
    # Tenter un redémarrage
    sudo systemctl restart cointegration
    
    sleep 5
    
    if systemctl is-active --quiet cointegration; then
        send_alert \
            "✅ Bot Restarted" \
            "Bot successfully restarted" \
            "default"
    else
        send_alert \
            "🚨 Bot Failed!" \
            "Failed to restart bot. Manual intervention required!" \
            "urgent"
    fi
fi

# Vérifier si le log a été mis à jour récemment (moins de 10 min)
LOG_FILE="$SCRIPT_DIR/logs/bot.log"
if [ -f "$LOG_FILE" ]; then
    LAST_MOD=$(stat -c %Y "$LOG_FILE" 2>/dev/null || echo 0)
    NOW=$(date +%s)
    DIFF=$((NOW - LAST_MOD))
    
    # Si pas de mise à jour depuis 10 min (600 sec)
    if [ $DIFF -gt 600 ]; then
        send_alert \
            "⚠️ Bot Stalled?" \
            "No log activity for $((DIFF / 60)) minutes" \
            "high"
    fi
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Health check OK"
