"""
Alerts Module - Notifications Telegram et Discord
===================================================
"""

import asyncio
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
        
        lines = [
            f"{emoji} *PAIRS TRADING SIGNAL*",
            f"",
            f"*Type:* `{signal.signal_type.value}`",
            f"*Pair:* {signal.symbol1} / {signal.symbol2}",
            f"*Z-Score:* {signal.zscore:.2f}",
            f"*Hedge Ratio:* {signal.hedge_ratio:.4f}",
        ]
        
        if signal.price1 and signal.price2:
            lines.append(f"*Prices:* {signal.price1:.4f} / {signal.price2:.4f}")
        
        if signal.scale_level > 0:
            lines.append(f"*Scale Level:* {signal.scale_level}")
        
        if signal.reason:
            lines.append(f"*Reason:* {signal.reason}")
        
        lines.append(f"*Time:* {signal.timestamp.strftime('%Y-%m-%d %H:%M UTC')}")
        
        # Actions
        if signal.signal_type in [SignalType.OPEN_LONG_SPREAD, SignalType.SCALE_IN_LONG]:
            lines.extend([
                "",
                "📌 *Action:*",
                f"• LONG {signal.symbol1}",
                f"• SHORT {signal.symbol2} × {signal.hedge_ratio:.3f}"
            ])
        elif signal.signal_type in [SignalType.OPEN_SHORT_SPREAD, SignalType.SCALE_IN_SHORT]:
            lines.extend([
                "",
                "📌 *Action:*",
                f"• SHORT {signal.symbol1}",
                f"• LONG {signal.symbol2} × {signal.hedge_ratio:.3f}"
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


class AlertManager:
    """Gestionnaire centralisé des alertes."""
    
    def __init__(self):
        self.telegram: Optional[TelegramNotifier] = None
        self.discord: Optional[DiscordNotifier] = None
        
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
    
    async def send_signal(self, signal: Signal):
        """Envoie un signal via tous les canaux configurés."""
        results = []
        
        if self.telegram:
            result = await self.telegram.send_signal(signal)
            results.append(("telegram", result))
        
        if self.discord:
            result = self.discord.send_signal(signal)
            results.append(("discord", result))
        
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
