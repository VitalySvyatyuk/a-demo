import urllib

from annoying.decorators import render_to
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import escape
from django.utils.translation import ugettext as _

from massmail.models import Campaign, Unsubscribed, OpenedCampaign, CampaignType, MailingList, Subscribed
import massmail.utils
from notification import models as notification
from shared.validators import email_re


def subscribe(request, email, signature, mail_list_id, first_name="", last_name="", phone=""):

    if massmail.utils.get_signature(email) != signature or not email_re.match(email):
        raise Http404

    list_id = mail_list_id.split(u'+')
    for mail_list_id in list_id:
        mail_list_id = int(mail_list_id)
        try:
            ml = MailingList.objects.get(pk=mail_list_id)
        except (ObjectDoesNotExist, ValueError):
            raise Http404

        if not request.user.is_anonymous():
            first_name = request.user.first_name
            last_name = request.user.last_name

        elif not first_name or not last_name:
            try:
                usr = User.objects.get(email=email)
                last_name = usr.last_name
                first_name = usr.first_name
            except ObjectDoesNotExist:
                # we dont know user last and first name here
                first_name = " "
                last_name = " "
        sub = Subscribed(email=email, first_name=first_name, last_name=last_name, phone=phone)
        ml.subscribers.add(sub)
        ml.subscribers_count += 1
        ml.save()

    if not request.user.is_anonymous():
        return redirect('/account/profile/subscriptions')
    else:
        return redirect('subscribed')

@render_to('massmail/unsubscribed.html')
def unsubscribe(request, email, signature, campaign_id=None):
    email = urllib.unquote(email)
    if massmail.utils.get_signature(email) != signature or not email_re.match(email):
        raise Http404

    if campaign_id is None:
        campaign_id = request.GET.get('campaign_id', None)

    # if Unsubscribed.objects.filter(email=email).exists():
    #     # messages.success(request, _('You have already unsubscribed'))
    #     try:
    #         return redirect('massmail_unsubscribed_id', urllib.quote(email), int(campaign_id))
    #     except (ValueError, TypeError):
    #         return redirect('massmail_unsubscribed', urllib.quote(email))
    #
    # if request.method == 'POST':
    #     Unsubscribed.objects.get_or_create(email=email)
    #     try:
    #         campaign_id = request.POST.get('campaign_id', None)
    #         campaign = Campaign.objects.get(id=int(campaign_id))
    #         campaign.unsubscribed += 1
    #         campaign.save()
    #         # messages.success(request, _('Copy of this message has been sent to your email'))
    #         notification.send([email], 'unsubscribed', {"email":urllib.quote(email), "campaign_id": campaign_id})
    #         return redirect('massmail_unsubscribed_id', urllib.quote(email), campaign_id)
    #     except (ValueError, TypeError, Campaign.DoesNotExist):
    #         # messages.success(request, _('Copy of this message has been sent to your email'))
    #         notification.send([email], 'unsubscribed', {"email":urllib.quote(email), "campaign_id": campaign_id})
    #         return redirect('massmail_unsubscribed', urllib.quote(email))
    return {'campaign_id':campaign_id,
            'unsubscribed': Unsubscribed.objects.get_or_create(email=email)[0],
            'email': urllib.quote(email)}

@render_to('massmail/unsubscribed.html')
def unsubscribed(request, email, campaign_id=None):
    email = urllib.unquote(email)
    if email_re.match(email):
        return {'unsubscribed': Unsubscribed.objects.filter(email=email).exists(),
                'email': urllib.quote(email),
                'campaign_id': campaign_id}
    else:
        raise Http404

@login_required
def resubscribe(request, email, campaign_id=None):
    # prevent from resubscribing of other users
    email = urllib.unquote(email)

    if request.user.email == email:
        Unsubscribed.objects.filter(email=email).delete()
        request.user.profile.subscription = CampaignType.objects.all()
        request.user.profile.save()
        try:
            camp = Campaign.objects.get(pk=int(campaign_id))
            if camp.unsubscribed != 0:  # To prevent situations with 0 unsubscribed users conflicts.
                camp.unsubscribed -= 1
                camp.save()
                return redirect('massmail_unsubscribed_id', urllib.quote(email), campaign_id)
        except (ValueError, TypeError, Campaign.DoesNotExist):
            return redirect('massmail_unsubscribed', urllib.quote(email))
    else:
        return redirect('/')

def _get_massmail_params(request):
    """Get campaign and email from request"""
    email = request.GET.get('email')
    if not (email and email_re.match(email)):
        email = None
    signature = request.GET.get('signature')
    if signature != massmail.utils.get_signature(email):
        email = None
    try:
        campaign = request.GET['campaign_id']
        campaign = Campaign.objects.get(pk=int(campaign))
    except (KeyError, Campaign.DoesNotExist, ValueError):
        campaign = None
    return campaign, email


def view_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    is_text = request.GET.get("text", False)

    # Remember that this email has read the campaign
    email = _get_massmail_params(request)[1]
    if campaign and email:
        obj, created = OpenedCampaign.objects.get_or_create(
            campaign=campaign, email=email.lower(), defaults={'opened': True}
        )
        if not obj.opened:
            obj.opened = True
            obj.save()

    context = {
        "email": email,
        "browser_url": request.get_full_path(),
        "browser": True,
    }
    for key, value in request.GET.iteritems():
        context[key] = escape(value)

    return HttpResponse("<pre>%s</pre>" % campaign.render_text(**context) if is_text else campaign.render_html(**context))


def serve_static(request, *args, **kwargs):
    """Get campaign id and email from GET parameters and remember the person

    Then serve the static image.
    """
    campaign, email = _get_massmail_params(request)

    # An ugly hack so that we can mock serve() in unit test
    import sys
    if 'test' in sys.argv:
        import django.views.static
        serve = django.views.static.serve
    else:
        from django.views.static import serve

    # This can raise a Http404 or whatever, so do it first
    response = serve(request, *args, **kwargs)

    # We have a response, so remember the person, who opened the email
    if campaign and email:
        obj, created = OpenedCampaign.objects.get_or_create(
            campaign=campaign,
                                     email=email.lower(),
                                     defaults=
                                         {'opened': True})
        if not obj.opened:
            obj.opened = True
            obj.save()
    return response
