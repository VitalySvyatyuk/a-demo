# -*- coding: utf-8 -*-

from django.dispatch import receiver
from django.db.models.signals import post_migrate
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from crm.models import CustomerRelationship


@receiver(post_migrate)
def create_permissions(sender, **kwargs):
    if sender.label != 'crm':
        return
    
    permission, created = Permission.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(CustomerRelationship),
        codename="crm_viewdealinginfo")

    if created:
        permission.name = "Can view fields only for dealing"
        permission.save()
        print "Adding permission: %s" % permission