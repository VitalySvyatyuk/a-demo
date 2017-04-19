from urlparse import urlparse

from django.conf import settings
from django.utils.translation import check_for_language
from django import http

def set_language(request):
    """
    Redirect to a given url while setting the chosen language in the
    session or cookie. The url and the language code need to be
    specified in the request parameters.

    Since this view changes how the user will see the rest of the site, it must
    only be accessed as a POST request. If called as a GET request, it will
    redirect to the page in the request (the 'next' parameter) without changing
    any state.
    """
    next = request.REQUEST.get('next', None)
    from_referer = False
    if not next:
        next = request.META.get('HTTP_REFERER', None)
        if next: from_referer = True
    if not next:
        next = '/'
    if "://" not in next or from_referer: # User will be redirected back to the domain from where he came
        domain = urlparse(next)[1] if from_referer else request.get_host()
        query = ''.join(urlparse(next)[2:]) if from_referer else next
        for language in settings.LANGUAGE_SETTINGS:
            if domain in settings.LANGUAGE_SETTINGS[language]['hosts']:
                # If the user requests this view from a language-specific domain,
                # redirect to the domain of this language
                next = settings.LANGUAGE_SETTINGS[language]['redirect_to'] + query
    response = http.HttpResponseRedirect(next)
    if request.method == 'POST':
        lang_code = request.POST.get('language', None)
        if lang_code and check_for_language(lang_code):
            if hasattr(request, 'session'):
                request.session['django_language'] = lang_code
            else:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)

        if request.user.is_authenticated():
            profile = request.user.profile
            language = request.session.get('django_language')
            if profile.language != language:
                profile.language = language
                profile.save()
    return response