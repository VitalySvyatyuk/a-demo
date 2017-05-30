# coding:utf-8
from rest_framework.routers import SimpleRouter

APIRouter = APIRouterV1 = SimpleRouter()
APIRouterV1.trailing_slash = '/?'  # fix trailing slash in some browsers, make it optional

from platforms.rest_api import TradingAccountViewSet, TradeViewSet
APIRouterV1.register(r'mt4account', TradingAccountViewSet, base_name='account')
APIRouterV1.register(r'mt4account/(?P<account_id>[0-9]+)/mt4trade', TradeViewSet, base_name='trade')

from profiles.rest_api import UserViewSet, UserDocumentViewSet
APIRouterV1.register(r'user', UserViewSet, base_name='user')
APIRouterV1.register(r'user_document', UserDocumentViewSet, base_name='user_document')

from private_messages.rest_api import MessageViewSet
APIRouterV1.register(r'message', MessageViewSet, base_name='message')

from otp.rest_api import OTPViewSet
APIRouterV1.register(r'security/otp', OTPViewSet, base_name='otp')

from geobase.rest_api import CountryViewSet, RegionViewSet
APIRouterV1.register(r'geobase/country', CountryViewSet, base_name='country')
APIRouterV1.register(r'geobase/region', RegionViewSet, base_name='region')

from payments.rest_api import DepositRequestViewSet, WithdrawRequestViewSet, PaymentViewSet, BaseRequestViewSet
APIRouterV1.register(r'payments/baserequest', BaseRequestViewSet, base_name='baserequest')
APIRouterV1.register(r'payments/withdraw', WithdrawRequestViewSet, base_name='withdraw')
APIRouterV1.register(r'payments/deposit', DepositRequestViewSet, base_name='deposit')
APIRouterV1.register(r'payments', PaymentViewSet, base_name="payments")

from reports.rest_api import ReportViewSet
APIRouterV1.register(r'reports', ReportViewSet, base_name='reports')

from friend_recommend.rest_api import RecommendationViewSet
APIRouterV1.register(r'friend_recommend', RecommendationViewSet, base_name='friend_recommend')

from issuetracker.rest_api import UserIssueViewSet, IssueCommentViewSet
APIRouterV1.register(r'issue/(?P<issue_id>[0-9]+)/comment', IssueCommentViewSet, base_name='comment')
APIRouterV1.register(r'issue', UserIssueViewSet, base_name='issue')

from referral.rest_api import PartnerDomainViewSet
APIRouterV1.register(r'referral/partner_domain', PartnerDomainViewSet, base_name='partner_domain')

from education.rest_api import WebinarRegistrationViewSet
APIRouterV1.register(r'webinar_registration', WebinarRegistrationViewSet, base_name='webinar_registration')

from crm.rest_api import CustomerViewSet, InfoViewSet, ManagersViewSet
APIRouterV1.register(r'crm/customer', CustomerViewSet, base_name="customer")
APIRouterV1.register(r'crm/info', InfoViewSet, base_name="info")
APIRouterV1.register(r'crm/manager', ManagersViewSet, base_name='manager')

from massmail.rest_api import CampaignTypeViewSet
APIRouterV1.register(r'massmail/type', CampaignTypeViewSet, base_name='type')

from gcrm.rest.viewsets import ContactViewSet, ManagerViewSet, ManagerReassignRequestViewSet, \
    TaskViewSet, NoteViewSet, AccountViewSet, CallViewSet, CountryViewSet, RegionViewSet
APIRouterV1.register(r'gcrm/contact', ContactViewSet, base_name='contact')
APIRouterV1.register(r'gcrm/manager', ManagerViewSet, base_name='manager')
APIRouterV1.register(r'gcrm/reassign_request', ManagerReassignRequestViewSet, base_name='reassign_request')
APIRouterV1.register(r'gcrm/task', TaskViewSet, base_name='task')
APIRouterV1.register(r'gcrm/note', NoteViewSet, base_name='note')
APIRouterV1.register(r'gcrm/account', AccountViewSet, base_name='account')
APIRouterV1.register(r'gcrm/call', CallViewSet, base_name='call')
APIRouterV1.register(r'gcrm/country', CountryViewSet, base_name='country')
APIRouterV1.register(r'gcrm/region', RegionViewSet, base_name='region')
