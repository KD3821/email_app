import shortuuid

from django.utils import timezone
from django.db import models
from django.db.models import CharField, TextField, DateTimeField, ForeignKey, JSONField, DecimalField

from accounts.models import User


class Campaign(models.Model):
    LAUNCHED = 'launched'
    SCHEDULED = 'scheduled'
    CANCELED = 'canceled'
    FINISHED = 'finished'
    CAMPAIGN_STATUSES = (
        (LAUNCHED, 'запущена'),
        (SCHEDULED, 'запланирована'),
        (CANCELED, 'отменена'),
        (FINISHED, 'завершена')
    )
    owner = ForeignKey(User, verbose_name='Владелец', on_delete=models.SET_NULL, null=True, blank=True, related_name='campaigns')
    created_at = DateTimeField(default=timezone.now, verbose_name='Дата создания')
    confirmed_at = DateTimeField(verbose_name='Дата подтверждения', null=True, blank=True)
    start_at = DateTimeField(verbose_name='Время запуска', null=True, blank=True)
    finish_at = DateTimeField(verbose_name='Время завершения', null=True, blank=True)
    text = TextField(max_length=200, verbose_name='Текст сообщения')
    params = JSONField(verbose_name='Параметры выборки', null=True, blank=True)
    status = CharField(max_length=15, choices=CAMPAIGN_STATUSES, default=SCHEDULED, verbose_name='Статус рассылки')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

    @property
    def paid_at(self):
        paid_invoice = self.invoices.filter(status=Invoice.PAID).first()
        if paid_invoice:
            return paid_invoice.paid_at
        return None

    def __str__(self):
        return f'{self.pk} - {self.text[:20]}'


class Customer(models.Model):
    MTS = 'mts'
    MEGAFON = 'megafon'
    BEELINE = 'beeline'
    TELE2 = 'tele2'
    YOTA = 'yota'
    CARRIER_NAMES = (
        (MTS, 'мтс'),
        (MEGAFON, 'мегафон'),
        (BEELINE, 'билайн'),
        (TELE2, 'теле2'),
        (YOTA, 'йота')
    )
    owner = ForeignKey(User, verbose_name='Владелец', on_delete=models.SET_NULL, null=True, blank=True, related_name='customers')
    phone = DecimalField(max_digits=11, decimal_places=0, verbose_name='Номер телефона', null=True, blank=True)
    carrier = CharField(max_length=10, choices=CARRIER_NAMES, verbose_name='Код оператора')
    tag = CharField(max_length=20, verbose_name='Тег', null=True, blank=True)
    tz_name = CharField(max_length=20, verbose_name='Часовой пояс')

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return f'ID: {self.pk} [{self.carrier} - {self.tag}]'


class Message(models.Model):
    OK = 'ok'
    FAILED = 'failed'
    PROCESSING = 'processing'
    CANCELED = 'canceled'
    MESSAGE_STATUSES = (
        (OK, 'доставлено'),
        (FAILED, 'не доставлено'),
        (PROCESSING, 'в обработке'),
        (CANCELED, 'отменено')
    )
    owner = ForeignKey(User, verbose_name='Владелец', on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    campaign = ForeignKey(Campaign, verbose_name='Рассылка', on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    customer = ForeignKey(Customer, verbose_name='Клиент', on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    sent_at = DateTimeField(verbose_name='Время отправки', null=True, blank=True)
    status = CharField(max_length=15, choices=MESSAGE_STATUSES, default=PROCESSING, verbose_name='Статус отправки')
    uuid = CharField(max_length=50, verbose_name='UUID', null=True, blank=True)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def assign_uuid(self, *args, **kwargs):
        if self.uuid is None:
            short_uuid = shortuuid.uuid()
            self.uuid = f'MSG-{short_uuid}-{str(self.pk)}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.campaign} [{self.customer}]'


class Invoice(models.Model):
    OPEN = 'open'
    PROCESSING = 'processing'
    PAID = 'paid'
    VOID = 'void'
    INVOICE_STATUSES = (
        (OPEN, 'ожидает оплаты'),
        (PROCESSING, 'в обработке'),
        (PAID, 'оплачен'),
        (VOID, 'отменен')
    )
    campaign = ForeignKey(Campaign, verbose_name='Рассылка', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    amount = DecimalField(max_digits=5, decimal_places=2, verbose_name='Сумма', null=True, blank=True)
    paid_at = DateTimeField(verbose_name='Дата оплаты', null=True, blank=True)
    checkout_session_id = CharField(max_length=80, verbose_name='ID сессии', null=True, blank=True)
    payment_intent_id = CharField(max_length=40, verbose_name='ID платежа', null=True, blank=True)
    invoice_number = CharField(max_length=30, verbose_name='Номер инвойса', null=True, blank=True)
    status = CharField(max_length=10, choices=INVOICE_STATUSES, default=OPEN, verbose_name='Статус оплаты')

    class Meta:
        verbose_name = 'Инвойс'
        verbose_name_plural = 'Инвойсы'

    def assign_invoice_number(self, *args, **kwargs):
        if self.invoice_number is None:
            num = self.pk
            if num < 10:
                number = '000' + str(num)
            elif num < 100:
                number = '00' + str(num)
            elif num < 1000:
                number = '0' + str(num)
            else:
                number = str(num)
            self.invoice_number = f'INVC-{number}/{self.campaign.pk}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'ID:{self.pk} [Рассылка {self.campaign}]'
