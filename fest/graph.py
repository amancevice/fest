"""
Facebook Graph API tools.
"""
import os
from copy import deepcopy
from datetime import timedelta

import facebook
from dateutil import parser as dateparser
from fest import bases

FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')


def authenticated(func):
    """ Authentication decorator. """
    def wrapper(graph, *args, **kwargs):
        """ Authentication wrapper. """
        if graph.service.access_token is None:
            graph.authenticate()
        try:
            return func(graph, *args, **kwargs)
        except facebook.GraphAPIError:
            graph.authenticate()
            return func(graph, *args, **kwargs)
    return wrapper


class GraphAPI(bases.BaseAPI):
    """ Facebook GraphAPI Object.

        :param object service: GraphAPI service instance
    """
    @classmethod
    def from_env(cls):
        """ Create GraphAPI object from ENV variables. """
        return cls.from_credentials()

    @classmethod
    def from_credentials(cls, app_id=None, app_secret=None):
        """ Create GraphAPI object from credentials

            :param str app_id: Facebook app ID
            :param str app_secret: Facebook app secret ID
        """
        service = facebook.GraphAPI()
        service.app_id = app_id or FACEBOOK_APP_ID
        service.app_secret = app_secret or FACEBOOK_APP_SECRET
        return cls(service)

    def authenticate(self):
        """ Get access token. """
        self.service.access_token = \
            self.service.get_app_access_token(
                self.service.app_id, self.service.app_secret)

    def get_page(self, page_id, *fields):
        """ Get facebook page.

            :param str page_id: facebook page ID
            :param tuple(str) fields: Optional page fields
        """
        fields = {'about', 'location', 'mission', 'name'} | set(fields)
        path = '{}?fields={}'.format(page_id, ','.join(sorted(fields)))
        return FacebookPage(self, **self.get_object(path))

    def get_event(self, event_id, *fields):
        """ Get page event.

            :param str event_id: facebook event ID
            :param tuple(str) fields: Optional page fields
        """
        fields = {'cover', 'description', 'end_time', 'id', 'name', 'place',
                  'start_time'} | set(fields)
        path = '{}?fields={}'.format(event_id, ','.join(sorted(fields)))
        return FacebookEvent(self, **self.get_object(path))

    def get_events(self, page_id, event_state_filter=None, time_filter=None):
        """ Get list of page events.

            :param str page_id: facebook page ID
            :param list<str> event_state_filter: Optional event state filter
            :param str time_filter: Optional time filter
        """
        return list(self.iter_events(page_id, event_state_filter, time_filter))

    @authenticated
    def get_object(self, facebook_id, **args):
        """ Get facebook object.

            :param str facebook_id: facebook object ID
            :param dict args: Optional additional arguments
        """
        self.logger.info('GET /%s %r', facebook_id, args)
        return self.service.get_object(facebook_id, **args)

    def iter_events(self, page_id, event_state_filter=None, time_filter=None):
        """ Iterate over page events.

            :param str page_id: facebook page ID
            :param list<str> event_state_filter: Optional event state filter
            :param str time_filter: Optional time filter
        """
        params = []
        if event_state_filter:
            params.append('event_state_filter={!r}'.format(event_state_filter))
        if time_filter:
            params.append('time_filter={}'.format(time_filter))
        path = '{}/events?{}'.format(page_id, '&'.join(params))
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
        return 'https://www.facebook.com/{id}'.format(id=self.source_id)


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

    def get_events(self, event_state_filter=None, time_filter=None):
        """ Get list of page events.

            :param str time_filter: Optional time filter
        """
        return self.service.get_events(
            self['id'], event_state_filter, time_filter)

    def iter_events(self, event_state_filter=None, time_filter=None):
        """ Iterate over page events.

            :param str time_filter: Optional time filter
        """
        return self.service.iter_events(
            self['id'], event_state_filter, time_filter)


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
            # pylint: disable=no-member
            timestamp = dateparser.parse(self.get('start_time'))
            offset = timestamp.tzinfo.utcoffset(timestamp)
            sign = '-' if offset.total_seconds() < 0 else '+'
            seconds = offset.total_seconds()
            hours = str(abs(int(seconds / 60**2))).rjust(2, '0')
            minutes = str(abs(int(seconds % 60**2))).rjust(2, '0')
            return 'UTC{sign}{hours}:{minutes}'.format(sign=sign,
                                                       hours=hours,
                                                       minutes=minutes)
        except (AttributeError, TypeError):
            return None

    def start_time(self):
        """ Helper to get start_time datetime object. """
        return dateparser.parse(self.get('start_time'))

    def end_time(self, **delta):
        """ Helper to get end_time datetime object.

            :param dict delta: Optional timedelta if end_time not given
        """
        try:
            return dateparser.parse(self.get('end_time'))
        except TypeError:
            delta = delta or {'hours': 1}
            return self.start_time() + timedelta(**delta)
