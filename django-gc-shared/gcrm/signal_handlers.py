# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from annoying.decorators import signals
from profiles.models import UserProfile
from gcrm.models import Contact


@signals.post_save(sender=UserProfile)
def sync_manager_back(sender, instance, created, **kwargs):
    # sync to userprofile is provided by serialiser by calling set_manager,
    #  which updates profile manager too
    if created or instance.changes.get('manager'):
        Contact.objects.filter(user=instance.user).set_manager(instance.manager, update_profile=False, comment="by profile change")
