import os
import time
import requests
import socket
import subprocess
from celery import shared_task
from django.utils import timezone
from .models import Socks5Proxy, ServerEndpoint, OpenRouterKey
from .utils import send_telegram_alert

@shared_task
def check_all_socks5():
    proxies = Socks5Proxy.objects.filter(is_active=True)
    for p in proxies:
        check_single_socks5.delay(p.id)

@shared_task
def check_single_socks5(proxy_id):
    try:
        p = Socks5Proxy.objects.get(id=proxy_id)
    except Socks5Proxy.DoesNotExist:
        return

    proxy_url = f"socks5://{p.username}:{p.password}@{p.host}:{p.port}" if p.username else f"socks5://{p.host}:{p.port}"
    proxies = {"http": proxy_url, "https": proxy_url}
    
    is_up = False
    start_time = time.time()
    try:
        resp = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=10)
        if resp.status_code == 200:
            is_up = True
    except Exception:
        pass
    end_time = time.time()
    
    if is_up:
        p.response_time_ms = int((end_time - start_time) * 1000)
    else:
        p.response_time_ms = None
    
    if p.is_online and not is_up:
        send_telegram_alert(f"🚨 <b>SOCKS5 {p.name}</b> упал!")
    elif not p.is_online and is_up:
        send_telegram_alert(f"✅ <b>SOCKS5 {p.name}</b> снова работает!")

    p.is_online = is_up
    p.last_checked = timezone.now()
    p.save(update_fields=['is_online', 'last_checked', 'response_time_ms'])

@shared_task
def check_all_endpoints():
    endpoints = ServerEndpoint.objects.filter(is_active=True)
    for e in endpoints:
        check_single_endpoint.delay(e.id)

@shared_task
def check_single_endpoint(endpoint_id):
    try:
        e = ServerEndpoint.objects.get(id=endpoint_id)
    except ServerEndpoint.DoesNotExist:
        return

    is_up = False
    start_time = time.time()
    
    e.response_time_ms = None

    if e.check_type == 'ping':
        result = subprocess.run(['ping', '-c', '1', '-W', '3', e.ip_or_url], stdout=subprocess.PIPE, text=True)
        if result.returncode == 0:
            is_up = True
            import re
            m = re.search(r'time=([\d\.]+)\s*ms', result.stdout)
            if m:
                e.response_time_ms = int(float(m.group(1)))
            else:
                e.response_time_ms = int((time.time() - start_time) * 1000)
    elif e.check_type == 'tcp':
        try:
            with socket.create_connection((e.ip_or_url, e.port), timeout=5):
                is_up = True
                e.response_time_ms = int((time.time() - start_time) * 1000)
        except Exception:
            is_up = False
    elif e.check_type == 'http':
        try:
            url = e.ip_or_url if e.ip_or_url.startswith('http') else f"http://{e.ip_or_url}"
            resp = requests.get(url, timeout=5)
            is_up = (resp.status_code < 500)
            if is_up:
                e.response_time_ms = int(resp.elapsed.total_seconds() * 1000)
        except Exception:
            is_up = False

    if e.is_online and not is_up:
        send_telegram_alert(f"🚨 <b>Сервер {e.name}</b> ({e.ip_or_url}) упал!")
    elif not e.is_online and is_up:
        send_telegram_alert(f"✅ <b>Сервер {e.name}</b> работает!")

    e.is_online = is_up
    e.last_checked = timezone.now()
    e.save(update_fields=['is_online', 'last_checked', 'response_time_ms'])

@shared_task
def check_openrouter():
    keys = OpenRouterKey.objects.filter(is_active=True)
    for k in keys:
        try:
            headers = {"Authorization": f"Bearer {k.api_key}"}
            resp = requests.get("https://openrouter.ai/api/v1/credits", headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json().get('data', {})
                total_credits = data.get('total_credits', 0.0)
                total_usage = data.get('total_usage', 0.0)
                
                balance = float(total_credits) - float(total_usage)
                
                if balance < k.balance_threshold and not k.is_alerted:
                    send_telegram_alert(f"⚠️ <b>OpenRouter {k.name}</b>: Баланс заканчивается! Осталось {balance:.2f}$ (Порог: {k.balance_threshold}$)")
                    k.is_alerted = True
                elif balance >= k.balance_threshold and k.is_alerted:
                    send_telegram_alert(f"✅ <b>OpenRouter {k.name}</b>: Баланс пополнен! Обновлено: {balance:.2f}$")
                    k.is_alerted = False

                k.current_balance = balance
                k.last_checked = timezone.now()
                k.save(update_fields=['current_balance', 'is_alerted', 'last_checked'])
            else:
                k.last_checked = timezone.now()
                k.save(update_fields=['last_checked'])
        except Exception as exc:
            print(f"Failed to check OpenRouter key {k.name}: {exc}")

@shared_task
def update_dashboard():
    from .utils import update_telegram_dashboard
    update_telegram_dashboard()
