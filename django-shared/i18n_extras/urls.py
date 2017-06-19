from django.conf.urls import *

urlpatterns = patterns('',
    (r'^setlang/$', 'i18n_extras.views.set_language'),
)