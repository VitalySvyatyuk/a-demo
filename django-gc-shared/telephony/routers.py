# -*- coding: utf-8 -*-


class AsteriskDBRouter(object):
    def db_for_read(self, model, **hints):
        if model.__name__ in ['ExternalAsteriskCDR', 'PhoneUser']:
            return 'asterisk'

    def db_for_write(self, model, **hints):
        if model.__name__ in ['ExternalAsteriskCDR', 'PhoneUser']:
            return 'asterisk'

    def allow_relation(self, obj1, obj2, **hints):
        pass

    def allow_migrate(self, db, model):
        pass
