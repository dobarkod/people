from django.db import models
from django.contrib.auth.models import User
import datetime

__all__ = ['BaseNote', 'BaseTemporalManager', 'BaseTemporalModel']


class BaseNote(models.Model):
    """Base class for notes with optional attachment."""

    author = models.ForeignKey(User, editable=False)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    text = models.TextField()
    attachment = models.FileField(upload_to='attachments',
        blank=True, null=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.text


class BaseTemporalManager(models.Manager):
    """Manager for BaseTemporalModel."""

    use_for_related_fields = True

    def filter_active(self, when=None):
        if when is None:
            when = datetime.datetime.now()

        return self.get_query_set() \
            .filter(models.Q(start__isnull=True) | models.Q(start__lte=when)) \
            .filter(models.Q(end__isnull=True) | models.Q(end__gte=when))

    def filter_archived(self, when=None):
        if when is None:
            when = datetime.datetime.now()
        return self.get_query_set().filter(end__lt=when)

    def filter_future(self, when=None):
        if when is None:
            when = datetime.datetime.now()
        return self.get_query_set().filter(start__gt=when)


class BaseTemporalModel(models.Model):
    """Base class for objects having 'start' and 'end' datetime."""

    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    objects = BaseTemporalManager()

    class Meta:
        abstract = True

    def is_active_at(self, when=None):
        if when is None:
            when = datetime.datetime.now()

        return ((not self.start or self.start <= when) and
            (not self.end or self.end >= when))

    @property
    def is_active(self):
        return self.is_active_at(None)

    @property
    def is_future(self):
        return self.start and self.start > datetime.datetime.now()

    @property
    def is_archived(self):
        return self.end and self.end < datetime.datetime.now()

    def days_range(self, frm=None, to=None, filter=None):
        # return days which are both within [frm,to] and [start,end] ranges,
        # while allowing any param to be None (unbounded); if both frm and
        # start are None, no days are returned; if both to and end are None,
        # current time is used as the end time
        # days are optionally filtered by the filter function (should return
        # True for days which should be included)

        if frm:
            if self.start:
                frm = max(frm, self.start)
        else:
            if self.start:
                frm = self.start
            else:
                return []  # startless unbounded - return [] for sanity

        if to:
            if self.end:
                to = min(to, self.end)
        else:
            if self.end:
                to = self.end
            else:
                return []  # endless unbounded - return [] for sanity

        retval = []
        while frm < to:
            if filter is None or filter(frm.date()):
                retval.append(frm.date())
            frm += datetime.timedelta(days=1)
        return retval

    @property
    def days(self):
        return len(self.days_range())
