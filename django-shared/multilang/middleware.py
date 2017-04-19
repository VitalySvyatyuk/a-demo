import re

from django.conf import settings
from django.shortcuts import redirect
from django.utils.translation import activate, get_language_from_request


class LanguageMiddleware(object):
    def process_request(self, request):
        def activate_lang(lang):
            activate(lang)
            request.LANGUAGE_CODE = lang
            request.session['django_language'] = lang

        if request.META.get("HTTP_X_USE_ACCEPT_LANGUAGE") == "true":
            request.session['use_accept_language'] = True

        if request.session.get('use_accept_language'):
            activate(get_language_from_request(request))
            return

        for language in settings.LANGUAGE_SETTINGS:
            if request.get_host() in settings.LANGUAGE_SETTINGS[language]['hosts']:
                if language == "autodetect":
                    for url in settings.LANGUAGE_REDIRECT_EXEMPT_URLS:  # We shouldn't issue redirects for these URLs
                        if re.search(url, request.path):
                            activate_lang(settings.LANGUAGE_CODE)
                            return
                    new_lang = get_language_from_request(request)  # Will always return a supported language
                    return redirect(settings.LANGUAGE_SETTINGS[new_lang]['redirect_to'] + request.get_full_path())
                else:
                    activate_lang(language)
                    return
        activate_lang("ru")