# coding=utf-8

"""
This API type describes custom commands written by
Andrey Vinogradov which usually follow MT4 Socket API's
conventions, but listen on different ports.
"""

import logging
import re
import socket
from json import dumps, loads

from django.conf import settings

from .utils import get_engine_name
from .base import BaseAPI, BaseCommand
from .exceptions import MT4Error


class CustomAPI(BaseAPI):
    def __init__(self, engine=None):
        self.uid = None
        self._engine = engine
        super(CustomAPI, self).__init__()

    @property
    def engine(self):
        return self._engine or get_engine_name(self.uid)

    def get_ip_and_port(self):
        return settings.ENGINES[self.engine]['custom']

    def connect(self):
        ip, port = self.get_ip_and_port()  # Different Custom API commands have different ports

        # noinspection PyAttributeOutsideInit
        self.log = logging.getLogger('CustomAPI.%s:%s' % (ip, port))

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.settimeout(settings.MT4_SERVER_SOCKET_TIMEOUT)

        try:
            server.connect((ip, port))
            return server
        except socket.error as exc:
            self.log.exception("Error connecting to MetaTrader Custom API server:")
            raise MT4Error(exc)

    def _do_query(self, qs, sensitive_fields_regexp):
        if not isinstance(qs, unicode):
            qs = qs.decode("utf-8")

        server = self.connect()
        qs_for_log = qs
        if sensitive_fields_regexp is not None:
            qs_for_log = re.sub(sensitive_fields_regexp, '******', qs_for_log)
        self.log.debug("Executing query: %r", qs_for_log)
        server.send(qs)

        try:
            data = []
            while True:
                buf = server.recv(10)
                data.append(buf)
                if not buf: # соединение закрыто сервером
                    break
            return "".join(data)
        except socket.error as exc:
            self.log.exception("Error receiving data:")
            raise MT4Error(exc)

        finally:
            server.close()

    def query(self, payload, log_answers=True, sensitive_fields_regexp=None):
        """
        Sends a given query string to the server, then returns received data (as object) or APIError
        Answer from server should always contain "status" and "message" fields,
        other fields depend on particular command
        """
        data = self._do_query(payload, sensitive_fields_regexp)
        try:
            data = loads(data)
        except (ValueError, TypeError):
            self.log.debug("Got data in wrong format", data)
            raise MT4Error("Got data in wrong format: %s" % repr(data))
        else:
            self.log.debug("Got: %r", data if log_answers else "<command asked not to log answer>")

            # status=0 is reserved as good answer, other - for errors
            if data["status"] != 0:
                raise MT4Error(data["status"], data["message"])
        return data


class Custom2API(CustomAPI):

    def get_ip_and_port(self):
        return settings.ENGINES[self.engine]['custom2']


class Custom3API(CustomAPI):
    def get_ip_and_port(self):
        return settings.ENGINES[self.engine]['custom3']


class CustomCommand(BaseCommand):
    """
    Упрощает написание команд для CustomAPI
    """

    ###
    # Стандартные ошибки, общие для всех команд
    # Все командно-специфичные ошибки должны начинаться с 11
    ###

    OK = 0  # ok
    INTERNAL_ERROR = 1  # внутренняя ошибка
    WRONG_SOCKET = 2  # неверная команда для сокета
    MT4_ERROR = 3  # ошибка МТ4
    UNKNOWN_COMMAND = 4  # сервер не знает такой команды

    port = None  # type: int
    log_answers = True  # type: bool
    sensitive_fields_regexp = None  # type: str

    @classmethod
    def register(cls):
        """
        Регистрируем команды в регистре команд с доступом по CustomAPI().<cls.name>
        """
        CustomAPI.register_command(cls.name, cls)

    def before(self, api, *args, **kwargs):
        """
        Добавляет к сообщению на сервер имя команды, которое берется из поля name класса команды
        """
        if getattr(self, "name", None) is not None:
            kwargs.update(command=self.name)

        return tuple(), kwargs

    def run(self, api, *args, **kwargs):
        """
        Запуск команды
        """
        # так как общение с сервером идет через JSON, то args игнорируются,
        # а словарь kwargs просто преобразуется в строковое представление
        return api.query(dumps(kwargs), self.log_answers, self.sensitive_fields_regexp)
