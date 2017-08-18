from massmail.models import OpenedCampaign
from massmail.views import _get_massmail_params


class MassMailMiddleware(object):
    def process_response(self, request, response):
        """If an html link was clicked from an email, count it"""

        # Process only html content
        # We also have massmail GET parameters for static content

        if isinstance(response, Exception) or 'text/html' not in response.get('content-type', ''):
            return response

        campaign, email = _get_massmail_params(request)
        if not (campaign and email):
            return response

        obj, created = OpenedCampaign.objects.get_or_create(
            campaign=campaign,
            email=email.lower(),
            defaults={'clicked': True,
                      'opened': True})

        # If campaign was opened but wasn't clicked, we don't
        # create new OpenedCampaign with same campaign and email,
        # instead of this we change clicked and opened to True
        if not (obj.clicked and obj.opened):
            obj.clicked = True
            obj.opened = True
            obj.save()

        return response
