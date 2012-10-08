from django.db import models
from decimal import Decimal

from core.models.base import BaseNote, BaseTemporalModel, CurrencyField
from core.models.person import Person

__all__ = ['Client', 'ClientNote', 'Project', 'Allocation']


class Client(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(blank=True, default=True)

    class Meta:
        app_label = 'pm'

    def __unicode__(self):
        return self.name  # pragma: no cover


class ClientNote(BaseNote):
    client = models.ForeignKey(Client, editable=False, related_name='notes')

    class Meta:
        app_label = 'pm'


class Project(BaseTemporalModel):
    client = models.ForeignKey(Client, blank=True, null=True)
    name = models.CharField(max_length=255)
    is_billable = models.BooleanField(blank=True, default=False)
    fixed_price = CurrencyField(blank=True, null=True)
    hourly_rate = CurrencyField(blank=True, null=True)
    estimated_hours = models.IntegerField(blank=True, null=True)

    class Meta:
        app_label = 'pm'
        unique_together = (('client', 'name'),)

    def __unicode__(self):
        return self.name  # pragma: no cover

    @property
    def estimated_price(self):
        if self.fixed_price:
            return self.fixed_price
        elif self.hourly_rate and self.estimated_hours:
            return self.hourly_rate * self.estimated_hours
        else:
            return Decimal(0)


class Allocation(BaseTemporalModel):
    project = models.ForeignKey(Project, related_name='allocations')
    person = models.ForeignKey(Person, related_name='allocations')
    weekly_hours = models.DateTimeField(blank=True, null=True)

    class Meta:
        app_label = 'pm'

    def __unicode__(self):
        return u'%s @ %s' % (unicode(self.person),
            unicode(self.project))  # pragma: no cover
