# -*- coding: utf-8 -*-

ACCESS_ENTRY_POINT = '/private/account/access_edit.php'


class UserAccess(object):
    def __init__(self, conn, user_id):
        self.conn = conn
        self.user_id = user_id

    def set_active(self, bool):
        data = {
            'user': self.user_id,
            'right': 'ACTIVE',
            'value': {True: 'Y', False: 'N'}[bool]
        }
        return self.conn.perform_get(ACCESS_ENTRY_POINT, params=data)

    def set(self, field, bool):
        data = {
            'user': self.user_id,
            'right': field,
            'value': {True: 'Y', False: 'N'}[bool]
        }
        return self.conn.perform_get(ACCESS_ENTRY_POINT, params=data)


class PyamoAccessMixin(object):
    def user(self, *a, **kwa):
        return UserAccess(self, *a, **kwa)
