# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division


class CorsMiddleware(object):
    def process_response(self, request, response):
        """
        Add the respective CORS headers
        """
        if request.path.startswith('/api/crm'):
            response['Access-Control-Allow-Methods'] = "GET, POST, PUT, PATCH"
            response['Access-Control-Allow-Credentials'] = "true"
            response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN')
            response['Access-Control-Allow-Headers'] = ", ".join(["Content-Type", "amotok", "accept", "origin", "*"])
            # force code 200 for options requests, which was sent by browser to test CORS
            if response.status_code == 403 and request.META.get('HTTP_ORIGIN'):
                response.status_code = 200
        return response
