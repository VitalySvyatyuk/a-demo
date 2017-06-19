# -*- coding: utf-8 -*-

# should be there because of some dark reasons; do not put in gcapital/utils, uWSGI will fail

# decorator to ease model translations
# takes list of fields as 'fields' param
# automatically creates TranslationOptions and registers model
from modeltranslation.translator import TranslationOptions, translator


def model_translate(*fields):

    def inner(klass):

        class_name = klass.__name__
        options_class_name = class_name + "TranslationOptions"

        options_class = type(options_class_name, (TranslationOptions, ), {"fields": fields})

        if klass not in translator.get_registered_models():  # Workaround for AlreadyRegistered bug
            translator.register(klass, options_class)

        return klass

    return inner
