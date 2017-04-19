# coding=utf-8
from datetime import datetime
from project.utils import is_from_external_source


class UtmMiddleware(object):
    """
    Processes utm
    """

    @staticmethod
    def process_request(request):
        def process_utm():
            utm_source = request.GET.get('utm_source', '')
            if not utm_source:
                return

            request.session['utm_analytics'] = {
                'utm_source': utm_source,
                'utm_medium': request.GET.get('utm_medium', ''),
                'utm_campaign': request.GET.get('utm_campaign', ''),
                'utm_timestamp': datetime.now(),
            }

        def process_referrer():
            if 'original_referrer' not in request.session and is_from_external_source(request):
                referer = request.META.get('HTTP_REFERER', None)
                if referer:
                    request.session['original_referrer'] = referer.lower()
                    request.session['original_referrer_timestamp'] = datetime.now()

        process_utm()
        process_referrer()
