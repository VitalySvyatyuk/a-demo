# -*- coding: utf-8 -*-
import StringIO
import hashlib
import json


def convert_to_base64(img):
    stream = StringIO.StringIO()
    img.save(stream, "png")
    return stream.getvalue().encode("base64")


def make_hash(*data_list):
    salt = "|#^4e12)uih87efh70823o&*^ub%r%q&5qjvj#"
    return hashlib.sha1(
        json.dumps(data_list, sort_keys=True) + salt).hexdigest()


def dict_without(dict, attributes):
    return {k: v
            for k, v in dict.iteritems()
            if k not in attributes}
