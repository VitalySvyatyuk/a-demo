# -*- coding: utf-8 -*-


class PyamoTasksMixin(object):
    def contact_tasks_precache(self, ids=None, since=None, **kwargs):
        """Accepts list of ids"""
        return self._objects_precache("tasks", ids, since, type="contact", **kwargs)

    def contact_tasks_get(self, ids=None, since=None, **kwargs):
        """"Returns dict(id => object_dict)"""
        return self._objects_get("tasks", ids, since, type="contact", **kwargs)

    def contact_task_get(self, id, refresh=False, **kwargs):
        """Returns object_dict"""
        return self._object_get("tasks", id, refresh, type="contact", **kwargs)

    def contact_tasks_set(self, objects_list, **kwargs):
        """Returns dict(request_id -> object_id)"""
        return self._objects_set("tasks", objects_list, **kwargs)

    def contact_task_delete(self, objects_list, **kwargs):
        """"Returns dict(request_id -> object_id)"""
        return self._objects_set("tasks", objects_list, **kwargs)

    def task_delete(self, id, type=1):  # 1 - contact, 2 - deal
        data = {
            'ACTION': 'TASK_DELETE',
            'ID': id,
            'ELEMENT_TYPE': type,
        }
        resp = self.perform_post("/private/notes/edit2.php", form_data=data)
        assert resp is not None
        return resp['status'] == 'ok'
