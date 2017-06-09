# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import post_migrate
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Permission

#
User._meta.get_field('username').max_length = 75


@receiver(post_migrate)
def create_permissions(sender, **kwargs):
    if sender.label != 'profiles':
        return

    from models import UserProfile
    
    permission, created = Permission.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(UserProfile),
        codename="can_change_agent_code_manager")

    if created:
        permission.name = "Can change fields agent_code & manager"
        permission.save()
        print "Adding permission: %s" % permission
