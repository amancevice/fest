"""
Utility functions
"""
import hashlib
import json
import logging


def digest(obj, encoding='utf-8'):
    """ Get SHA1 hexdigest of JSON object. """
    return hashlib.sha1(json.dumps(obj).encode(encoding)).hexdigest()


def logger(obj):
    """ Get logger for object. """
    cls = type(obj)
    clsname = cls.__name__
    modname = cls.__module__
    return logging.getLogger(f'{modname}.{clsname}')
