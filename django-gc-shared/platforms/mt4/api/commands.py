# -*- coding: utf-8 -*-

import re
import struct
import time
from datetime import datetime, timedelta
from itertools import groupby

from django.conf import settings
from django.utils.datastructures import SortedDict
from structures import from_dict

from platforms.mt4.api import (
    DatabaseCommand, SocketCommand, SocketAPI,
    CustomCommand, CustomAPI,
    UserInfo, UserHistory, Operation,

    # Constants.
    OPERATION_TYPES,

    # Exceptions.
    MT4Error, InvalidAccount,
    Custom2API, Custom3API)
from shared.compat import namedtuple


# Database commands; each should subclass DatabaseCommand, unless
# you're doing something tricky and define a single __required__
# attribute: sql.


# noinspection PyMethodMayBeStatic
class DatabaseHistory(DatabaseCommand):

    def before(self, api, start=None, end=None, opened=False, count_limit=None):
        return super(DatabaseHistory, self).before(api,
                                                   start=start or (datetime.now() - timedelta(300)),
                                                   end=end or datetime.now(),
                                                   opened=opened, count_limit=count_limit)

    def run(self, api, account, start, end, opened, count_limit, *args, **kwargs):
        """
        Get trade operations for choosen account.

        `start` - start date
        `end` - end date
        `opened` -  True for searching open trades in this timespan
                    using `open_time` field
                    False for searching closed trades, `close_time` field
        """
        from ..external.models import trade

        qs = trade[api.db_name].objects.filter(login=account)
        if opened:
            qs = qs.filter(open_time__range=(start, end))
        else:
            qs = qs.filter(close_time__range=(start, end))
        qs = qs.order_by('-open_time')
        if count_limit is not None:
            qs = qs[:count_limit]
        return qs

    def after(self, api, result):
        # To create structures of history operations, we need dictionaries, not Django models
        dict_models = result.values()
        # We need to preprocess results from db, so here we go...
        for obj in dict_models:
            cmd = obj.pop("cmd")
            obj.update(swap=obj.pop("swaps"),
                       type=unicode(OPERATION_TYPES.get(cmd) or cmd),
                       type_raw=cmd,
                       volume=float(obj["volume"]) / 100)
            # Create operations holder with basic information
        history = from_dict(UserHistory, {
            "login": api.uid,
            "timestamp": api.info().lastdate})
        # Populate it with all found operations
        history.operations = [from_dict(Operation, obj) for obj in dict_models]
        return history


# noinspection PyMethodMayBeStatic
class DatabaseInfo(DatabaseCommand):
    def run(self, api, account, *args, **kwargs):
        from ..external.models import mt4_user

        return mt4_user[api.db_name].objects.filter(login=account)

    def after(self, api, result):
        if not result:
            raise InvalidAccount(api.uid)
        else:
            return from_dict(UserInfo, result.values().get())


class DatabaseOpenOrders(DatabaseCommand):
    def run(self, api, account, *args, **kwargs):
        from ..external.models import trade

        return trade[api.db_name].objects.filter(close_time='1970-01-01',
                                                 cmd__in=[0, 1],
                                                 login=account).count()

# a) a command can register itself ...
DatabaseInfo.register("info")
DatabaseHistory.register("history")
DatabaseOpenOrders.register("db_open_orders_count")
# b) .. or we can register it manually

# Socket commands; each should subclass SocketCommand and define
# `command` attribute, optionally you can set `encoded` attribute
# to True, forcing the API to use encoded_query() instead of simple
# query() -- don't forget to provide key argument when calling a
# a command, in that case.

re_hash = re.compile(r"(?m)^(\w+):\s*(.+?)\s*$")
re_hash_ws = re.compile(r"(?m)^(\w+):(\s*.+?\s*)*$")


# noinspection PyMethodMayBeStatic
class SocketInfo(SocketCommand):
    command = "USERINFO"

    sensitive_fields_regexp = r"(?<=\|password=)[^|]+"

    def before(self, api):
        return super(SocketInfo, self).before(api, {
            "login": api.uid,
            "password": api.password,
        })

    def after(self, api, result):
        data, response = parse_response(result)

        # The remaining string is:
        # <login>\r\n
        # <name>\r\n
        # <timestamp>\r\n
        # ... junk ...

        login, name = response.split("\r\n")[:2]
        return from_dict(UserInfo,
                         norm(data, login=login, name=name))


# noinspection PyMethodMayBeStatic
class SocketUInfo(SocketCommand):
    command = "UINFO"
    encoded = True

    def before(self, api, from_ts=None, to_ts=None, force_calc_totals=False):
        params = SortedDict.fromkeys(('MASTER', 'IP', 'ACCOUNT'))
        params.update({
            "MASTER": settings.MT4_PLUGIN_UINFO_MASTER_PASSWORD,
            "key": settings.MT4_PLUGIN_UINFO_KEY,
            "ACCOUNT": api.uid,
            "IP": "127.0.0.1",
        })

        time_to_unix = lambda t: int(round(time.mktime(t.timetuple())))

        min_from_time = datetime(2000, 1, 1)

        if force_calc_totals:
            from_ts = from_ts or min_from_time

        if from_ts or to_ts:
            params['GETINOUTFROM'] = time_to_unix(from_ts or min_from_time)
            if to_ts:
                params['GETINOUTTO'] = time_to_unix(to_ts)
            else:
                params['GETINOUTTO'] = 0

        return super(SocketUInfo, self).before(api, params)

    def after(self, api, result):
        info = UserInfo()
        ordered_result_params = ('login', 'balance', 'credit', 'equity',
                                 'margin', 'free', 'group', 'deposit',
                                 'withdraw', 'credit_deposit',
                                 'credit_withdraw', 'irr', 'agent_commission',
                                 'profit')

        for index, data in enumerate(result.split("\r\n")):
            setattr(info, ordered_result_params[index], data)
        return info


# noinspection PyMethodMayBeStatic
class SocketHistory(SocketCommand):
    command = "USERHISTORY"

    def before(self, api, start=None, end=None):
        start = start or (datetime.now() - timedelta(300))
        end = end or datetime.now()
        return super(SocketHistory, self).before(api, {
            "login": api.uid,
            "password": api.password,
            "from": start.strftime("%s"),
            "to": end.strftime("%s")
        })

    def after(self, api, result):
        data, response = parse_response(result)

        # The remaining string is:
        # <login>\r\n
        # <name>\r\n
        # <timestamp>\r\n
        # ... operations ...

        response = response.strip().split("\r\n")
        login, name, timestamp = response[:3]

        history = from_dict(UserHistory,
                            norm(data, login=login, name=name, timestamp=timestamp))

        # FIXME: I've copied Igor's code, but it's still unclear why
        # we don't take the last argument. And thanks to the excellent
        # API docs, which don't cover it as well.
        fields = ("ticket", "open_time", "type", "volume", "symbol",
                  "open_price", "sl", "tp", "close_time", "close_price",
                  "swap", "profit")
        for line in response[3:]:
            operation = line.strip().split("\t")[:12]
            if len(operation) != 12:
                api.log.error("Failed to parse operation line: %r",
                              line)
            else:
                history.operations.append(
                    from_dict(Operation, dict(zip(fields, operation))))
        return history


# noinspection PyMethodMayBeStatic
class QuotesHistory(SocketCommand):
    command = 'HISTORYNEW'
    binary = True

    def before(self, api, **kwargs):
        params = {'symbol': kwargs['symbol'],
                  'from': kwargs['_from'],
                  'to': kwargs.get('_to', datetime.now()),
                  'period': kwargs.get('period', 60)}
        allowed_periods = {
            'M1': 1, 'M5': 5, 'M15': 15, 'H1': 60, 'H4': 240, 'D1': 1440,
            'W1': 10080, 'MN': 43200,
        }
        params['period'] = allowed_periods.get(params['period'], params['period'])
        assert params['period'] in allowed_periods.values(), 'Period "%s" no allowed' \
                                                             % kwargs.get('period')
        params['from'] = int(round(time.mktime(params['from'].timetuple())))
        params['to'] = int(round(time.mktime(params['to'].timetuple())))
        return super(QuotesHistory, self).before(api, **params)

    def after(self, api, result):
        # Copied from php code
        count, digits, ctime = struct.unpack('<III', result[:12])
        divide = float(10 ** digits or 1)
        output = []
        data_t = namedtuple('QuotesHistory', ('time', 'open', 'high', 'low', 'close', 'volume'))
        for i in xrange(count):
            result_part = result[12 + i * 28:12 + (i + 1) * 28]
            if len(result_part) < 28:
                break
            data = struct.unpack('<iiiiid', result_part)
            time = datetime.fromtimestamp(data[0])
            _open = data[1] / divide
            high = (data[1] + data[2]) / divide
            low = (data[1] + data[3]) / divide
            close = (data[1] + data[4]) / divide
            volume = data[5]
            output.append(data_t(time, _open, high, low, close, volume))
        return output


QuotesHistory.register('quotes_history')


# noinspection PyMethodMayBeStatic
@SocketAPI.register_command
class CreateAccount(SocketCommand):
    command = "NEWACCOUNT"

    sensitive_fields_regexp = r"((?<=\|PASSWORD=)[^|]+)|((?<=\|PHONE_PASSWORD=)[^|]+)|((?<=\|INVESTOR=)[^|]+)"

    def before(self, api, **kwargs):
        params = SortedDict.fromkeys(["MASTER", "IP", "GROUP", "NAME", "PASSWORD", "INVESTOR",
                                      "EMAIL", "COUNTRY", "CITY", "STATE", "ADDRESS", "COMMENT",
                                      "PHONE", "PHONE_PASSWORD", "STATUS", "ZIPCODE", "ID", "LEVERAGE",
                                      "AGENT", "DEPOSIT", "SEND_REPORTS", "READ_ONLY"], "")
        params.update(dict((key.upper(), value or "")
                           for key, value in kwargs.iteritems()))

        return super(CreateAccount, self).before(api, params)

    def after(self, api, result):
        return int(*re.findall(r"(?m)^LOGIN=(\d+)\s*$", result))


# noinspection PyClassHasNoInit,PyPep8Naming
class TRADE_TYPES:
    open_trade = 66
    open_order = 67
    close_trade = 70
    modify_order = 71
    delete_order = 72


@SocketAPI.register_command
class OpenTrade(SocketCommand):
    command = "WEBTRADE"

    encoded = True

    sensitive_fields_regexp = r"(?<=\|PASSWORD=)[^|]+"

    def before(self, api, **kwargs):
        params = SortedDict.fromkeys(["MASTER", "IP", "ACCOUNT", "PASSWORD",
                                      "CMD", "TYPE", "ORDER", "SYMBOL", "OPENPRICE", "EXPIRATION",
                                      "VOLUME", "SL", "TP", "COMMENT"], "")

        params.update({
            "MASTER": settings.WEBTRADER_MASTER_KEY,
            "key": settings.WEBTRADER_PLUGIN_KEY,
            "IP": "127.0.0.1",
        })

        params.update(dict((key.upper(), value or "")
                           for key, value in kwargs.iteritems()))
        return super(OpenTrade, self).before(api, params)


@SocketAPI.register_command
def quotes(self, *pair):
    # Wonderful Mt4 introduces positional arguments, hurray!
    # Which aren't supported in the current api bindings ...
    pair = ''.join(pair)
    response = self.query("QUOTES-%s," % pair)

    # Expected format is:
    # <growth:up|down> <pair> <bid> <ask> <date>\n<date>.

    try:
        growth = response.split()[0]
        bid = float(response.split()[2])
        ask = float(response.split()[3])
        date = datetime.strptime(response.split('\n')[1],
                                 '%Y.%m.%d %H:%M:%S')
        return {'growth': growth, 'bid': bid, 'ask': ask,
                'date': date}
    except IndexError:
        raise MT4Error("Invalid quotes pair: %r" % pair)


@SocketAPI.register_command
def open_orders(api, password=None):
    """Returns the open orders for the account"""
    if password is None:
        password = api.password
    result = api.query(
        "WAPUSER-%s|%s" % (api.uid, password))
    if result.startswith('Invalid Account'):
        raise MT4Error('Invalid Account')
    orders = result.strip('end').strip().strip('<br/>').split('<anchor>')[1:]

    def parse_order(order):
        type = order.split('<')[0]
        amount, symbol = order.strip().strip('<br/>').split('> ')[-1].split(' ')
        return {'type': type, 'amount': float(amount), 'symbol': symbol.upper()}

    return map(parse_order, orders)


# noinspection PyMethodMayBeStatic
class AccumulatedTrades(DatabaseCommand):
    def run(self, api, account, *args, **kwargs):
        return api.raw_query("""SELECT cmd, close_time, profit, volume
            FROM mt4_trades WHERE login = %(account)s
            AND close_time > '2000-01-01'
            ORDER BY close_time""", account=account)

    def after(self, api, result):
        keys = ['profit', 'inout', 'trade_count', 'inout_count', 'deposit',
                'withdraw', 'volume', 'credit', 'credit_deposit', 'credit_withdraw']

        totals = dict.fromkeys(keys, 0)
        trades_t = namedtuple('Trades', keys)

        for date, rows in groupby(result, lambda row: row['close_time'].date()):
            rows = list(rows)

            def _reduce(totals, row):
                if row['cmd'] < 2:  # 0, 1 - торговая
                    totals['trade_count'] += 1
                    totals['profit'] += row['profit']
                    totals['volume'] += row['volume']
                elif row['cmd'] == 6:  # 2, 3, 4, 5 - отложенный ордер, 6 - балансовая операция
                    totals['inout'] += row['profit']
                    totals['inout_count'] += 1
                    if row['profit'] >= 0:
                        totals['deposit'] += row['profit']
                    else:
                        totals['withdraw'] += row['profit']
                elif row['cmd'] == 7:  # 7- кредит
                    totals['credit'] += row['profit']
                    if row['profit'] >= 0:
                        totals['credit_deposit'] += row['profit']
                    else:
                        totals['credit_withdraw'] += row['profit']
                return totals

            daytrades = reduce(_reduce, rows, dict.fromkeys(keys, 0))
            for k, v in daytrades.iteritems():
                totals[k] += v
            yield date, trades_t(**totals)


# noinspection PyMethodMayBeStatic
class FirstDeposit(DatabaseCommand):
    def run(self, api, account, *args, **kwargs):
        return api.raw_query('''SELECT sum(profit) AS profit FROM mt4_trades t1
            WHERE ticket < (SELECT min(ticket) FROM mt4_trades t2 WHERE cmd < 2 AND login = %(account)s)
            AND cmd = 6
            AND login = %(account)s''', account=account)

    def after(self, api, result):
        try:
            return result[0]['profit']
        except IndexError:
            return 0


AccumulatedTrades.register('trades')
FirstDeposit.register('first_deposit')

SocketAPI.register_command("old_info", SocketInfo)
SocketAPI.register_command("info", SocketUInfo)
SocketAPI.register_command("history", SocketHistory)


@CustomAPI.register_command
class ChangeAccountBalance(CustomCommand):
    name = "change_account_balance"

    def before(self, api, login, amount, comment, request_id, transaction_type, credit):
        from platforms.models import TradingAccount

        mt4_acc = TradingAccount.objects.filter(mt4_id=login)
        if mt4_acc and mt4_acc[0].is_micro:
            amount *= 100
        return super(ChangeAccountBalance, self).before(
            api, login=login, amount=amount, comment=comment, request_id=request_id,
            transaction_type=transaction_type, credit=credit
        )


@Custom2API.register_command
class NewQuotesHistory(CustomCommand):
    name = "quotes_history"

    log_answers = False

    # error codes
    WRONG_SYMBOL = 11

    def before(self, api, symbol, period, time_from, time_to):
        from project.templatetags.app_tags import as_timestamp

        if isinstance(time_from, datetime):
            time_from = as_timestamp(time_from)

        if isinstance(time_to, datetime):
            time_to = as_timestamp(time_to)

        return super(NewQuotesHistory, self).before(
            api, symbol=symbol, period=period, time_from=time_from, time_to=time_to
        )


@Custom3API.register_command
class RabbitMqTradesInfo(CustomCommand):
    name = "rabbitmq_trades_info"


# noinspection PyMethodMayBeStatic
@Custom3API.register_command
class PasswordAuthentication(CustomCommand):
    name = "password_authentication"
    sensitive_fields_regexp = r'(?<="pass": ")[^"]+'

    def after(self, api, result):
        return result["result"] is True  # We may get arbitrary things here so we should check if it IS True


class ChangeOptionsStyle(CustomCommand):
    name = "option_style_change"

    def before(self, api, login, new_style):
        if new_style not in ("AM", "EU"):
            raise ValueError('new_style should be either "AM" or "EU", not {}'.format(new_style))

        return super(ChangeOptionsStyle, self).before(
            api, login=login, new_style=new_style,
        )

CustomAPI.register_command("change_options_style", ChangeOptionsStyle)


# Santa's little helpers.

def parse_response(response):
    """
    Parses a given response string and returns a pair, where the first
    element is dict of `Field: value` pairs and second is the unparsed
    part of the string.
    """
    return re_hash.findall(response), re_hash_ws.sub("", response)


def norm(data, **kwargs):
    """
    Normalizes keys in a given list of key-value pairs and optionally
    updates resulting dict with kwargs.
    """
    return dict(((str(k).lower(), v) for k, v in data), **kwargs)
