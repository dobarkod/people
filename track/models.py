from django.db import models
import datetime
from decimal import Decimal

from core.models.base import BaseTemporalModel
from core.models.person import Person
from pm.models import Project

__all__ = ['Activity', 'TimeEntry']


class Activity(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_billable = models.BooleanField(blank=True, default=False)
    is_active = models.BooleanField(blank=True, default=True)

    def __unicode__(self):
        return self.name  # pragma: no cover


class TimeEntry(BaseTemporalModel):
    person = models.ForeignKey(Person, editable=False,
        related_name='time_entries')
    project = models.ForeignKey(Project, blank=True, null=True,
        related_name='time_entries')
    activity = models.ForeignKey(Activity, blank=True, null=True,
        related_name='time_entries')
    is_billable = models.BooleanField(blank=True, default=False)
    description = models.CharField(max_length=255, blank=True, null=True)

    # FIXME: do we want additional tagging of time entries? if so, uncomment:
    # tags = TaggableManager()

    def __unicode__(self):
        return '%.1f' % self.hours  # pragma: no cover

    @property
    def hours(self):
        if not self.start:
            return Decimal(0)

        end = self.end if self.end else datetime.datetime.now()
        duration = (end - self.start).total_seconds()
        return Decimal(duration) / Decimal(3600)
