import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

try:
    from django_celery_beat.models import PeriodicTask, IntervalSchedule

    # Create intervals
    interval_1m, _ = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.MINUTES)
    interval_5m, _ = IntervalSchedule.objects.get_or_create(every=5, period=IntervalSchedule.MINUTES)
    interval_1h, _ = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.HOURS)

    # Create tasks
    PeriodicTask.objects.get_or_create(
        name='Update Telegram Dashboard (Auto)',
        defaults={'task': 'monitor.tasks.update_dashboard', 'interval': interval_1m}
    )
    PeriodicTask.objects.get_or_create(
        name='Check All SOCKS5 (Auto)',
        defaults={'task': 'monitor.tasks.check_all_socks5', 'interval': interval_5m}
    )
    PeriodicTask.objects.get_or_create(
        name='Check All Endpoints (Auto)',
        defaults={'task': 'monitor.tasks.check_all_endpoints', 'interval': interval_5m}
    )
    PeriodicTask.objects.get_or_create(
        name='Check OpenRouter (Auto)',
        defaults={'task': 'monitor.tasks.check_openrouter', 'interval': interval_1h}
    )

    print("Default periodic tasks successfully created!")
except Exception as e:
    print(f"Error setting up tasks: {e}")
