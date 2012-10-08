from django.test import TestCase
from django.db import models
from django.contrib.auth.models import User
import datetime

from .models.base import *
from .models.person import *


class TestModel(BaseTemporalModel):
    amount = CurrencyField(blank=True, null=True)


class TestModelNote(BaseNote):
    testmodel = models.ForeignKey(TestModel, related_name='notes')


class BaseTemporalTest(TestCase):

    def setUp(self):
        self.now = datetime.datetime.now()
        self.yesterday = self.now - datetime.timedelta(days=1)
        self.tomorrow = self.now + datetime.timedelta(days=1)

    def tearDown(self):
        TestModel.objects.all().delete()

    def test_is_active(self):
        m = TestModel(start=self.yesterday, end=self.tomorrow)

        self.assertTrue(m.is_active_at(self.now))
        self.assertTrue(m.is_active_at(None))
        self.assertTrue(m.is_active)

        self.assertFalse(m.is_active_at(
            self.yesterday - datetime.timedelta(seconds=1)))
        self.assertFalse(m.is_active_at(
            self.tomorrow + datetime.timedelta(seconds=1)))

    def test_is_future(self):
        m = TestModel(start=self.tomorrow, end=self.tomorrow)
        self.assertTrue(m.is_future)

    def test_is_archived(self):
        m = TestModel(start=self.yesterday, end=self.yesterday)
        self.assertTrue(m.is_archived)

    def test_endless_active(self):
        m = TestModel(start=self.now)
        self.assertTrue(m.is_active_at(datetime.datetime(3001, 1, 1)))

    def test_startless_active(self):
        m = TestModel(end=self.now)
        self.assertTrue(m.is_active_at(datetime.datetime(1970, 1, 1)))

    def test_days_range(self):
        m = TestModel(start=self.yesterday, end=self.tomorrow)
        self.assertEqual(m.days_range(),
            [self.yesterday.date(), self.now.date()])

    def test_days(self):
        m = TestModel(start=self.yesterday, end=self.tomorrow)
        self.assertEqual(m.days, 2)

    def test_days_range_filtered(self):
        m = TestModel(start=self.yesterday, end=self.tomorrow)

        self.assertEqual(m.days_range(frm=self.now),
            [self.now.date()])
        self.assertEqual(m.days_range(to=self.now),
            [self.yesterday.date()])
        self.assertEqual(m.days_range(frm=self.now, to=self.now), [])
        self.assertEqual(m.days_range(frm=self.tomorrow, to=self.yesterday),
            [])

    def test_endless_days_range_sanity(self):
        m = TestModel()
        m2 = TestModel(start=self.yesterday)

        self.assertEqual(m.days, 0)
        self.assertEqual(m.days_range(), [])
        self.assertEqual(m2.days_range(), [])

    def test_unbounded_days_range_filtered(self):
        startless = TestModel(end=self.now)
        endless = TestModel(start=self.now)
        always = TestModel()

        self.assertEqual(startless.days_range(frm=self.yesterday),
            [self.yesterday.date()])
        self.assertEqual(endless.days_range(to=self.tomorrow),
            [self.now.date()])
        self.assertEqual(
            always.days_range(frm=self.yesterday, to=self.tomorrow),
            [self.yesterday.date(), self.now.date()])

    def test_filter_active_endless(self):
        m = TestModel.objects.create()
        self.assertEqual(m, TestModel.objects.filter_active().get())

    def test_filter_active(self):
        m = TestModel.objects.create(start=self.yesterday, end=self.tomorrow)

        self.assertEqual(m,
            TestModel.objects.filter_active(when=self.now).get())
        self.assertEqual(m,
            TestModel.objects.filter_active(when=self.yesterday).get())
        self.assertEqual(m,
            TestModel.objects.filter_active(when=self.tomorrow).get())

        self.assertFalse(TestModel.objects.filter_active(
                when=self.tomorrow + datetime.timedelta(seconds=1)).exists())
        self.assertFalse(TestModel.objects.filter_active(
                when=self.yesterday - datetime.timedelta(seconds=1)).exists())

    def test_filter_archived(self):
        m = TestModel.objects.create(end=self.yesterday)

        self.assertEqual(m,
            TestModel.objects.filter_archived().get())
        self.assertFalse(
            TestModel.objects.filter_archived(when=self.yesterday).exists())

    def test_filter_future(self):
        m = TestModel.objects.create(start=self.tomorrow)

        self.assertEqual(m,
            TestModel.objects.filter_future().get())
        self.assertFalse(
            TestModel.objects.filter_archived(when=self.tomorrow).exists())


class BaseNoteTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='foo', password='bar')
        self.model = TestModel.objects.create()

    def tearDown(self):
        User.objects.all().delete()
        TestModel.objects.all().delete()
        TestModelNote.objects.all().delete()

    def test_note_creation(self):
        n = self.model.notes.create(text='Test Note', author=self.user)
        self.assertEqual(self.model.notes.get(), n)
        self.assertEqual(unicode(n), 'Test Note')


class PersonTest(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        User.objects.all().delete()
        Person.objects.all().delete()

    def test_auto_creation(self):
        u = User.objects.create_user(username='foo', password='bar')
        u.is_active = True
        u.first_name = 'Foo'
        u.last_name = 'Bar'
        u.save()

        p = u.get_profile()
        self.assertEqual(p.user, u)
        self.assertTrue(p.is_active)
        self.assertEqual(unicode(p), u'Foo Bar')

    def test_auto_deletion(self):
        u = User.objects.create_user(username='foo', password='bar')
        self.assertEqual(Person.objects.count(), 1)

        u.delete()
        self.assertEqual(Person.objects.count(), 0)
