# -*- coding: utf-8 -*-
import json
import os
import random
from hashlib import sha1

from annoying.decorators import ajax_request, render_to
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

from geobase.models import Country
from log.models import Logger, Events
from profiles.forms import DocumentForm
from profiles.models import DOCUMENT_TYPES
from project.utils import memoize
from referral.forms import (PartnerCertificateForm, PartnerAPIKeyForm)
from referral.models import (PartnerDomain, PartnerCertificateIssue)
from referral.utils import get_clicks_for_user, get_clicks_for_account
from wkhtmltopdf.models import render_to_pdf


@login_required
def referral_click_count(request):
    if request.is_ajax():
        account_id = request.GET.get('account_id')
        data = json.dumps(get_clicks_for_account(account_id))
        return HttpResponse(data, content_type="application/json")
    else:
        data = get_clicks_for_user(request.user)
        return render(request, 'referral/redirect_count.html', data)


@login_required
@render_to('referral/partner_certificate.html')
def partner_certificate(request):
    form = PartnerCertificateForm(request.POST or None, request=request)
    if form.is_valid():
        instance = form.save()
        messages.success(request,
                         _(u'You have created a request for printed certificate # %i') % instance.pk)
    return {'form': form}


@login_required
def partner_certificate_download(request, filename='partner_certificate.pdf'):
    account = request.user
    partner_name = "%s %s %s" % (account.first_name, account.profile.middle_name, account.last_name)
    tempfile = render_to_pdf('referral/partner_certificate_pdf.html', {'partner_name': partner_name},
                             None, ['-T', '0', '-B', '0', '-L', '0', '-R', '0'])
    content = open(tempfile).read()
    os.remove(tempfile)
    response = HttpResponse(content, content_type="application/pdf")
    if filename:
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response


@login_required
@render_to(template='referral/documents.html')
def partner_documents(request):
    return {'already_requested': PartnerCertificateIssue.objects.filter(author=request.user, status='open').exists()}


@ajax_request
def delete_domain(request):
    domain = request.POST.get("domain")

    try:
        domain_to_delete = PartnerDomain.objects.get(account=request.user, domain=domain)
    except PartnerDomain.DoesNotExist:
        messages.error(request,
                       _(u'Failed to remove the domain.'))
        return redirect('referral_banner_list')

    domain_to_delete.delete()
    messages.success(request,
                     _(u'Domain was successfully deleted.'))
    return redirect('referral_banner_list')


@require_POST
@ajax_request
def add_domain(request):
    account = request.user
    form = PartnerAPIKeyForm(request.POST, current_user=account)
    if form.is_valid():
        current_domain, ib_account = form.cleaned_data['domain'], form.cleaned_data['ib_account']
        random_salt = str(random.SystemRandom().randint(1, 9999999))
        current_domain = current_domain.strip()
        api_key = sha1(random_salt + current_domain.encode('utf-8')).hexdigest()
        pd = PartnerDomain(api_key=api_key, domain=current_domain,
                           account=account, ib_account=ib_account)
        pd.save()

        #create task to review domain on next day
    return redirect('referral_banner_list')

get_regions_data = memoize()(lambda: json.dumps({c.id: [(r.id, unicode(r)) for r in c.regions.all()]
                                                 for c in Country.objects.order_by('name').all()}))


@render_to("referral/verify_partner.html")
def verify_partner(request):

    docs = [DOCUMENT_TYPES.IB_AGREEMENT, DOCUMENT_TYPES.PASSPORT_SCAN]

    form = DocumentForm(request.POST or None, request.FILES or None, documents=docs)
    if form.is_valid():
        document = form.save(commit=False)
        document.user = request.user
        document.save()

        Logger(user=request.user, content_object=document,
               ip=request.META["REMOTE_ADDR"], event=Events.DOCUMENT_UPLOADED).save()

        messages.success(request, _("Successfully uploaded document %s") % document)
        form = DocumentForm()
    from project.templatetags.app_tags import agreement_url
    return {
        "form": form,
        "agreement_link": agreement_url("real_ib_partner")
    }