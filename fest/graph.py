"""
Facebook Graph API tools.
"""
import os
import urllib
from copy import deepcopy
from datetime import datetime
from datetime import timezone
from datetime import timedelta

import facebook

from fest import bases

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
FACEBOOK_PAGE_TOKEN = os.getenv('FACEBOOK_PAGE_TOKEN')


class GraphAPI(bases.BaseAPI):
    """ Facebook GraphAPI Object.

        :param object service: GraphAPI service instance
    """
    @classmethod
    def from_env(cls):
        """ Create GraphAPI object from ENV variables. """
        return cls.from_token()

    @classmethod
    def from_token(cls, page_token=None):
        """ Create GraphAPI object from credentials

            :param str page_token: Facebook page token
        """
        service = facebook.GraphAPI(page_token or FACEBOOK_PAGE_TOKEN)
        return cls(service)

    def get_page(self, page_id, *fields):
        """ Get facebook page.

            :param str page_id: facebook page ID
            :param tuple(str) fields: Optional page fields
        """
        fields = {'about', 'location', 'mission', 'name'} | set(fields)
        fields = ','.join(sorted(fields))
        path = f'{page_id}?fields={fields}'
        return FacebookPage(self, **self.get_object(path))

    def get_event(self, event_id, *fields):
        """ Get page event.

            :param str event_id: facebook event ID
            :param tuple(str) fields: Optional page fields
        """
        fields = {
            'cover', 'description', 'end_time', 'id', 'name', 'place',
            'start_time'
        } | set(fields)
        fields = ','.join(sorted(fields))
        path = f'{event_id}?fields={fields}'
        return FacebookEvent(self, **self.get_object(path))

    def get_events(self, page_id, **args):
        """ Get list of page events.

            :param str page_id: facebook page ID
            :param dict args: Optional arguments to get_object
        """
        return list(self.iter_events(page_id, **args))

    def get_object(self, facebook_id, **args):
        """ Get facebook object.

            :param str facebook_id: facebook object ID
            :param dict args: Optional additional arguments
        """
        params = urllib.parse.urlencode(args)
        self.logger.info('GET /%s?%s', facebook_id, params)
        return self.service.get_object(facebook_id, **args)

    def get_objects(self, facebook_ids, **args):
        """ Get facebook objects.

            :param str facebook_id: facebook object ID
            :param dict args: Optional additional arguments
        """
        return list(self.iter_objects(facebook_ids, **args))

    def iter_events(self, page_id, **args):
        """ Iterate over page events.

            :param str page_id: facebook page ID
            :param dict args: Optional arguments to get_object
        """
        params = urllib.parse.urlencode(args)
        path = '{page_id}/events?{params}'
        response = self.get_object(path)
        for item in response['data']:
            # Yield recurring events as individual FacebookEvent items
            try:
                for event_time in item['event_times']:
                    this_event = deepcopy(item)
                    del this_event['event_times']
                    this_event.update(event_time)
                    yield FacebookEvent(self, **this_event)
            # Yield normal FacebookEvent
            except KeyError:
                yield FacebookEvent(self, **item)
        while True:
            try:
                after = response['paging']['cursors']['after']
                response = self.get_object(path, after=after)
                for item in response['data']:
                    yield FacebookEvent(self, **item)
            except KeyError:
                break

    def iter_objects(self, facebook_ids, **args):
        """ Get facebook objects.

            :param str facebook_id: facebook object ID
            :param dict args: Optional additional arguments
        """
        params = urllib.parse.urlencode(args)
        self.logger.info('GET /%s?%s', facebook_ids, params)
        chunks = list(range(0, len(facebook_ids), 50)) + [len(facebook_ids)]
        for left, right in zip(chunks[:-1], chunks[1:]):
            objs = self.service.get_objects(facebook_ids[left:right], **args)
            for obj in objs.values():
                yield obj


class FacebookObject(bases.BaseObject):
    """ Base FacebookObject. """
    @property
    def source_id(self):
        """ The source of a facebook object is itself. """
        return self['id']

    @property
    def source_digest(self):
        """ The source of a facebook object is itself. """
        return self.digest()

    @property
    def url(self):
        """ Facebook URL of object. """
        return f'https://www.facebook.com/{self.source_id}'


class FacebookPage(FacebookObject):
    """ Facebook Page Object. """
    # pylint: disable=too-many-ancestors
    DESCRIPTION_KEYS = ('about', 'mission')
    LOCATION_KEYS = ('name', 'street', 'city', 'state', 'country', 'zip')

    def description_string(self, *keys):
        """ Get description as a string.

            :param tuple(str) keys: Optional keys to use in building string
        """
        keys = keys or self.DESCRIPTION_KEYS
        values = [self[x] for x in keys if x in self]
        values += [self.url]
        return '\n'.join(values) or None

    def location_string(self, *keys):
        """ Get location info as a string.

            :param tuple(str) keys: Optional keys to use in building string
        """
        keys = keys or self.LOCATION_KEYS
        location = self.get('location', {})
        values = [str(location[x]) for x in keys if x in location]
        return ' '.join(values) or None

    def get_event(self, event_id):
        """ Get page event.

            :param str event_id: facebook event ID
        """
        return self.service.get_event(event_id)

    def get_events(self, **args):
        """ Get list of page events.

            :param str time_filter: Optional time filter
        """
        return self.service.get_events(self['id'], **args)

    def iter_events(self, **args):
        """ Iterate over page events.

            :param str time_filter: Optional time filter
        """
        return self.service.iter_events(self['id'], **args)


class FacebookEvent(FacebookObject):
    """ Facebook Event Object. """
    # pylint: disable=too-many-ancestors
    LOCATION_KEYS = ('name', 'street', 'city', 'state', 'country', 'zip')

    def location_string(self, *keys):
        """ Get location info as a string.

            :param tuple(str) keys: Optional keys to use in building string
        """
        keys = keys or self.LOCATION_KEYS
        place = self.get('place', {}).copy()
        try:
            loc = place['location'].copy()
            loc.update(name=place['name'])
        except KeyError:
            loc = place
        values = [str(loc[x]) for x in keys if x in loc]
        return ' '.join(values) or None

    def timezone(self):
        """ Get timezone from event. """
        try:
            return self.start_time().tzname()
        except ValueError:
            return None

    def start_time(self):
        """ Helper to get start_time datetime object. """
        start_time = self.get('start_time')
        return datetime.strptime(start_time, DATETIME_FORMAT)

    def end_time(self, **delta):
        """ Helper to get end_time datetime object.

            :param dict delta: Optional timedelta if end_time not given
        """
        end_time = self.get('end_time')
        try:
            return datetime.strptime(end_time, DATETIME_FORMAT)
        except TypeError:
            delta = delta or {'hours': 1}
            return self.start_time() + timedelta(**delta)
