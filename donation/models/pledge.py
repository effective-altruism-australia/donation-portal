from __future__ import unicode_literals

import random
import string

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from enumfields import Enum, EnumIntegerField

from .partner_charity import PartnerCharity


class PaymentMethod(Enum):
    BANK = 1
    CHEQUE = 2
    CREDIT_CARD = 3
    PAYPAL = 4


class RecurringFrequency(Enum):
    WEEKLY = 1
    FORTNIGHTLY = 2
    MONTHLY = 3


class ReferralSource(models.Model):
    slug_id = models.CharField(max_length=30, unique=True, null=True)
    reason = models.CharField(max_length=256, help_text="Instead of editing this text, you probably want to "
                                                        "disable this ReferralSource and create a new one. If you edit "
                                                        "this, you'll also update the referral sources for donations "
                                                        "already made.",
                              unique=True)
    enabled = models.BooleanField(default=True)
    order = models.BigIntegerField(blank=True, null=True,
                                   help_text='Enter an integer. Reasons will be ordered from smallest to largest.')

    def __str__(self):
        return '{}{}'.format('(DISABLED) ' if not self.enabled else '', self.reason)


class Pledge(models.Model):
    completed_time = models.DateTimeField()
    ip = models.GenericIPAddressField(null=True)
    reference = models.TextField(blank=True)
    first_name = models.CharField(max_length=100, blank=True, verbose_name='name')
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    subscribe_to_updates = models.BooleanField(default=False, verbose_name='Send me news and updates')
    payment_method = EnumIntegerField(PaymentMethod)
    recurring = models.BooleanField(default=False)
    recurring_frequency = EnumIntegerField(RecurringFrequency, blank=True, null=True)
    publish_donation = models.BooleanField(default=False)  # TODO remove?
    how_did_you_hear_about_us_db = models.ForeignKey(ReferralSource, blank=True, null=True, on_delete=models.PROTECT,
                                                     verbose_name='How did you hear about us?')

    is_gift = models.BooleanField(default=False)
    gift_recipient_name = models.CharField(max_length=100, blank=True, null=True)
    gift_recipient_email = models.EmailField(blank=True, null=True)
    gift_personal_message = models.TextField(blank=True, null=True)
    gift_message_sent = models.BooleanField(default=False)

    # TODO rename these historical_drupal_share_...
    share_with_givewell = models.BooleanField(default=False)
    share_with_gwwc = models.BooleanField(default=False)
    share_with_tlycs = models.BooleanField(default=False)

    # Historical fields from imported data
    drupal_uid = models.IntegerField(default=0, editable=False)
    drupal_username = models.TextField(blank=True, editable=False)
    drupal_preferred_donation_method = models.TextField(blank=True, editable=False)

    @property
    def amount(self):
        return self.components.aggregate(total=models.Sum('amount'))['total']

    @property
    def partner_charity_str(self):
        num_components = self.components.count()
        if num_components == 1:
            return self.components.get().partner_charity.name
        elif num_components > 1:
            partner_names = [component.partner_charity.name for component in self.components.all()]
            return '{} and {}'.format(', '.join(partner_names[:-1]), partner_names[-1])
        else:
            raise Exception('Pledge does not have any associated components')

    def generate_reference(self):
        if self.reference:  # for safety, don't overwrite
            return self.reference
        # TODO
        self.reference = ''.join(random.choice('ABCDEF' + string.digits) for _ in range(12))
        self.save()
        return self.reference

    def save(self, *args, **kwargs):
        if not self.completed_time:
            self.completed_time = timezone.now()
        super(Pledge, self).save(*args, **kwargs)

    def __unicode__(self):
        components = ', '.join([c.__unicode__() for c in self.components.all()])
        return "Pledge of {1} by {0.first_name} {0.last_name}, " \
               "made on {2}. Reference {0.reference}".format(self, components, self.completed_time.date())


class PledgeComponent(models.Model):
    """Tracks the breakdown of a pledge between partner charities"""

    class Meta:
        unique_together = ('pledge', 'partner_charity')

    pledge = models.ForeignKey(Pledge, related_name='components')
    partner_charity = models.ForeignKey(PartnerCharity, related_name='pledge_components')
    amount = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0.01)])

    @property
    def proportion(self):
        return self.amount / self.pledge.amount

    def __unicode__(self):
        return "${0.amount} to {0.partner_charity}".format(self)
