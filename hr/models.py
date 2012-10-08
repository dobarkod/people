from django.db import models

from core.models.base import BaseNote, BaseTemporalModel, CurrencyField
from core.models.person import Person

__all__ = ['Contract', 'ContractNote', 'Absence', 'AbsenceNote']


class Contract(BaseTemporalModel):
    TYPES = (
        ('employee', 'Employee'),
        ('contractor', 'Contractor'),
        ('student', 'Student'),
    )

    person = models.ForeignKey(Person, editable=False,
        related_name='contracts')
    type = models.CharField(max_length=32, choices=TYPES, blank=True,
        default='employee')
    title = models.CharField(max_length=255, blank=True, default='')
    description = models.TextField(blank=True, default='')

    weekly_hours = models.DecimalField(max_digits=3, decimal_places=1,
        blank=True, null=True)
    hourly_rate = CurrencyField(blank=True, null=True)
    monthly_salary = CurrencyField(blank=True, null=True)

    class Meta:
        app_label = 'hr'

    def __unicode__(self):
        return unicode(self.person)  # pragma: no cover


class ContractNote(BaseNote):
    contract = models.ForeignKey(Contract, editable=False,
        related_name='contracts')

    class Meta:
        app_label = 'hr'


class Absence(BaseTemporalModel):
    TYPES = (
        ('vacation', 'Vacation'),
        ('sickday', 'Sick days'),
        ('other', 'Other')
    )
    STATES = (
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    )

    person = models.ForeignKey(Person, editable=False, related_name='absences')
    type = models.CharField(max_length=32, choices=TYPES, blank=True,
        default='vacation')
    title = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        app_label = 'hr'

    def __unicode__(self):
        return u'%s (%s)' % (self.title,
            self.get_type_display())  # pragma: no cover


class AbsenceNote(BaseNote):
    absence = models.ForeignKey(Absence, editable=False, related_name='notes')

    class Meta:
        app_label = 'hr'
