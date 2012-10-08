from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver

from .base import BaseNote

__all__ = ['Person', 'PersonNote']


class Person(models.Model):
    user = models.OneToOneField(User, editable=False)

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return u'%s %s' % (self.user.first_name, self.user.last_name)

    @property
    def is_active(self):
        return self.user.is_active


@receiver(models.signals.post_save, sender=User)
def user_created_cb(sender, instance, created, **kwargs):
    """Create Person related to the newly created User object."""
    if created:
        # FIXME - superuser is created in syncdb and this app uses South
        # migrations, it'll crash; catch the exception here (but make sure
        # the except is not too broad)
        Person.objects.create(user=instance)


class PersonNote(BaseNote):
    person = models.ForeignKey(Person, editable=False, related_name='notes')

    class Meta:
        app_label = 'core'
