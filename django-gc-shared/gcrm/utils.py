# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from django.db import models


def user_can_manage(user, manager, self=True):
    if manager is None and not (user.is_superuser or user.crm_manager.is_head_supermanager):
        return False
    return (self and user == manager) \
        or user.is_superuser \
        or user.crm_manager.is_head_supermanager \
        or (manager and user.crm_manager.is_office_supermanager and user.crm_manager.office == manager.crm_manager.office)


def can_user_set_agent_codes(user):
    return user.is_superuser or user.crm_manager.can_set_agent_codes

from project.utils import StatefullModel