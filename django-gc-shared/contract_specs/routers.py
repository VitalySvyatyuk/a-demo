# -*- coding: utf-8 -*-


class MultiDBRouter(object):
    def db_for_read(self, model, **hints):
        """Manage routes or Mt4 abstract models to read 'em"""
        # Don't care about anything except mt4 models
        if model.__name__ in ['Instruments', 'Options', 'OptionsUS']:
            return 'specifications'
        if model.__name__ in ["InstrumentsByGroup", "SymbolsByInstrument"]:
            return 'config'

    def db_for_write(self, model, **hints):
        """Blocking writing of abstract models"""
        return None
