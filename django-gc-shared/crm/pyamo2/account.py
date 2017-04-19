# -*- coding: utf-8 -*-

from common import PyamoResponse


class PyamoAccountMixin(object):
    def account_info(self, refresh=False):
        if not self._account_info or refresh:
            self._account_info = self.perform_get("/private/api/v2/json/accounts/current")
            self._account_info = PyamoResponse(self._account_info.get('account'))
            self._account_info.time = self._account_info.get('server_time')
        return self._account_info
    _account_info = None

    def object_field_id(self, type_name, code):
        assert code
        for cfield in self.account_info().get('custom_fields').get(type_name):
            if cfield.get('code') == code:
                return cfield.get('id')

    def contact_field_id(self, code):
        return int(self.object_field_id('contacts', code))

    def lead_field_id(self, code):
        return int(self.object_field_id('leads', code))
