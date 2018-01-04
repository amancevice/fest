"""
Base objects
"""
import collections
import hashlib
import json
import logging


class BaseAPI(object):
    """ Base API. """
    # pylint: disable=too-few-public-methods
    def __init__(self, service):
        self.service = service
        self.logger = logging.getLogger(self.__log__)

    @property
    def __log__(self):
        """ Logger name. """
        cls = type(self)
        return '{mod}.{cls}'.format(mod=cls.__module__, cls=cls.__name__)


class BaseObject(collections.Mapping):
    """ Base Object. """
    def __init__(self, service, **service_object):
        # pylint: disable=super-init-not-called
        self.service = service
        self.struct = service_object

    def __getitem__(self, key):
        return self.struct[key]

    def __iter__(self):
        return iter(self.struct)

    def __len__(self):
        return len(self.struct)

    def __repr__(self):
        return str(self)

    def __str__(self):
        try:
            return json.dumps(self.struct, indent=2, sort_keys=True)
        except TypeError:
            return str(self.struct)

    def digest(self):
        """ Return SHA-1 of struct. """
        return hashlib.sha1(str(self).encode('utf-8')).hexdigest()

    @property
    def source_digest(self):
        """ Get digest of source object. """
        pass

    @property
    def source_id(self):
        """ Get ID of source object. """
        pass
