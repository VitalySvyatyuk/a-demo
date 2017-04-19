# -*- coding: utf-8 -*-

from django.core.management import BaseCommand
from datetime import datetime
import time

from crm.pyamo2 import get_pyamo_api
from crm.models import AmoContact, AmoTask, AmoNote
from django.utils import translation
from django.conf import settings

# disable dirty logs in django.log
import logging
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)


class Command(BaseCommand):
    def execute(self, *args, **options):
        # protect from devs!
        if settings.DEBUG:
            return

        translation.activate('ru')
        amo = get_pyamo_api()

        for i in xrange(30):
            for sync_op in [sync_contacts, sync_tasks, sync_notes]:
                sync_forced(amo)
                sync_op(amo)
            time.sleep(1)


def sync_forced(amo):
    # check for available new assignment requests
    # TODO
    pass


def sync_contacts(amo):
    # sync new ones first
    objects = AmoContact.objects.unsynced()

    new_object = objects.filter(synced_at=None).first()
    if new_object:
        sync_new_object(amo, "contacts", new_object)
        # since we spent too much time  - 2s per contact(get&set)
        return

    uploaded_objects = objects.exclude(synced_at=None).order_by('-sync_at')[:100]
    if uploaded_objects:
        sync_objects(amo, "contacts", uploaded_objects)


def sync_tasks(amo):
    objects = AmoTask.objects.unsynced().order_by('synced_at')[:200]
    if objects:
        sync_objects(amo, "tasks", objects)


def sync_notes(amo):
    objects = AmoNote.objects.unsynced().order_by('synced_at')[:200]
    if objects:
        sync_objects(amo, "notes", objects)


def sync_new_object(amo, slug, obj):
    data = [obj.get_amo_json(amo)]
    time.sleep(1)  # get_amo_json get current data from amo
    if not data:
        return
    result = amo._objects_set(slug, data)
    if result:
        obj.oid = result.values()[0]
        obj.synced_at = datetime.now()
        obj.sync_at = None
        obj.save()
        obj.post_sync(True, amo)
    time.sleep(1)


def sync_objects(amo, slug, qs):
    data = []
    objects_ids = []

    # collect possible data
    amo._objects_precache(slug, [obj.oid for obj in qs if obj.oid])
    time.sleep(1)
    for obj in qs:
        obj_data = obj.get_amo_json(amo)
        if obj_data:
            data.append(obj_data)
            objects_ids.append(obj.id)
    amo.clear_cache()

    # upload new data
    amo._objects_set(slug, data)
    qs.model.objects.filter(
        id__in=objects_ids
    ).update(
        sync_at=None, synced_at=datetime.now()
    )
    time.sleep(1)
