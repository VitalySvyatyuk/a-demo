from unittest import skip

from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, RequestFactory
from massmail.admin import MailingListAdmin, MailingListAdminForm
from massmail.models import MailingList
import fudge


class TestMailingListAdmin(TestCase):

    def test_get_readonly_fields_su(self):
        request = RequestFactory().get('test/')
        request.user = User.objects.get(pk=3)
        self.assertEqual(self.admin.get_readonly_fields(request), ())

    def test_get_readonly_fields_non_su(self):
        request = RequestFactory().get('test/')
        request.user = User.objects.get(pk=6)
        self.assertEqual(self.admin.get_readonly_fields(request), ('query',))

    @fudge.patch('massmail.tasks.recount_email_count.delay')
    def test_save_model_obj_pk(self, t):
        t.is_callable().returns(True)
        request = RequestFactory().get('test/')
        request.user = User.objects.get(pk=3)

        self.admin.form = MailingListAdminForm({'subscribers': '1 2'})
        self.admin.form.is_valid()

        self.admin.save_model(request, request.user, self.admin.form, 1)

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata', 'django-shared/geobase/tests/fixtures/test_geobase.json', verbosity=0)
        call_command('loaddata', 'django-gc-shared/profiles/tests/fixtures/test_users.json', verbosity=0)
        cls.admin = MailingListAdmin(model=MailingList, admin_site=AdminSite())
