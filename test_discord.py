from alerts import AlertManager

am = AlertManager()
if am.discord:
    result = am.discord.send_message('🧪 Test cointegration bot')
    print('✅ Discord OK' if result else '❌ Discord failed')
else:
    print('⚠️  Discord non configuré ou désactivé')
