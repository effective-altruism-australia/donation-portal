from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from raven.contrib.django.raven_compat.models import client

from donation.models import Pledge
from donation_portal.eaacelery import app


@app.task()
def send_gift_notification(pledge_id):
    try:
        pledge = Pledge.objects.get(id=pledge_id)
        assert pledge.is_gift, 'Expected the pledge to be marked as a gift'
        assert not pledge.gift_message_sent, 'Gift message has already been sent'
        context = {'pledge': pledge,
                   'personal_message': 'A personal message from %s:\n\n%s' %
                                       (pledge.first_name, pledge.gift_personal_message or '')}
        body = render_to_string('gift_message.txt', context)

        message = EmailMultiAlternatives(
            subject='%s has made a donation on your behalf' % pledge.first_name,
            body=body,
            to=[pledge.gift_recipient_email],
            cc=[settings.EAA_INFO_EMAIL],
            from_email=settings.POSTMARK_SENDER,
        )
        message.send()

        pledge.gift_message_sent = True
        pledge.save()
    except Exception as e:
        client.captureException()
