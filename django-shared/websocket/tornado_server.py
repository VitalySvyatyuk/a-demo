# -*- coding: utf-8 -*-
import json
import time
import re
from datetime import datetime

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.tcpserver


class QuotesStream(object):
    symbol_re = re.compile(r'"symbol":"(.+?)"')
    login_re = re.compile(r'"login":(\d+)')

    def __init__(self, stream):
        self.stream = stream
        self.channel_name = None
        self.stream.set_close_callback(self.on_stream_close)
        self.stream.read_until('\n', self.handshake_handler)

    def on_stream_close(self):
        QuotesReceiver.streams.remove(self)

    def handshake_handler(self, data):
        data = json.loads(data.strip())
        self.channel_name = data['channel_name']
        if self.channel_name not in QuotesConnection.trades_keys:
            QuotesConnection.trades_keys[self.channel_name] = {}
        self.stream.read_until('\n', self.main_loop)

    def main_loop(self, data):
        data = data.strip()
        if data == "{}":  # Keepalive
            pass
        else:
            if "MsType" in data:
                self.process_trade(data)
            else:
                self.process_quote(data)
        self.stream.read_until('\n', self.main_loop)

    def process_quote(self, data):
        start_time = time.time()
        QuotesReceiver.last_quote_in_between_time = start_time - QuotesReceiver.last_quote_end_time
        self.send_quote(data)
        QuotesReceiver.last_quote_end_time = time.time()
        QuotesReceiver.last_quote_processing_time = QuotesReceiver.last_quote_end_time - start_time

    def send_quote(self, data):
        QuotesReceiver.quotes_processed += 1
        QuotesReceiver.last_quote = data
        symbol = self.symbol_re.search(data).group(1)  # Sorry JSON, but regexp is like 1000 times faster
        if self.channel_name in QuotesConnection.quotes_subscribers and \
                        symbol in QuotesConnection.quotes_subscribers[self.channel_name]:
            subscribers = QuotesConnection.quotes_subscribers[self.channel_name][symbol]
            if subscribers:
                for s in subscribers:
                    s.write_message(data)
            else:
                del QuotesConnection.quotes_subscribers[self.channel_name][symbol]

    def process_trade(self, data):
        QuotesReceiver.last_trade = data
        login = int(self.login_re.search(data).group(1))
        if login in QuotesConnection.trades_subscribers:
            subscribers = QuotesConnection.trades_subscribers[login]
            if subscribers:
                for s in subscribers:
                    s.write_message(data)
            else:
                del QuotesConnection.trades_subscribers[login]
        # if client_id == "all":
        #     channel_name = self.channel_name[:-7]  # demo_trades -> demo
        #     for s in QuotesConnection.broadcast_trades_subscribers.get(channel_name, []):
        #         s.write_message(data)
        # elif client_id in QuotesConnection.trades_subscribers:
        #     QuotesConnection.trades_subscribers[client_id].write_message(data)


class QuotesReceiver(tornado.tcpserver.TCPServer):
    last_quote_processing_time = 0
    last_quote_in_between_time = 0
    last_quote_end_time = 0
    quotes_processed = 0
    last_quote = None
    last_trade = None
    streams = []

    def handle_stream(self, stream, address):
        QuotesReceiver.streams.append(QuotesStream(stream))


class QuotesConnection(tornado.websocket.WebSocketHandler):
    # Class level variables
    available_channels = ("real", "demo", "gtmarkets")
    # {"channel": {"quote": [list of connections]}}
    quotes_subscribers = {channel: {} for channel in available_channels}
    trades_subscribers = {}
    trades_keys = {}
    closed_connections = 0
    opened_connections = 0 

    def __init__(self, application, request, **kwargs):
        self.exchange = "real"
        super(QuotesConnection, self).__init__(application, request, **kwargs)

    def check_origin(self, origin):
        return True

    def open(self):
        QuotesConnection.opened_connections += 1

    def on_message(self, message):
        if 'mode' in message:  # Change quotes channel
            self.unsubscribe_all()
            self.exchange = message.split(':')[1]
        elif 'trades' in message:  # Subscribe to trades
            trade_key = message.split(':')[1]
            # Client sends comand like trades:key
            # To find out account login, trades of which client wants to recieve
            # We look up key in trades_keys, which is populated by server request
            if trade_key in self.trades_keys.get(self.exchange, {}):
                login = self.trades_keys[self.exchange][trade_key][0]
                self.trades_subscribers.setdefault(login, set()).add(self)
        elif message.startswith('!'):  # Unsubscribe from quote
            self.quotes_subscribers[self.exchange].get(message[1:], set()).discard(self)
        else:  # Subscribe to quote
            self.quotes_subscribers[self.exchange].setdefault(message, set()).add(self)

    def unsubscribe_all(self):
        for channel in self.quotes_subscribers.itervalues():
            for subscribers in channel.itervalues():
                subscribers.discard(self)
        for k, subscribers in self.trades_subscribers.iteritems():
            subscribers.discard(self)

    def on_close(self):
        QuotesConnection.closed_connections += 1
        self.unsubscribe_all()


class StatsHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        quotes_subscribers = set()
        for channel in QuotesConnection.quotes_subscribers.itervalues():
            for s in channel.itervalues():
                quotes_subscribers.update(s)

        if QuotesReceiver.last_quote:
            last_quote_time = datetime.fromtimestamp(int(json.loads(QuotesReceiver.last_quote)["time"]))
        else:
            last_quote_time = ""
        self.render("stats.html",
                    connected_quotes=len(quotes_subscribers),
                    connected_trades=len(QuotesConnection.trades_subscribers),
                    quotes_real=QuotesConnection.quotes_subscribers['real'].keys(),
                    quotes_demo=QuotesConnection.quotes_subscribers['demo'].keys(),
                    now=datetime.now(),
                    last_quote_time=last_quote_time,
                    last_quote_raw=QuotesReceiver.last_quote,
                    last_trade_raw=QuotesReceiver.last_trade,
                    closed_connections=QuotesConnection.closed_connections,
                    opened_connections=QuotesConnection.opened_connections,
                    quotes_processed=QuotesReceiver.quotes_processed,
                    last_quote_processing_time=QuotesReceiver.last_quote_processing_time * 1000,
                    last_quote_in_between_time=QuotesReceiver.last_quote_in_between_time * 1000,
                    buffers={s.channel_name: s.stream._read_buffer_size // 1024 for s in QuotesReceiver.streams},
                    )


class OrderTradesHandler(tornado.web.RequestHandler):
    def put(self, *args, **kwargs):
        request = json.loads(self.request.body)
        if request['channel_name'] in QuotesConnection.trades_keys:
            QuotesConnection.trades_keys[request['channel_name']][request['queue']] \
                = (int(request['login']), datetime.now())


if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/", StatsHandler),
        (r"/quotes", QuotesConnection),
        (r"/order_trades", OrderTradesHandler),
    ])

    app.listen(8500, "127.0.0.1")

    quotes_receiver = QuotesReceiver()
    quotes_receiver.listen(8501, "10.0.0.24")

    tornado.ioloop.IOLoop.instance().start()
