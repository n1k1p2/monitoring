from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats
from .models import GlobalSettings, Socks5Proxy, ServerEndpoint, OpenRouterKey

class JSONOnlyFormatBase(base_formats.JSON):
    pass

class Socks5ProxyResource(resources.ModelResource):
    class Meta:
        model = Socks5Proxy

class ServerEndpointResource(resources.ModelResource):
    class Meta:
        model = ServerEndpoint

class OpenRouterKeyResource(resources.ModelResource):
    class Meta:
        model = OpenRouterKey

@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    pass

@admin.register(Socks5Proxy)
class Socks5ProxyAdmin(ImportExportModelAdmin):
    resource_classes = [Socks5ProxyResource]
    formats = [base_formats.JSON]
    list_display = ('name', 'host', 'port', 'is_active', 'is_online', 'last_checked', 'response_time_ms')
    list_filter = ('is_active', 'is_online')

@admin.register(ServerEndpoint)
class ServerEndpointAdmin(ImportExportModelAdmin):
    resource_classes = [ServerEndpointResource]
    formats = [base_formats.JSON]
    list_display = ('name', 'ip_or_url', 'check_type', 'is_active', 'is_online', 'last_checked', 'response_time_ms')
    list_filter = ('check_type', 'is_active', 'is_online')

@admin.register(OpenRouterKey)
class OpenRouterKeyAdmin(ImportExportModelAdmin):
    resource_classes = [OpenRouterKeyResource]
    formats = [base_formats.JSON]
    list_display = ('name', 'current_balance', 'balance_threshold', 'is_active', 'is_alerted', 'last_checked')
    list_filter = ('is_active', 'is_alerted')
