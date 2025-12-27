#!/bin/bash
# =============================================================================
# Pairs Trading Bot - Wrapper avec alertes d'erreur
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Charger les variables d'environnement
source .env 2>/dev/null || true

# Fonction pour envoyer une alerte Ntfy
send_alert() {
    local title="$1"
    local message="$2"
    local priority="${3:-high}"
    local tags="${4:-warning}"
    
    if [ -n "$NTFY_TOPIC" ]; then
        curl -s \
            -H "Title: $title" \
            -H "Priority: $priority" \
            -H "Tags: $tags" \
            -d "$message" \
            "${NTFY_SERVER:-https://ntfy.sh}/$NTFY_TOPIC" > /dev/null 2>&1
    fi
}

# Fonction pour envoyer une alerte en cas d'erreur
on_error() {
    local exit_code=$?
    local error_msg="Bot crashed with exit code $exit_code"
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $error_msg"
    
    send_alert \
        "🚨 Bot Crashed!" \
        "$error_msg\nServer: $(hostname)\nTime: $(date '+%Y-%m-%d %H:%M:%S')" \
        "urgent" \
        "rotating_light,skull"
}

# Trap les erreurs
trap on_error ERR

# Envoyer notification de démarrage
send_alert \
    "🚀 Bot Started" \
    "Pairs Trading bot started on $(hostname)" \
    "default" \
    "rocket"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Pairs Trading Bot..."

# Lancer le bot
exec .venv/bin/python main.py run
