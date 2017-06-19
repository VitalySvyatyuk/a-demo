# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

from datetime import datetime, timedelta

from annoying.decorators import signals
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from friend_recommend.models import Recommendation
from log.models import Logger, Event
from profiles.models import UserProfile, UserDocument

import logging
log = logging.getLogger(__name__)


@signals.post_save(sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@signals.post_save(sender=User)
def log_user_changes(sender, instance, created, **kwargs):
    changes = {field.name: unicode(getattr(instance, field.name))
               for field in instance._meta.fields}
    Event.USER_SAVED.log(instance, changes, user=instance)


@signals.post_save(sender=UserProfile)
def log_profile_changes(sender, instance, created, **kwargs):
    changes = {field.name: unicode(getattr(instance, field.name))
               for field in instance._meta.fields}
    Event.PROFILE_SAVED.log(instance, changes)

    if instance.changes.get('manager'):
        old = instance.changes.get('manager')[0]
        Event.MANAGER_CHANGED.log(instance.user, {
            "old_id": old.id if old else None,
            "old_str": unicode(old),
            "new_id": instance.manager.id if instance.manager else None,
            "new_str": unicode(instance.manager),
        })


@signals.post_save(sender=Logger)
def log_user_activity(sender, instance, created, **kwargs):
    if instance.user and instance.user.is_authenticated():
        # write activity in en since we will translate it anyway
        from django.utils.translation import override
        with override('en'):
            instance.user.profile.add_last_activity(unicode(instance.get_event_display()), 'first')


@signals.pre_save(sender=UserProfile)
def detect_recommendation(sender, instance, **kwargs):
    # if we got new profile, we should try to find agent_code by recommendations
    if instance.pk is None:
        try:
            # if recomendation with certain real_ib account exists then assign agent code
            recommendation = Recommendation.objects.filter(
                creation_ts__gte=datetime.now() - timedelta(30),
                email=instance.user.email,
                ib_account__isnull=False
            ).latest('creation_ts')
            if recommendation.ib_account:
                instance.agent_code = recommendation.ib_account.mt4_id
        except Recommendation.DoesNotExist:
            # There is no recommendation for this user
            pass


# Because user can simultaniously upload multiple docs
# We need lock object to prevent cretion of unnecessary CheckDocumentIssues
from threading import Lock
from collections import defaultdict
# Dictionary of locks associated with users to make signal handling sequential
user_doc_locks = defaultdict(Lock)

@signals.post_save(sender=UserDocument)
def on_userdocument(sender, instance, created, *args, **kwargs):
    # Crappy circular dependencies...
    from issuetracker.models import issue, CheckDocumentIssue
    log.info("User doc uploaded")
    with user_doc_locks[instance.user.id] as lock:
        try:
            profile = UserProfile.objects.get(user=instance.user)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            log.warn('Profile have not been founded when tried to create document issue')
        else:
            if profile.status != profile.VERIFIED and\
                    not CheckDocumentIssue.objects.filter(author=instance.user, status="open").exists():
                CheckDocumentIssue.objects.create(document=instance, author=instance.user, status="open")
