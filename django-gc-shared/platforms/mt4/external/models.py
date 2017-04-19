# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from models_symbol_config import *
from models_users import *
from models_group_settings import *
from models_order_conf import *
from models_other import *
from models_trade import *


class ChangeIssue(models.Model):
    """
    Client change request.
    """
    # types of changes
    FIELD_CHOISES = (
        ('LEVERAGE', 'Leverage'),
        ('PASSWORD', 'Password'),
        ('AGENTACCOUNT', 'Agent Account'),
        ('BLOCK', 'Block Account'),
    )
    # possible statuses
    STATUS_CHOICES = (
        ('CREATED', 'Created'),
        ('DONE', 'Done'),
    )

    # user login
    login = models.PositiveIntegerField("Account number", null=True, blank=True)
    # change
    field = models.CharField(max_length=30)
    # new value
    value = models.CharField(max_length=30)
    # time of request
    creation_ts = models.DateTimeField("Creation timestamp", default=datetime.now)
    # request status
    status = models.CharField(choices=STATUS_CHOICES, default='CREATED', max_length=60)

    class Meta():
        db_table = "jb_web_task_db"
        app_label = 'external'



