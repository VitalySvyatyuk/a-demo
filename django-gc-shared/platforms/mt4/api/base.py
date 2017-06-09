# -*- coding: utf-8 -*-
from platforms.mt4.api.utils import to_underscore, to_camelcase

__all__ = ("BaseAPI", "BaseCommand")

import logging
import types


class BaseAPIMetaclass(type):
    """
    Metaclass which initializes API class, by adding command registry
    dict and logger.
    """
    def __new__(mcs, name, bases, attrs):
        new_class = type.__new__(mcs, name, bases, attrs)
        new_class.commands = {}
        new_class.log = logging.getLogger(new_class.__name__)
        return new_class


class BaseAPI(object):
    """Base API class, which implements command registration."""

    __metaclass__ = BaseAPIMetaclass

    def __getattr__(self, attr):
        try:
            return self.__class__.commands[attr](self)
        except KeyError:
            raise AttributeError(attr)

    def query(self, *args, **kwargs):
        raise NotImplementedError(
            "You must define a query() method on your %r subclass." % self)

    @classmethod
    def register_command(cls, *args):
        """Registers a command within an API class.

        Can be called either with a single argument `command`, which
        is a BaseCommand subclass, or a __non anonymous__ function:

            BaseAPI.register_command(SomeCommand)
            BaseAPI.register_command(some_other_command)

        in that case a name for a command is constructed from the __name__
        attribute; alternatively you can pass in two arguments: `name`
        and `command`:

            BaseAPI.register_command("some_command", SomeCommand)
            BaseAPI.register_command("some_other_command",
                                     some_other_command)

        Raises TypeError if a given command is not a subclass of BaseCommand
        and ValueError if a command has already been registered.
        """
        try:
            name, command = args
        except ValueError:
            name, command = None, args[0]

        # If a given command is a callable, we wrap it in BaseCommand,
        # using callable's body for run() method.
        if not isinstance(command, types.TypeType) and \
               callable(command) and command.__name__ != "<lambda>":
            name = command.__name__
            import copy
            command_ = copy.copy(command)
            attrs = {
                "run": lambda self, *args, **kwargs: command_(*args, **kwargs)
            }
            command = type(to_camelcase(name), (BaseCommand,), attrs)
        if not isinstance(command, types.TypeType):
            raise TypeError(command)
        elif not name:
            # `SomeLongCommand` will be registered as 'some_long'
            # if name wansn't provided explicitly.
            name = to_underscore(command.__name__.replace("Command", ""))

        if not issubclass(command, BaseCommand):
            raise TypeError("%r doesn't subclass BaseCommand." % command)
        elif name in cls.commands:
            raise ValueError("%r is already registered." % name)

        cls.commands[name] = command
        return command


class BaseCommand(object):
    """Base API command class.

    Subclasses might also define the following methods:

      - BaseCommand.before(self, api, *args, **kwargs) which might
        modify arguments a subclass is called with and __should__
        return them back (as a pair of args and kwargs)

      - after(self, api, result) which might parse / modify result
        object returned by run() and __should__ return it back.
    """
    def __init__(self, api):
        self.api = api

    def run(self, api, *args, **kwargs):
        raise NotImplementedError(
            "You must define a run() method on your %r subclass." % self)

    # noinspection PyArgumentList
    def __call__(self, *args, **kwargs):
        if hasattr(self, "before"):
            args, kwargs = self.before(self.api, *args, **kwargs)

        result = self.run(self.api, *args, **kwargs)

        if hasattr(self, "after"):
            return self.after(self.api, result)
        else:
            return result
