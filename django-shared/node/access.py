# coding: utf-8

class PublicAccessMixin(object):
    """Mix it in, if the access to the model is public"""

    public_access = True

    @classmethod
    def has_access(cls, user):
        return True

    @classmethod
    def access_description(cls):
        return u'Публичный доступ'


class LoggedInAccessMixin(object):

    public_access = False

    @classmethod
    def has_access(cls, user):
        return user.is_authenticated()

    @classmethod
    def access_description(cls):
        return u'Только для зарегистрированных пользователей'
