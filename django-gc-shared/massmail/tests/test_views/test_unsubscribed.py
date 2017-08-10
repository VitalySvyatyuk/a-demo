# -*- coding: utf-8 -*-
from django.http import Http404, HttpResponse
from django.test import TestCase, RequestFactory

from massmail.models import Unsubscribed
from massmail.views import unsubscribed


class TestUnsubscribed(TestCase):

    def test_uns(self):
        request = RequestFactory().post('test/')
        ch = unsubscribed(request, 'test@email.ru', 1)
        correct = '<title>Private office</title>'
        self.assertTrue(isinstance(ch, HttpResponse) and correct in ch.content)

    def test_uns_404(self):
        with self.assertRaises(Http404):
            unsubscribed(1, 'русские нельзя', 1)

    @classmethod
    def setUpTestData(cls):
        Unsubscribed.objects.create(email='test@email.ru')
