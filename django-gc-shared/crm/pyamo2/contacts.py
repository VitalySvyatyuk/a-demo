# -*- coding: utf-8 -*-


class PyamoContactsMixin(object):
    def contacts_precache(self, ids=None, since=None, **kwargs):
        """Accepts list of ids"""
        return self._objects_precache("contacts", ids, since, **kwargs)

    def contacts_get(self, ids=None, since=None, responsible_user_id=None, **kwargs):
        """Returns dict(id => object_dict)"""
        return self._objects_get("contacts", ids, since, responsible_user_id=responsible_user_id, **kwargs)

    def contact_get(self, id, refresh=False, **kwargs):
        """Returns object_dict"""
        return self._object_get("contacts", id, refresh, **kwargs)

    def contacts_set(self, objects_list, **kwargs):
        """Returns dict(request_id -> object_id)"""
        return self._objects_set("contacts", objects_list, **kwargs)
