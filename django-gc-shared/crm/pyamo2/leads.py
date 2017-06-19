# -*- coding: utf-8 -*-


class PyamoLeadsMixin(object):
    def leads_precache(self, ids=None, since=None, **kwargs):
        """"Accepts list of ids"""
        return self._objects_precache("leads", ids, since, **kwargs)

    def leads_get(self, ids=None, since=None, **kwargs):
        """"Returns dict(id => object_dict)"""
        return self._objects_get("leads", ids, since, **kwargs)

    def lead_get(self, id, refresh=False, **kwargs):
        """"Returns object_dict"""
        return self._object_get("leads", id, refresh, **kwargs)

    def leads_set(self, objects_list, **kwargs):
        """Returns dict(request_id -> object_id)"""
        return self._objects_set("leads", objects_list, **kwargs)
