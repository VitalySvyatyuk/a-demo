from massmail.models import OpenedCampaign
from massmail.views import _get_massmail_params

class MassMailMiddleware(object):

    def process_response(self, request, response):
        """If an html link was clicked from an email, count it"""

        # Process only html content
        # We also have massmail GET parameters for static content

        if 'text/html' not in response.get('content-type', ''):
            return response

        campaign, email = _get_massmail_params(request)
        if not (campaign and email):
            return response

        obj, created = OpenedCampaign.objects.get_or_create(
                                     campaign=campaign,
                                     email=email.lower(),
                                     defaults={'clicked': True,
                                               'opened': True})
        if not (obj.clicked and obj.opened):
            obj.clicked = True
            obj.clicked = True
            obj.save()

        return response