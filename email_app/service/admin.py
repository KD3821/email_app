from django.contrib import admin

from .models import Campaign, Customer, Message


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['id', 'confirmed_at', 'owner', 'start_at', 'finish_at', 'status', 'params']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['phone', 'owner', 'carrier', 'tag', 'tz_name']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['owner', 'campaign', 'customer', 'sent_at', 'status', 'uuid']
