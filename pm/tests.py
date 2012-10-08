from django.test import TestCase
from decimal import Decimal

from .models import *


class ProjectTest(TestCase):

    def test_estimated_price_fixed(self):
        p = Project(name='tst', fixed_price=Decimal('1337.01'))
        self.assertEqual(p.estimated_price, Decimal('1337.01'))

    def test_estimated_price_hourly(self):
        p = Project(name='tst', hourly_rate=Decimal('42.42'),
            estimated_hours=100)
        self.assertEqual(p.estimated_price, Decimal('4242'))

    def test_estimated_price_not_set(self):
        p = Project(name='tst')
        self.assertEqual(p.estimated_price, 0)
