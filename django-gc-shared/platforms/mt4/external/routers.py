"""
Special rounting of different types of users.
"""


# noinspection PyProtectedMember,PyProtectedMember,PyProtectedMember,PyMethodMayBeStatic,PyMethodMayBeStatic,PyMethodMayBeStatic,PyUnusedLocal
class Mt4ExternalRouter(object):
    """A router to control all database operations on models in
    the platforms.mt4.external application

    Copypasted from Django manual
    """

    def db_for_read(self, model=None, **hints):
        """Point all operations on mt4_external models to mt4_externaldb"""
        # Same models with different databases
        if model._meta.app_label == 'external':
            if model.__name__ in ['RealTrade', 'RealUser', 'Mt4Quote']:
                return 'real'
            elif model.__name__ in ['DemoTrade', 'DemoUser']:
                return 'demo'
            elif model.__name__ in ['ArchiveTrade', 'ArchiveUser']:
                return 'db_archive'
            elif model.__name__ in ['Instruments']:
                return 'specifications'
            return 'mt4_externaldb'
        return None

    def db_for_write(self, model, **hints):
        """Point all operations on mt4_external models to mt4_externaldb"""
        return self.db_for_read(model, **hints)

    def allow_relation(self, obj1, obj2, **hints):
        """Allow any relation if a model in mt4_external is involved"""
        if obj1._meta.app_label == 'external' or obj2._meta.app_label == 'external':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Prevent syncdb for this app"""
        if app_label == 'external' or db != 'default':
            return False
