# coding: utf-8

from django.db import models
from annoying.decorators import signals

from notification import models as notification
from django.utils.translation import ugettext_lazy as _


class Recommendation(models.Model):
    """A recommendation of our service from a user to his friend"""
    user = models.ForeignKey('auth.User')
    name = models.CharField(_("Friend's name"), max_length=255)
    email = models.EmailField(verbose_name=_("Friend's email"))
    creation_ts = models.DateTimeField(auto_now_add=True)
    ib_account = models.ForeignKey('platforms.TradingAccount', blank=True, null=True)

    class Meta:
        verbose_name = u'Рекомендация другу'
        verbose_name_plural = u'Рекомендации друзьям'

        
@signals.post_save(sender=Recommendation)
def on_recommendation(sender, instance, created, **kwargs):
    if created:
        notification.send([instance.email], 'friend_recommendation', {
            'recommendation': instance,
        }, display_subject_prefix=False)