import os
from decimal import Decimal

from dotenv import load_dotenv
import stripe

from .models import Invoice


load_dotenv()

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')

endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

campaign_price_id = os.getenv('STRIPE_CAMPAIGN_PRICE_ID')


def create_checkout_session(campaign_id, invoice_number):
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                'price': campaign_price_id,
                'quantity': 1,
            }],
            mode='payment',
            metadata={'invoice_number': invoice_number},
            success_url=f'http://127.0.0.1:8080/checkout/{campaign_id}/success',
            cancel_url=f'http://127.0.0.1:8080/checkout/{campaign_id}/failure'
        )
        return checkout_session.id

    except Exception as e:
        return str(e)


def create_invoice(campaign):
    old_invoices = Invoice.objects.filter(campaign=campaign, status=Invoice.OPEN)
    for invoice in old_invoices:
        invoice.status = Invoice.VOID
        invoice.save()
    new_invoice = Invoice.objects.create(
        campaign=campaign,
        amount=Decimal('10.00')
    )
    return new_invoice


def pay_invoice(invoice_number, payment_intent_id, paid_at):
    invoice = Invoice.objects.get(invoice_number=invoice_number)
    invoice.status = Invoice.PAID
    invoice.payment_intent_id = payment_intent_id
    invoice.paid_at = paid_at
    invoice.save()
