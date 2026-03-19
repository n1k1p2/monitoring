import requests
import json
from django.utils import timezone
from .models import GlobalSettings

def send_telegram_alert(message):
    settings = GlobalSettings.load()
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return
        
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception:
        pass

def update_telegram_dashboard():
    settings = GlobalSettings.load()
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return

    from .models import Socks5Proxy, ServerEndpoint, OpenRouterKey
    
    lines = ["📊 <b>System Monitoring Dashboard</b>\n"]
    
    socks = Socks5Proxy.objects.filter(is_active=True)
    if socks.exists():
        lines.append("🌐 <b>SOCKS5 Proxies:</b>")
        for s in socks:
            if s.is_online:
                ping_txt = f" ({s.response_time_ms}ms)" if s.response_time_ms else ""
                status = f"✅ UP{ping_txt}"
            else:
                status = "🚨 DOWN"
            lines.append(f"{status} - {s.name}")
        lines.append("")

    endpoints = ServerEndpoint.objects.filter(is_active=True)
    if endpoints.exists():
        lines.append("🖥 <b>Servers & Sites:</b>")
        for e in endpoints:
            if e.is_online:
                ping_txt = f" ({e.response_time_ms}ms)" if e.response_time_ms else ""
                status = f"✅ UP{ping_txt}"
            else:
                status = "🚨 DOWN"
            lines.append(f"{status} - {e.name}")
        lines.append("")

    keys = OpenRouterKey.objects.filter(is_active=True)
    if keys.exists():
        lines.append("🔑 <b>OpenRouter Balances:</b>")
        for k in keys:
            if k.current_balance is not None:
                if k.current_balance < k.balance_threshold:
                    status = f"⚠️ LOW ({k.current_balance:.2f}$)"
                else:
                    status = f"✅ OK ({k.current_balance:.2f}$)"
                lines.append(f"{status} - {k.name}")
            else:
                lines.append(f"⏳ Pending - {k.name}")
        lines.append("")

    from zoneinfo import ZoneInfo
    now = timezone.now()
    msk_time = now.astimezone(ZoneInfo("Europe/Moscow")).strftime('%H:%M:%S')
    bali_time = now.astimezone(ZoneInfo("Asia/Makassar")).strftime('%H:%M:%S')
    
    lines.append(f"⏱ <i>Обновлено: {msk_time} (МСК) | {bali_time} (Бали)</i>")
    text = "\n".join(lines)
    
    bot_token = settings.telegram_bot_token
    chat_id = settings.telegram_chat_id
    
    if settings.status_message_id:
        url = f"https://api.telegram.org/bot{bot_token}/editMessageText"
        payload = {"chat_id": chat_id, "message_id": settings.status_message_id, "text": text, "parse_mode": "HTML"}
        resp = requests.post(url, json=payload).json()
        if not resp.get("ok"):
            settings.status_message_id = None
            settings.save(update_fields=['status_message_id'])
            
    if not settings.status_message_id:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        resp = requests.post(url, json=payload).json()
        if resp.get("ok"):
            settings.status_message_id = resp["result"]["message_id"]
            settings.save(update_fields=['status_message_id'])
