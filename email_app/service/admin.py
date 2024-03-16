from django.contrib import admin

from .models import Campaign, Customer, Message, Invoice


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['id', 'confirmed_at', 'paid_at', 'owner', 'start_at', 'finish_at', 'status', 'params']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['phone', 'owner', 'carrier', 'tag', 'tz_name']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['owner', 'campaign', 'customer', 'sent_at', 'status', 'uuid']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'amount', 'paid_at', 'invoice_number', 'status', 'payment_intent_id',
                    'checkout_session_id']
