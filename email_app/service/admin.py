from django.contrib import admin

from .models import Campaign, Customer, Message


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['start_at', 'finish_at', 'status', 'params']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['phone', 'carrier', 'tag', 'tz_name']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'customer', 'sent_at', 'status']
