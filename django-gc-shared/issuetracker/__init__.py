# coding=utf-8
default_app_config = 'issuetracker.apps.IssuetrackerConfig'

from django.db.models.signals import post_save

from issuetracker.notifications import send_issue_notification as notice

# A dictionary of initialized issuetracker classes
registry = {}


def autodiscover():
    """Connect a post_save signal to every issue that needs it"""
    from issuetracker.models import GenericIssue
    global registry

    for cls in GenericIssue.__subclasses__():
        if cls not in registry:
            registry[cls] = cls.notifications
            notice_type = cls.notice_type()
            if notice_type and cls.notifications:
                post_save.connect(notice(notice_type), sender=cls, weak=False)