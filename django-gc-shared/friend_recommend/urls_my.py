from django.conf.urls import *

urlpatterns = patterns('friend_recommend.views',
    url(r'^recommend/$', 'recommend', name='friend_recommend')
)