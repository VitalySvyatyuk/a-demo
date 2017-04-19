# coding=utf-8
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import resolve, Resolver404

from urlparse import urlparse


from registration.signals import user_registered


class UtmAnalytics(models.Model):
    user = models.OneToOneField(User, related_name="utm_analytics")
    utm_source = models.CharField(max_length=256, default='')
    utm_medium = models.CharField(max_length=256, default='')
    utm_campaign = models.CharField(max_length=256, default='')
    utm_timestamp = models.DateTimeField(null=True)
    referrer = models.CharField(max_length=2048, default='')
    referrer_timestamp = models.DateTimeField(null=True)
    agent_code_timestamp = models.DateTimeField(null=True)
    registration_page = models.CharField(max_length=4096, default='')


@receiver(user_registered)
def process_registration(sender, user, request, **kwargs):
    if request and ('utm_analytics' in request.session or 'original_referrer' in request.session or
                    'agent_code_timestamp' in request.session or 'registration_page' in request.session):
        ua = UtmAnalytics(user=user)
        if 'utm_analytics' in request.session:
            for key, value in request.session['utm_analytics'].iteritems():
                setattr(ua, key, value)
        if 'original_referrer' in request.session:
            ua.referrer = request.session['original_referrer']
            if 'original_referrer_timestamp' in request.session:
                ua.referrer_timestamp = request.session['original_referrer_timestamp']
        if 'agent_code_timestamp' in request.session:
            ua.agent_code_timestamp = request.session['agent_code_timestamp']

        if 'registration_page' in request.session:
            try:
                ua.registration_page = resolve(urlparse(request.session['registration_page']).path).url_name
            except Resolver404:
                ua.registration_page = request.session['registration_page']

        ua.save()


@receiver(post_migrate)
def create_permissions(sender, **kwargs):
    if sender.label != 'visitor_analytics':
        return
    permission, created = Permission.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(UtmAnalytics),
        codename="can_view_utm_report")

    if created:
        permission.name = "Can view UTM report"
        permission.save()
        print "Adding permission: %s" % permission
