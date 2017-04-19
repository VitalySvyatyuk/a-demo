# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def get_full_name(u):
    name_parts = filter(lambda x: x, [
        u.last_name,
        u.first_name,
        u.profile.middle_name,
    ])
    if name_parts:
        return ' '.join(name_parts)
    return u.username


def set_name(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Contact = apps.get_model("gcrm", "Contact")
    for c in Contact.objects.exclude(user=None):
        c.name = get_full_name(c.user)
        c.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gcrm', '0024_contact_name_sync_from_user'),
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(set_name)
    ]
