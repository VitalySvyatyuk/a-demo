from django.conf.urls import *
from shared.generic_views import NodeDetailView

from uptrader_cms.models import CompanyNews

from node.views import node

urlpatterns = patterns('uptrader_cms.views',
    url(r"^news/$", "company_news",
       name="company_news_list"),
    url(r'^news/(?P<node_id>\d+)/$',
       node,
       kwargs={'allowed_hidden_classes': [CompanyNews]},
       name='company_news_by_id'),
    url(r'^news/(?P<slug>[^/]+)/$',
       NodeDetailView.as_view(model=CompanyNews,
                              template_name="uptrader_cms/company_news_detail.jade"),
       name='company_news_by_slug'),
    url(r'^legal_documentation/$', 'legal_documentation', name='legal_documentation'),
    url('^economic_calendar/$', 'economic_calendar', name="economic_calendar"),
)
