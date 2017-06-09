# -*- coding: utf-8 -*-
from unittest import TestCase
from zeep import Client
from zeep.transports import Transport
from datetime import datetime, time

CLIENT = Client("https://demows.cfhclearing.com:8090/BrokerDataAccess?wsdl",
           transport=Transport(http_auth=("UpTraderAdmin", "UpTraderAdmin1")))

TEST_DATE = datetime(2016, 8, 25)


class TestBasicFunc(TestCase):
    """
    Testing methods that don't require data.
    """
    client = Client("https://demows.cfhclearing.com:8090/BrokerDataAccess?wsdl",
                    transport=Transport(http_auth=("UpTraderAdmin", "UpTraderAdmin1")))

    def test_validate(self):
        self.assertTrue(self.client.service.ValidateService())

    def test_lastmidrate(self):
        midrate = float(self.client.service.GetLastMidRate(InstrumentSymbol="EURUSD"))
        self.assertTrue(0 < midrate < 2)

    def test_eodmidrate(self):
        midrate = float(self.client.service.GetEODMidRate(InstrumentSymbol="EURUSD", TradeDate=TEST_DATE))
        self.assertAlmostEquals(midrate, 1.129, places=3)

    def test_completetime(self):
        comp_time = self.client.service.GetGlobalEODCompleteTime(tradeDate=TEST_DATE).time()
        self.assertEquals(comp_time, time(21, 55, 27, 797000))

    def test_clientinfo(self):
        pass

    def test_accountlist(self):
        pass

    def test_accountinfo(self):
        pass

    def test_getlogins(self):
        pass

