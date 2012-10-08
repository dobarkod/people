from django.test import TestCase
import datetime
from decimal import Decimal

from .models import *


class TimeEntryTest(TestCase):

    def setUp(self):
        self.now = datetime.datetime.now()

    def test_hours_notstarted(self):
        t = TimeEntry()
        self.assertEqual(t.hours, Decimal(0))

    def test_hours(self):
        t = TimeEntry(start=self.now,
            end=self.now + datetime.timedelta(seconds=12600))
        self.assertEqual(t.hours, Decimal('3.5'))
