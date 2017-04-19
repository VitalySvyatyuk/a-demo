# -*- coding: utf-8 -*-

from django.test import TestCase
from geobase.phone_code_widget import split_phone_number
from geobase.models import Country


class TestPhoneCodeWidget(TestCase):

    def test_split_phone_number_nice1(self):
        r = split_phone_number("8(911)189-6204")
        self.assertEqual(r, ("+8", "9111896204", self.RUSSIA))

    def test_split_phone_number_nice2(self):
        r = split_phone_number("886(76)189-6204")
        self.assertEqual(r, ("+8", "86761896204", self.RUSSIA))

    def test_split_phone_number_bad1(self):
        r = split_phone_number("badnumber")
        self.assertEqual(r, self.NONE_NUMBER)

    def test_split_phone_number_bad2(self):
        r = split_phone_number(None)
        self.assertEqual(r, self.NONE_NUMBER)

    def test_split_phone_number_bad3(self):
        r = split_phone_number("23-445-6567")
        self.assertEqual(r, self.NONE_NUMBER)

    @classmethod
    def setUpTestData(cls):
        cls.NONE_NUMBER = (None, None, None)
        cls.RUSSIA = Country(name="Russia", code="RU", phone_code=8, language="Russian")
        cls.RUSSIA.save()
