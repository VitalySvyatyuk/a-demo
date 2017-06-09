# -*- coding: utf-8 -*-


class PyamoNotesMixin(object):
    def contact_notes_precache(self, ids=None, since=None, **kwargs):
        """Accepts list of ids"""
        return self._objects_precache("notes", ids, since, type="contact", **kwargs)

    def contact_notes_get(self, ids=None, since=None, **kwargs):
        """Returns dict(id => object_dict)"""
        return self._objects_get("notes", ids, since, type="contact", **kwargs)

    def contact_note_get(self, id, refresh=False, **kwargs):
        """"Returns object_dict"""
        return self._object_get("notes", id, refresh, type="contact", **kwargs)

    def contact_notes_set(self, objects_list, **kwargs):
        """Returns dict(request_id -> object_id)"""
        return self._objects_set("notes", objects_list, **kwargs)
