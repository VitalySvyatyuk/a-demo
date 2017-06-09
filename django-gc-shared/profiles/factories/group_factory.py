# -*- coding: utf-8 -*-
import factory
from django.contrib.auth.models import Group


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: '%s' % n)


def make_objects():
    GroupFactory(name='Managers')
    GroupFactory(name='Partnership')
    GroupFactory(name='Regional Managers')
    GroupFactory(name='Analytics')
    GroupFactory(name='Translators')
    GroupFactory(name='Tech support')
    GroupFactory(name='Accounting')
    GroupFactory(name='Client support')
    GroupFactory(name='Marketing')
