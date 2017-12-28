"""
Base objects
"""
import collections
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
        return json.dumps(self.struct, indent=2, sort_keys=True)

    def __str__(self):
        return str(self.struct)
