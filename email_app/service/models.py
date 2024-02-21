from django.utils import timezone
from django.db import models
from django.db.models import CharField, TextField, DateTimeField, ForeignKey, JSONField, DecimalField


class Campaign(models.Model):
    LAUNCHED = 'launched'
    SCHEDULED = 'scheduled'
    CANCELED = 'canceled'
    CAMPAIGN_STATUSES = (
        (LAUNCHED, 'запущена'),
        (SCHEDULED, 'запланирована'),
        (CANCELED, 'отменена')
    )
    created_at = DateTimeField(default=timezone.now, verbose_name='Дата создания')
    start_at = DateTimeField(verbose_name='Время запуска', null=True, blank=True)
    finish_at = DateTimeField(verbose_name='Время завершения', null=True, blank=True)
    text = TextField(max_length=200, verbose_name='Текст сообщения')
    params = JSONField(verbose_name='Параметры выборки', null=True, blank=True)
    status = CharField(max_length=15, choices=CAMPAIGN_STATUSES, default=LAUNCHED, verbose_name='Статус рассылки')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

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
    campaign = ForeignKey(Campaign, verbose_name='Рассылка', on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    customer = ForeignKey(Customer, verbose_name='Клиент', on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    sent_at = DateTimeField(default=timezone.now, verbose_name='Время отправки')
    status = CharField(max_length=15, choices=MESSAGE_STATUSES, default=PROCESSING, verbose_name='Статус отправки')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f'{self.campaign} [{self.customer}]'
