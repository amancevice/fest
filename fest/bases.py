"""
Base objects
"""
import collections
import hashlib
import json


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
