from django.conf.urls import *

urlpatterns = patterns('treemenus.views',
    url(r'^reorder/$', 'reorder', name='treemenus_reorder'),

# We don't need that
#    url(r'^map/(?P<menu_name>\w+)/$', 'menumap',
#        name='menu_map'),
)