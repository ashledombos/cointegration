from alerts import AlertManager

am = AlertManager()
if am.ntfy:
    result = am.ntfy.send_message('🧪 Test depuis Python')
    print('✅ Ntfy OK' if result else '❌ Ntfy failed')
else:
    print('⚠️  Ntfy non configuré')
