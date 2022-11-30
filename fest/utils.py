"""
Utility functions
"""
import hashlib
import json
import logging


class Future:
    """
    Base future.
    """

    def __init__(self, request):
        self.request = request

    def execute(self):
        """Execute request."""
        return list(self.request)

    def filter(self, func):
        """Fitler request."""
        self.request = filter(func, self.request)
        return self


def digest(obj, encoding="utf-8"):
    """
    Get SHA1 hexdigest of JSON object.
    """
    return hashlib.sha1(json.dumps(obj).encode(encoding)).hexdigest()


def logger(obj):
    """
    Get logger for object.
    """
    cls = type(obj)
    clsname = cls.__name__
    modname = cls.__module__
    return logging.getLogger(f"{modname}.{clsname}")
