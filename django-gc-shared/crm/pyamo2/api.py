# -*- coding: utf-8 -*-

import requests
import json

from common import PyamoResponse
from contacts import PyamoContactsMixin
from leads import PyamoLeadsMixin
from tasks import PyamoTasksMixin
from notes import PyamoNotesMixin
from account import PyamoAccountMixin
from access import PyamoAccessMixin


class AuthException(Exception):
    pass


class PyamoAPI(PyamoContactsMixin, PyamoLeadsMixin, PyamoTasksMixin, PyamoAccountMixin, PyamoNotesMixin, PyamoAccessMixin):
    def __init__(self, base_url, login, token, debug=False):
        self.debug = debug
        self.base_url = base_url

        #setup
        self._counter = 0  # requests counter
        self._queries = []
        self._cache = {}
        self._req_session = requests.Session()
        self._auth(login, token)

    def perform_post(self, url, **kwargs):
        if 'json_data' in kwargs:
            kwargs['data'] = json.dumps(kwargs.pop('json_data'))
        elif 'form_data' in kwargs:
            kwargs['data'] = kwargs.pop('form_data')

        if self.debug:
            self._queries.append("POST %s %s" % (self.base_url+url, kwargs))
        r = self._req_session.post(self.base_url+url, **kwargs)
        return self._process_response(r)

    def perform_get(self, url, **kwargs):
        if 'json_data' in kwargs:
            kwargs['data'] = json.dumps(kwargs.pop('json_data'))

        if self.debug:
            s = "GET %s %s" % (self.base_url+url, kwargs)
            print s
            self._queries.append(s)
        r = self._req_session.get(self.base_url+url, **kwargs)
        return self._process_response(r)

    def _process_response(self, req):
        self._counter += 1

        #DEBUG:
        if self.debug:
            print 'REQUEST >>>>>'
            print req.request.headers
            print 'BODY >>>>>'
            print req.request.body
            print '<<<<< REQUEST'
            print 'RESPONSE >>>>>'
            print req.status_code
            print req.text
            print '<<<<< RESPONSE'

        #check for bad response
        if req.status_code not in [200, 204] or "502 Bad Gateway" in req.text:
            raise Exception(u"Pyamo error response: {}".format(req.text))
        #output is json now
        try:
            return req.json().get('response', req.json()) if req.text else None
        except ValueError:
            raise Exception(u'Cannot parse response: {}'.format(req.text))

    def clear_cache(self):
        self._cache.clear()

    def _auth(self, login, token):
        result = self.perform_post('/private/api/auth.php?type=json', data={
            "USER_LOGIN": login,
            "USER_HASH": token
        })
        if not result['auth']:
            raise AuthException()

    ###########################################################################
    ################ Objects common methods ###################################
    ###########################################################################

    def _objects_get(self, object_name, ids=None, since=None, **kwargs):
        """
        "Returns dict(id => object_dict)"
        Returns dict(objects => [object_dict, ... ]).
        Posible arguments:
        query, responsible_user_id, limit_rows, limit_offset, ids
        """
        headers = dict()
        if ids:
            assert isinstance(ids, (tuple, list)) and len(ids) <= 500
            kwargs.update({'id': ids})
        if since:
            headers['if-modified-since'] = since.strftime("%a, %d %b %Y %H:%M:%S")
        resp = self.perform_get(
            "/private/api/v2/json/%s/list" % (object_name,),
            headers=headers,
            params=kwargs)
        if resp and len(resp[object_name]):
            result = PyamoResponse([(int(d['id']), d) for d in resp[object_name]])
            result.time = resp.get('server_time')
            return result

    def _objects_precache(self, object_name, ids=None, since=None, cache_name=None, **kwargs):
        if not ids:
            return []
        res = self._objects_get(object_name, ids, since, **kwargs)
        self._cache[cache_name or object_name] = res or dict()
        return self._cache[cache_name or object_name]

    def _object_get(self, object_name, id, refresh=False, cache_name=None, **kwargs):
        "Returns object_dict"
        #try to find cached version
        if not refresh and id in self._cache.get(object_name, {}):
            result = PyamoResponse(self._cache[object_name][id])
            result.time = self._cache[object_name].time
            return result

        #retrieve fresh version
        kwargs.update({'id': id})
        resp = self.perform_get("/private/api/v2/json/%s/list" % (object_name,), params=kwargs)
        if resp and len(resp[object_name]):
            result = PyamoResponse(resp[object_name][0])
            result.time = resp.get('server_time')
            return result

    def _objects_set(self, object_name, objects_list, **kwargs):
        "Returns dict(request_id -> object_id)"
        data = {'add': [], 'update': []}

        #new objects should be in 'add', updated in 'update'
        for cj in objects_list:
            data['update' if cj.get('id') else 'add'].append(cj)

        resp = self.perform_post("/private/api/v2/json/%s/set" % (object_name,), json_data={
            "request": {object_name: data}
        })
        assert resp is not None

        result = PyamoResponse()
        result.time = resp.get('server_time')

        #in the case of update, it returns null
        if resp[object_name] and 'add' in resp[object_name]:
            for info in resp[object_name]['add']:
                result[info['request_id']] = info['id']
        return result
