# -*- coding: utf-8 -*-


class Bunch(object):
    """A dictionary that provides attribute-style access."""

    def __init__(self, *args, **kwargs):
        self.__dict__.update(*args, **kwargs)


class Enum(object):
    """
    A small helper class for more readable enumerations, compatible
    with Django's choice convention.

    Example:
        MY_ENUM = Enum(
            ('MY_NAME', 'My verbose name'),
            ('MY_AGE', 'My verbose age'),
        )
        assert MY_ENUM.MY_AGE == 1
        assert MY_ENUM[1] == (2, 'My verbose age')

    Originally from http://djangosnippets.org/snippets/1647/
    """
    def __init__(self, *options):
        self.enum_list = []
        self.enum_dict = {}

        for idx, item in enumerate(options):
            attr, verbose_name = item

            self.enum_list.append((idx + 1, verbose_name))
            self.enum_dict[attr] = idx + 1

    def __contains__(self, v):
        return v in self.enum_list

    def __len__(self):
        return len(self.enum_list)

    def __getitem__(self, v):
        if isinstance(v, basestring):
            return self.enum_dict[v]
        elif isinstance(v, int):
            return self.enum_list[v]

    def __getattr__(self, name):
        return self.enum_dict[name]

    def __iter__(self):
        return self.enum_list.__iter__()
