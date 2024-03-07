from celery import shared_task


@shared_task(bind=True)
def send_email(self, message):
    print('hello from celery!')
    return
