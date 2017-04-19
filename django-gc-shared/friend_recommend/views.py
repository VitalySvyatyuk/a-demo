# coding: utf-8

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib import messages

from friend_recommend.forms import RecommendationForm

from annoying.decorators import render_to
from django.utils.translation import ugettext_lazy as _


@login_required
@render_to('friend_recommend/recommend_form.html')
def recommend(request):
    has_ib_account = request.user.accounts.real_ib().count()
    form = RecommendationForm(request.POST or None, request=request, has_ib_account=has_ib_account)

    context = {'form': form, 'has_ib_account': has_ib_account}
    if request.is_ajax():
        context['TEMPLATE'] = 'friend_recommend/_recommend_form_ajax.html'

    if form.is_valid():
        instance = form.save()
        thanks_msg = _('Thank you for recommending us!')

        if request.is_ajax():
            return HttpResponse(thanks_msg)

        # Non-ajax way
        messages.info(request, thanks_msg)
        return HttpResponseRedirect('/')

    return context
