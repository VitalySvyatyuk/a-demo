import re
import xmlrpclib
import logging

from django.conf import settings

from platforms.exceptions import PlatformError

log = logging.getLogger(__name__)

class MT4Exception(PlatformError):
    pass


class RemoteMT4Manager(object):
    def __init__(self, engine):
        server, port = settings.MT4_MANAGER_SERVER_ADDRESS
        self.engine = xmlrpclib.ServerProxy("http://%s:%s/" % (server, port), allow_none=True)
        self.mt4_connection_details = settings.MT4_API_ENGINES[engine]

    def _check_password_requirement(self, password):
        if len(password) < 6 or not re.search("[a-zA-Z]", password) or not re.search("[0-9]", password):
            raise ValueError("Password should be at least 6 characters long and contain at least 1 digit and 1 letter")

    def _handle_fault(self, method, *args):
        for i, j in enumerate(args):
            if i is None:
                log.critical("MT4 method {} received None arg (arg index: {}), list of args {}".format(method, j, args))
        try:
            log.debug("XMLRPCserver trying to call mt4 method {} with following parameters {}".format(method, args))
            return self.engine.call_mt4_method(self.mt4_connection_details, method, *args)
        except xmlrpclib.Fault as e:
            if 'mt4_api.MT4Exception' in e.faultString.split(':', 1)[0]:
                raise MT4Exception(e.faultString.split(':', 1)[1])
            elif 'exceptions.ValueError' in e.faultString.split(':', 1)[0]:
                raise ValueError(e.faultString.split(':', 1)[1])
            raise

    def change_balance(self, login, amount, comment, credit=False):
        if not comment:
            comment = "Balance/credit operation"  # MT4 requires us to have a comment
        self._handle_fault('change_balance', login, amount, comment, credit)

    # -1 means "do not modify"
    def change_user_data(self, login, leverage=-1, agent_account=-1, enable=-1, read_only=-1, send_reports=-1):
        self._handle_fault('change_user_data', login, leverage, agent_account, enable, read_only, send_reports)

    def change_password(self, login, password, investor=False, clean_pubkey=False):
        self._check_password_requirement(password)
        self._handle_fault('change_password', login, password, investor, clean_pubkey)

    def check_password(self, login, password):
        return self._handle_fault('check_password', login, password)

    def create_account(self, group, password, leverage, name, login=0, agent_account=0, password_phone="", enable=True,
                       read_only=False, country="", state="", city="", address="", email="", phone=""):
        self._check_password_requirement(password)
        # Since we need to protect from send None value
        return self._handle_fault('create_account', group, password, leverage, name, login or 0, agent_account or 0,
                                  password_phone or "", enable, read_only, country or "", state or "", city or "",
                                  address or "", email or "", phone or "")