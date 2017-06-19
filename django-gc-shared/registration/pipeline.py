# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from django.utils.translation import get_language
from social.pipeline.partial import partial


def set_lost_otp(backend, user, response, *args, **kwargs):
    if get_language() == 'ru':
        profile = user.profile
        profile.lost_otp = True
        profile.save()


@partial
def get_additional_data(strategy, details, user=None, is_new=False, *args, **kwargs):
    user = strategy.session.get('partial_pipeline', {}).get('user')
    if not is_new:
        return
    if user:
        return {
            'user': user,
            'is_new': True
        }

    return redirect('/?continue_registration=true')