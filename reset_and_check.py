import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from monitor.models import Socks5Proxy, ServerEndpoint, OpenRouterKey
from monitor.tasks import check_single_socks5, check_single_endpoint, check_openrouter

print("Сбрасываем статусы в базе данных, чтобы принудительно вызвать уведомления...")

Socks5Proxy.objects.update(is_online=False, last_checked=None)
ServerEndpoint.objects.update(is_online=False, last_checked=None)
OpenRouterKey.objects.update(is_alerted=False, last_checked=None)

print("Запускаем проверки прямо сейчас (в обход ожидания расписания)...")

for p in Socks5Proxy.objects.filter(is_active=True):
    print(f"  Проверка SOCKS5: {p.name}")
    check_single_socks5(p.id)

for e in ServerEndpoint.objects.filter(is_active=True):
    print(f"  Проверка сайта/сервера: {e.name}")
    check_single_endpoint(e.id)

print("  Проверка OpenRouter...")
check_openrouter()

from monitor.utils import update_telegram_dashboard
update_telegram_dashboard()

print("Готово. Единый дашборд отправлен в Телеграм!")
