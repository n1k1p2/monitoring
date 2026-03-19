from django.db import models

class SingletonModel(models.Model):
    class Meta:
        abstract = True
    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class GlobalSettings(SingletonModel):
    telegram_bot_token = models.CharField(max_length=255, blank=True, null=True, help_text="Token from @BotFather")
    telegram_chat_id = models.CharField(max_length=255, blank=True, null=True, help_text="Chat ID to send alerts to")
    status_message_id = models.IntegerField(null=True, blank=True, help_text="ID of the dashboard message to edit")

    class Meta:
        verbose_name = "Global Setting"
        verbose_name_plural = "Global Settings"

class Socks5Proxy(models.Model):
    name = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)
    last_checked = models.DateTimeField(null=True, blank=True)
    response_time_ms = models.IntegerField(null=True, blank=True, help_text="Last response time in ms")

    class Meta:
        verbose_name = "SOCKS5 Proxy"
        verbose_name_plural = "SOCKS5 Proxies"

    def __str__(self):
        return self.name

class ServerEndpoint(models.Model):
    CHECK_TYPES = [
        ('ping', 'ICMP Ping'),
        ('tcp', 'TCP Port Check'),
        ('http', 'HTTP GET'),
    ]
    name = models.CharField(max_length=255)
    ip_or_url = models.CharField(max_length=255)
    port = models.IntegerField(null=True, blank=True, help_text="For TCP check")
    check_type = models.CharField(max_length=10, choices=CHECK_TYPES, default='ping')
    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)
    last_checked = models.DateTimeField(null=True, blank=True)
    response_time_ms = models.IntegerField(null=True, blank=True, help_text="Last response time in ms")

    def __str__(self):
        return f"{self.name} ({self.ip_or_url})"

class OpenRouterKey(models.Model):
    name = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)
    balance_threshold = models.DecimalField(max_digits=10, decimal_places=4, default=1.0)
    current_balance = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_alerted = models.BooleanField(default=False)
    last_checked = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
