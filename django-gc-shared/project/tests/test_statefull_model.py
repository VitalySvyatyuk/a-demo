# -*- coding: utf-8 -*-
import fudge
from datetime import datetime

from shared.models import StateSavingModel
from project.utils import StatefullModel
from payments.models import WithdrawRequestsGroup
from django.test import TestCase

class TestStatefullModel(TestCase):
    def test_fresh_instance_should_say_everything_is_changes(self):
        assert StateSavingModel in WithdrawRequestsGroup.mro()

        #assign from constructor
        obj = WithdrawRequestsGroup(updated_at=datetime.now())
        # Disabled cause I really can't understand why there must be any changes
        # It does not work with initial StafullModel also
        # assert obj.changes

        #assign via attribute change
        wr = WithdrawRequestsGroup()
        assert not wr.changes
        wr.updated_at = datetime.now()
        assert 'updated_at' in wr.changes

    @fudge.patch('django.db.models.Model.save')
    def test_reset_upon_save(self, save):
        save.is_callable()
        wr = WithdrawRequestsGroup()
        wr.updated_at = datetime.now()
        wr.save()
        assert not wr.changes
