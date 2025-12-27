"""
Alerts Module - Notifications Telegram, Discord et Ntfy
=========================================================
"""

import asyncio
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dataclasses import dataclass, field
from loguru import logger

from config import config
from signals import Signal, SignalType

# Telegram
try:
    from telegram import Bot
    from telegram.constants import ParseMode
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("python-telegram-bot non installé")

# Discord
try:
    from discord_webhook import DiscordWebhook, DiscordEmbed
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    logger.warning("discord-webhook non installé")


@dataclass
class AlertCooldown:
    """Gestion du cooldown des alertes par paire."""
    last_alerts: Dict[str, datetime] = field(default_factory=dict)
    cooldown_minutes: int = 5
    
    def can_send(self, pair_id: str) -> bool:
        if pair_id not in self.last_alerts:
            return True
        
        elapsed = datetime.now() - self.last_alerts[pair_id]
        return elapsed > timedelta(minutes=self.cooldown_minutes)
    
    def mark_sent(self, pair_id: str):
        self.last_alerts[pair_id] = datetime.now()


class TelegramNotifier:
    """Envoi de notifications via Telegram."""
    
    def __init__(self, bot_token: str, chat_id: str):
        if not TELEGRAM_AVAILABLE:
            raise ImportError("python-telegram-bot requis: pip install python-telegram-bot")
        
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id
        self.cooldown = AlertCooldown(cooldown_minutes=config.signal.alert_cooldown_minutes)
    
    async def send_signal(self, signal: Signal) -> bool:
        """Envoie un signal via Telegram."""
        if not self.cooldown.can_send(signal.pair_id):
            logger.debug(f"Alert cooldown for {signal.pair_id}")
            return False
        
        message = self._format_signal(signal)
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            self.cooldown.mark_sent(signal.pair_id)
            logger.info(f"Telegram alert sent: {signal.signal_type.value}")
            return True
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return False
    
    async def send_daily_report(self, report: Dict) -> bool:
        """Envoie le rapport quotidien."""
        message = self._format_daily_report(report)
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            return True
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return False
    
    async def send_message(self, text: str) -> bool:
        """Envoie un message simple."""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=ParseMode.MARKDOWN
            )
            return True
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return False
    
    def _format_signal(self, signal: Signal) -> str:
        emoji_map = {
            SignalType.OPEN_LONG_SPREAD: "🟢",
            SignalType.OPEN_SHORT_SPREAD: "🔴",
            SignalType.CLOSE_LONG_SPREAD: "✅",
            SignalType.CLOSE_SHORT_SPREAD: "✅",
            SignalType.STOP_LOSS: "🛑",
            SignalType.TIME_EXIT: "⏰",
            SignalType.BREAKDOWN_EXIT: "⚠️",
            SignalType.SCALE_IN_LONG: "📈",
            SignalType.SCALE_IN_SHORT: "📉",
        }
        emoji = emoji_map.get(signal.signal_type, "📊")
        
        # Determine if entry or exit
        is_entry = signal.signal_type in [
            SignalType.OPEN_LONG_SPREAD, SignalType.OPEN_SHORT_SPREAD,
            SignalType.SCALE_IN_LONG, SignalType.SCALE_IN_SHORT
        ]
        is_exit = signal.signal_type in [
            SignalType.CLOSE_LONG_SPREAD, SignalType.CLOSE_SHORT_SPREAD,
            SignalType.STOP_LOSS, SignalType.TIME_EXIT, SignalType.BREAKDOWN_EXIT
        ]
        
        # Header
        if signal.signal_type in [SignalType.OPEN_LONG_SPREAD, SignalType.SCALE_IN_LONG]:
            header = f"{emoji} *ENTRY LONG SPREAD*"
        elif signal.signal_type in [SignalType.OPEN_SHORT_SPREAD, SignalType.SCALE_IN_SHORT]:
            header = f"{emoji} *ENTRY SHORT SPREAD*"
        elif signal.signal_type == SignalType.STOP_LOSS:
            header = f"{emoji} *STOP LOSS - EXIT NOW*"
        elif signal.signal_type == SignalType.TIME_EXIT:
            header = f"{emoji} *TIME EXIT - CLOSE POSITIONS*"
        elif signal.signal_type == SignalType.BREAKDOWN_EXIT:
            header = f"{emoji} *BREAKDOWN - EXIT*"
        else:
            header = f"{emoji} *EXIT SIGNAL*"
        
        lines = [
            header,
            "━" * 28,
            f"*Paire:* `{signal.symbol1}` / `{signal.symbol2}`",
            f"*Z-Score:* `{signal.zscore:.2f}`",
        ]
        
        if is_entry:
            # Calculate position sizing
            # Base: 1 lot for first instrument, hedge_ratio for second
            base_lots = 1.0
            hedge_lots = abs(signal.hedge_ratio * base_lots)
            
            # For very small hedge ratios (like EURGBP/EURJPY), adjust
            if hedge_lots < 0.01:
                # Inverse: use second as base
                hedge_lots = 1.0
                base_lots = 1.0 / abs(signal.hedge_ratio) if signal.hedge_ratio != 0 else 1.0
            
            if signal.signal_type in [SignalType.OPEN_LONG_SPREAD, SignalType.SCALE_IN_LONG]:
                action1, action2 = "BUY", "SELL"
            else:
                action1, action2 = "SELL", "BUY"
            
            lines.extend([
                "",
                "📊 *POSITIONS À OUVRIR:*",
                "```",
                f"{action1:4} {signal.symbol1:12} {base_lots:.2f} lots",
                f"{action2:4} {signal.symbol2:12} {hedge_lots:.2f} lots",
                "```",
                "",
                "⚠️ *PAS DE SL/TP INDIVIDUELS !*",
                "_Surveiller le z-score du spread_",
                "",
                "📍 *SORTIES:*",
                f"• TP: z-score → `{config.signal.zscore_exit:.1f}` (convergence)",
                f"• SL: z-score → `±{config.signal.zscore_stop:.1f}` (divergence)",
                f"• TIME: Sortir après `{int(signal.half_life * config.signal.max_holding_multiplier)}j` max",
                "",
                f"⏱ *Délai de réaction:* ~1-2h (TF 4H)",
            ])
            
            if signal.price1 and signal.price2:
                lines.extend([
                    "",
                    f"💹 *Prix actuels:*",
                    f"• {signal.symbol1}: `{signal.price1:.5f}`",
                    f"• {signal.symbol2}: `{signal.price2:.5f}`",
                ])
        
        elif is_exit:
            lines.extend([
                "",
                "🚨 *ACTION:* Fermer les 2 positions",
                "",
                f"• Fermer {signal.symbol1}",
                f"• Fermer {signal.symbol2}",
            ])
            
            if signal.reason:
                lines.append(f"\n📝 *Raison:* {signal.reason}")
        
        lines.extend([
            "",
            "━" * 28,
            f"🕐 {signal.timestamp.strftime('%Y-%m-%d %H:%M')} UTC",
        ])
        
        return "\n".join(lines)
    
    def _format_daily_report(self, report: Dict) -> str:
        lines = [
            "📊 *DAILY PAIRS TRADING REPORT*",
            f"*Date:* {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "*Portfolio Status:*",
            f"• Active Pairs: {report.get('active_pairs', 0)}",
            f"• Open Positions: {report.get('open_positions', 0)}",
            f"• Long Spread: {report.get('long_spread', 0)}",
            f"• Short Spread: {report.get('short_spread', 0)}",
            "",
            "*Today's Signals:*",
            f"• Total: {report.get('signals_today', 0)}",
            f"• Entries: {report.get('entries_today', 0)}",
            f"• Exits: {report.get('exits_today', 0)}",
        ]
        
        if report.get('top_zscore_pairs'):
            lines.extend(["", "*Top Z-Score Pairs:*"])
            for pair in report['top_zscore_pairs'][:5]:
                lines.append(f"• {pair['pair_id']}: {pair['zscore']:.2f}")
        
        return "\n".join(lines)


class DiscordNotifier:
    """Envoi de notifications via Discord Webhook."""
    
    def __init__(self, webhook_url: str):
        if not DISCORD_AVAILABLE:
            raise ImportError("discord-webhook requis: pip install discord-webhook")
        
        self.webhook_url = webhook_url
        self.cooldown = AlertCooldown(cooldown_minutes=config.signal.alert_cooldown_minutes)
    
    def send_signal(self, signal: Signal) -> bool:
        """Envoie un signal via Discord."""
        if not self.cooldown.can_send(signal.pair_id):
            return False
        
        embed = self._create_signal_embed(signal)
        webhook = DiscordWebhook(url=self.webhook_url)
        webhook.add_embed(embed)
        
        try:
            response = webhook.execute()
            self.cooldown.mark_sent(signal.pair_id)
            logger.info(f"Discord alert sent: {signal.signal_type.value}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Discord error: {e}")
            return False
    
    def send_daily_report(self, report: Dict) -> bool:
        """Envoie le rapport quotidien."""
        embed = self._create_report_embed(report)
        webhook = DiscordWebhook(url=self.webhook_url)
        webhook.add_embed(embed)
        
        try:
            response = webhook.execute()
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Discord error: {e}")
            return False
    
    def send_message(self, text: str) -> bool:
        """Envoie un message simple."""
        webhook = DiscordWebhook(url=self.webhook_url, content=text)
        try:
            response = webhook.execute()
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Discord error: {e}")
            return False
    
    def _create_signal_embed(self, signal: Signal) -> DiscordEmbed:
        color_map = {
            SignalType.OPEN_LONG_SPREAD: "00ff00",
            SignalType.OPEN_SHORT_SPREAD: "ff0000",
            SignalType.CLOSE_LONG_SPREAD: "0099ff",
            SignalType.CLOSE_SHORT_SPREAD: "0099ff",
            SignalType.STOP_LOSS: "ff6600",
            SignalType.BREAKDOWN_EXIT: "ffcc00",
        }
        color = color_map.get(signal.signal_type, "808080")
        
        embed = DiscordEmbed(
            title=f"🔔 {signal.signal_type.value.upper()}",
            description=f"**{signal.symbol1} / {signal.symbol2}**",
            color=color
        )
        
        embed.add_embed_field(name="Z-Score", value=f"{signal.zscore:.2f}", inline=True)
        embed.add_embed_field(name="Hedge Ratio", value=f"{signal.hedge_ratio:.4f}", inline=True)
        
        if signal.price1 and signal.price2:
            embed.add_embed_field(name="Prices", value=f"{signal.price1:.4f} / {signal.price2:.4f}", inline=True)
        
        if signal.reason:
            embed.add_embed_field(name="Reason", value=signal.reason, inline=False)
        
        embed.set_footer(text=signal.timestamp.strftime('%Y-%m-%d %H:%M UTC'))
        
        return embed
    
    def _create_report_embed(self, report: Dict) -> DiscordEmbed:
        embed = DiscordEmbed(
            title="📊 Daily Pairs Trading Report",
            description=f"Date: {datetime.now().strftime('%Y-%m-%d')}",
            color="0099ff"
        )
        
        embed.add_embed_field(name="Active Pairs", value=str(report.get('active_pairs', 0)), inline=True)
        embed.add_embed_field(name="Open Positions", value=str(report.get('open_positions', 0)), inline=True)
        embed.add_embed_field(name="Signals Today", value=str(report.get('signals_today', 0)), inline=True)
        
        return embed


class NtfyNotifier:
    """Envoi de notifications via Ntfy (léger, idéal pour mobile)."""
    
    def __init__(self, topic: str, server: str = "https://ntfy.sh"):
        self.topic = topic
        self.server = server.rstrip("/")
        self.url = f"{self.server}/{self.topic}"
        self.cooldown = AlertCooldown(cooldown_minutes=config.signal.alert_cooldown_minutes)
    
    def send_signal(self, signal: Signal) -> bool:
        """Envoie un signal via Ntfy."""
        if not self.cooldown.can_send(signal.pair_id):
            return False
        
        message = self._format_signal(signal)
        title = self._get_title(signal)
        tags = self._get_tags(signal)
        priority = self._get_priority(signal)
        
        try:
            response = requests.post(
                self.url,
                data=message.encode('utf-8'),
                headers={
                    "Title": title,
                    "Tags": tags,
                    "Priority": priority,
                }
            )
            if response.status_code == 200:
                self.cooldown.mark_sent(signal.pair_id)
                logger.info(f"Ntfy alert sent: {signal.signal_type.value}")
                return True
            else:
                logger.error(f"Ntfy error: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Ntfy error: {e}")
            return False
    
    def send_message(self, text: str, title: str = "Pairs Trading", tags: str = "chart_with_upwards_trend", priority: str = "default") -> bool:
        """Envoie un message simple."""
        try:
            response = requests.post(
                self.url,
                data=text.encode('utf-8'),
                headers={
                    "Title": title,
                    "Tags": tags,
                    "Priority": priority,
                }
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ntfy error: {e}")
            return False
    
    def send_daily_report(self, report: Dict) -> bool:
        """Envoie le rapport quotidien."""
        message = self._format_daily_report(report)
        return self.send_message(message, title="📊 Daily Report", tags="bar_chart")
    
    def _get_title(self, signal: Signal) -> str:
        titles = {
            SignalType.OPEN_LONG_SPREAD: f"🟢 LONG {signal.symbol1}/{signal.symbol2}",
            SignalType.OPEN_SHORT_SPREAD: f"🔴 SHORT {signal.symbol1}/{signal.symbol2}",
            SignalType.CLOSE_LONG_SPREAD: f"✅ EXIT {signal.symbol1}/{signal.symbol2}",
            SignalType.CLOSE_SHORT_SPREAD: f"✅ EXIT {signal.symbol1}/{signal.symbol2}",
            SignalType.WARNING: f"⚠️ WARNING {signal.symbol1}/{signal.symbol2}",
            SignalType.STOP_LOSS: f"🛑 STOP {signal.symbol1}/{signal.symbol2}",
            SignalType.TIME_EXIT: f"⏰ TIME EXIT {signal.symbol1}/{signal.symbol2}",
            SignalType.BREAKDOWN_EXIT: f"⚠️ BREAKDOWN {signal.symbol1}/{signal.symbol2}",
            SignalType.SCALE_IN_LONG: f"📈 SCALE {signal.symbol1}/{signal.symbol2}",
            SignalType.SCALE_IN_SHORT: f"📉 SCALE {signal.symbol1}/{signal.symbol2}",
        }
        return titles.get(signal.signal_type, f"📊 {signal.pair_id}")
    
    def _get_tags(self, signal: Signal) -> str:
        tags_map = {
            SignalType.OPEN_LONG_SPREAD: "green_circle,chart_with_upwards_trend",
            SignalType.OPEN_SHORT_SPREAD: "red_circle,chart_with_downwards_trend",
            SignalType.WARNING: "warning,eyes",
            SignalType.STOP_LOSS: "rotating_light,warning",
            SignalType.BREAKDOWN_EXIT: "warning,x",
        }
        return tags_map.get(signal.signal_type, "bell")
    
    def _get_priority(self, signal: Signal) -> str:
        if signal.signal_type == SignalType.STOP_LOSS:
            return "urgent"
        elif signal.signal_type == SignalType.WARNING:
            return "high"
        elif signal.signal_type in [SignalType.OPEN_LONG_SPREAD, SignalType.OPEN_SHORT_SPREAD]:
            return "high"
        elif signal.signal_type == SignalType.BREAKDOWN_EXIT:
            return "high"
        return "default"
    
    def _format_signal(self, signal: Signal) -> str:
        """Format compact pour mobile avec position sizing complet."""
        is_entry = signal.signal_type in [
            SignalType.OPEN_LONG_SPREAD, SignalType.OPEN_SHORT_SPREAD,
            SignalType.SCALE_IN_LONG, SignalType.SCALE_IN_SHORT
        ]
        is_warning = signal.signal_type == SignalType.WARNING
        
        lines = [f"Z-Score: {signal.zscore:+.2f}"]
        
        if is_entry:
            # Utiliser TradingConfig pour le calcul
            price1 = signal.price1 or 0
            price2 = signal.price2 or 0
            
            # Calculer position sizing si on a les prix
            if price1 > 0 and price2 > 0:
                pos = config.trading.calculate_position_for_pair(
                    signal.symbol1,
                    signal.symbol2,
                    signal.hedge_ratio,
                    spread_std=0.01,  # Approximation
                    price1=price1,
                    price2=price2
                )
                lots1 = pos["lots1"]
                lots2 = pos["lots2"]
                margin1 = pos["margin1"]
                margin2 = pos["margin2"]
                total_margin = pos["total_margin"]
                risk_amount = pos["risk_amount"]
            else:
                # Fallback simple basé sur hedge ratio
                lots1 = 1.0
                lots2 = round(abs(signal.hedge_ratio), 2)
                if lots2 < 0.01:
                    lots2 = 1.0
                    lots1 = round(1.0 / abs(signal.hedge_ratio), 2) if signal.hedge_ratio != 0 else 1.0
                risk_amount = config.trading.account_size * config.trading.risk_per_trade
                margin1 = margin2 = total_margin = 0
            
            if signal.signal_type in [SignalType.OPEN_LONG_SPREAD, SignalType.SCALE_IN_LONG]:
                action1, action2 = "BUY", "SELL"
            else:
                action1, action2 = "SELL", "BUY"
            
            lines.extend([
                "",
                f"═══ POSITION 1 ═══",
                f"{action1} {signal.symbol1}",
                f"Quantité: {lots1:.2f} lots",
            ])
            if price1 > 0:
                lines.append(f"Prix: ~{price1:.5g}")
            if margin1 > 0:
                lines.append(f"Marge: ~{margin1:,.0f} USD")
            
            lines.extend([
                "",
                f"═══ POSITION 2 ═══",
                f"{action2} {signal.symbol2}",
                f"Quantité: {lots2:.2f} lots",
            ])
            if price2 > 0:
                lines.append(f"Prix: ~{price2:.5g}")
            if margin2 > 0:
                lines.append(f"Marge: ~{margin2:,.0f} USD")
            
            lines.extend([
                "",
                f"═══ RÉSUMÉ ═══",
                f"💰 Capital: {config.trading.account_size:,.0f}",
                f"⚠️ Risque: {config.trading.risk_per_trade*100:.1f}% ({risk_amount:,.0f})",
            ])
            if total_margin > 0:
                lines.append(f"📊 Marge totale: ~{total_margin:,.0f}")
            
            lines.extend([
                "",
                f"═══ SORTIES ═══",
                f"TP: z → ±{config.signal.zscore_exit}",
                f"⚠️: z → ±{config.signal.zscore_warning}",
                f"SL: z → ±{config.signal.zscore_stop}",
                f"Max: {int(signal.half_life * 2)}j",
            ])
        
        elif is_warning:
            # Format WARNING
            direction = "diverge" if abs(signal.zscore) > 2.0 else "approche stop"
            lines.extend([
                "",
                f"⚠️ Le spread {direction}!",
                f"Entry était à z=±2.0",
                f"Stop sera à z=±{config.signal.zscore_stop}",
                "",
                "👀 Surveiller de près",
                "Préparer sortie manuelle si nécessaire",
            ])
        
        else:
            # Format EXIT / STOP
            lines.extend([
                "",
                "🚨 ACTION REQUISE",
                "FERMER les 2 positions",
            ])
            if signal.reason:
                lines.append(f"Raison: {signal.reason}")
        
        return "\n".join(filter(None, lines))
    
    def _format_daily_report(self, report: Dict) -> str:
        return (
            f"Paires actives: {report.get('active_pairs', 0)}\n"
            f"Positions: {report.get('open_positions', 0)}\n"
            f"Signaux 24h: {report.get('signals_today', 0)}"
        )


class AlertManager:
    """Gestionnaire centralisé des alertes."""
    
    def __init__(self):
        self.telegram: Optional[TelegramNotifier] = None
        self.discord: Optional[DiscordNotifier] = None
        self.ntfy: Optional[NtfyNotifier] = None
        
        # Initialize Telegram
        if config.alert.telegram_enabled and config.alert.telegram_bot_token:
            try:
                self.telegram = TelegramNotifier(
                    config.alert.telegram_bot_token,
                    config.alert.telegram_chat_id
                )
                logger.info("Telegram notifier initialized")
            except Exception as e:
                logger.error(f"Telegram init error: {e}")
        
        # Initialize Discord
        if config.alert.discord_enabled and config.alert.discord_webhook_url:
            try:
                self.discord = DiscordNotifier(config.alert.discord_webhook_url)
                logger.info("Discord notifier initialized")
            except Exception as e:
                logger.error(f"Discord init error: {e}")
        
        # Initialize Ntfy
        if config.alert.ntfy_enabled and config.alert.ntfy_topic:
            try:
                self.ntfy = NtfyNotifier(
                    config.alert.ntfy_topic,
                    config.alert.ntfy_server
                )
                logger.info(f"Ntfy notifier initialized (topic: {config.alert.ntfy_topic})")
            except Exception as e:
                logger.error(f"Ntfy init error: {e}")
    
    async def send_signal(self, signal: Signal):
        """Envoie un signal via tous les canaux configurés."""
        results = []
        
        if self.telegram:
            result = await self.telegram.send_signal(signal)
            results.append(("telegram", result))
        
        if self.discord:
            result = self.discord.send_signal(signal)
            results.append(("discord", result))
        
        if self.ntfy:
            result = self.ntfy.send_signal(signal)
            results.append(("ntfy", result))
        
        return results
    
    async def send_daily_report(self, report: Dict):
        """Envoie le rapport quotidien via tous les canaux."""
        results = []
        
        if self.telegram:
            result = await self.telegram.send_daily_report(report)
            results.append(("telegram", result))
        
        if self.discord:
            result = self.discord.send_daily_report(report)
            results.append(("discord", result))
        
        if self.ntfy:
            result = self.ntfy.send_daily_report(report)
            results.append(("ntfy", result))
        
        return results
    
    async def send_message(self, text: str):
        """Envoie un message simple via tous les canaux."""
        results = []
        
        if self.telegram:
            result = await self.telegram.send_message(text)
            results.append(("telegram", result))
        
        if self.discord:
            result = self.discord.send_message(text)
            results.append(("discord", result))
        
        if self.ntfy:
            result = self.ntfy.send_message(text)
            results.append(("ntfy", result))
        
        return results


# Fonction helper synchrone
def send_signal_sync(signal: Signal, manager: Optional[AlertManager] = None):
    """Envoie un signal de manière synchrone."""
    if manager is None:
        manager = AlertManager()
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(manager.send_signal(signal))


if __name__ == "__main__":
    import sys
    logger.remove()
    logger.add(sys.stdout, level="INFO")
    
    # Test signal
    from signals import Signal, SignalType
    
    test_signal = Signal(
        signal_type=SignalType.OPEN_LONG_SPREAD,
        pair_id="SPY_QQQ",
        symbol1="SPY",
        symbol2="QQQ",
        zscore=-2.15,
        hedge_ratio=0.85,
        timestamp=datetime.now(),
        price1=450.25,
        price2=380.50,
        reason="Z-score -2.15 <= -2.0"
    )
    
    print("=== Telegram Format ===")
    if TELEGRAM_AVAILABLE:
        notifier = TelegramNotifier.__new__(TelegramNotifier)
        notifier.cooldown = AlertCooldown()
        print(notifier._format_signal(test_signal))
    else:
        print(test_signal.format_message())
    
    print("\n=== Test Report ===")
    report = {
        "active_pairs": 15,
        "open_positions": 5,
        "long_spread": 3,
        "short_spread": 2,
        "signals_today": 8,
        "entries_today": 3,
        "exits_today": 5,
        "top_zscore_pairs": [
            {"pair_id": "XOM_CVX", "zscore": 2.45},
            {"pair_id": "GLD_SLV", "zscore": -2.12},
        ]
    }
    
    if TELEGRAM_AVAILABLE:
        print(notifier._format_daily_report(report))
