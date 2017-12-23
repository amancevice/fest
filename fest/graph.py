"""
Facebook Graph API tools.
"""
import os
from datetime import datetime

import facebook

FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')


def authenticated(func):
    """ Authentication decorator. """
    def wrapper(graph, *args, **kwargs):
        """ Authentication wrapper. """
        try:
            return func(graph, *args, **kwargs)
        except facebook.GraphAPIError:
            graph.authenticate()
            return func(graph, *args, **kwargs)
    return wrapper


class GraphAPI(facebook.GraphAPI):
    """ Facebook GraphAPI Object.

        :param app_id: Facebook app ID
        :param app_secret: Facebook app secret ID
        :type app_id: str
        :type app_secret: str
    """
    def __init__(self, app_id=None, app_secret=None, **kwargs):
        self.app_id = app_id or FACEBOOK_APP_ID
        self.app_secret = app_secret or FACEBOOK_APP_SECRET
        super(GraphAPI, self).__init__(**kwargs)

    def authenticate(self):
        """ Get access token. """
        self.access_token = self.get_app_access_token(self.app_id,
                                                      self.app_secret)

    @authenticated
    def get_page(self, page_id, *fields):
        """ Get facebook page. """
        fields = {'about', 'location', 'mission', 'name'} | set(fields)
        path = '{}?fields={}'.format(page_id, ','.join(sorted(fields)))
        return FacebookPage(self, **self.get_object(path))

    def get_events(self, page_id, time_filter=None):
        """ Get list of page events. """
        return list(self.iter_events(page_id, time_filter))

    @authenticated
    def iter_events(self, page_id, time_filter=None):
        """ Iterate over page events. """
        path = '{}/events'.format(page_id)
        if time_filter:
            path += '?time_filter={}'.format(time_filter)
        response = self.get_object(path)
        for item in response['data']:
            yield FacebookEvent(self, **item)
        while True:
            try:
                after = response['paging']['cursors']['after']
                response = self.get_object(path, after=after)
                for item in response['data']:
                    yield FacebookEvent(self, **item)
            except KeyError:
                break


class FacebookObject(dict):
    """ Base Facebook Object. """
    LOCATION_KEYS = ('name', 'street', 'city', 'state', 'country', 'zip')

    def __init__(self, graph, *args, **kwargs):
        self.graph = graph
        super(FacebookObject, self).__init__(*args, **kwargs)

    def get_events(self, time_filter=None):
        """ Get list of page events. """
        return list(self.graph.iter_events(self['id'], time_filter))

    def iter_events(self, time_filter=None):
        """ Iterate over page events. """
        return self.graph.iter_events(self['id'], time_filter=time_filter)


class FacebookPage(FacebookObject):
    """ Facebook Page Object. """
    DESCRIPTION_KEYS = ('about', 'mission')

    def description_string(self, *keys):
        """ Get description as a string. """
        keys = keys or self.DESCRIPTION_KEYS
        values = [self[x] for x in keys if x in self] + \
            ["facebook#{id}".format(**self)]
        return '\n'.join(values) or None

    def location_string(self, *keys):
        """ Get location info as a string. """
        keys = keys or self.LOCATION_KEYS
        location = self.get('location', {})
        values = [str(location[x]) for x in keys if x in location]
        return ' '.join(values) or None

    def get_events(self, time_filter=None):
        """ Get list of page events. """
        return self.graph.get_events(self['id'], time_filter)

    def to_google(self, tz=None):  # pylint: disable=invalid-name
        """ Convert object to Google. """
        return {
            'description': self.description_string(),
            'summary': self.get('name'),
            'location': self.location_string(),
            "timeZone": tz
        }


class FacebookEvent(FacebookObject):
    """ Facebook Event Object. """
    def location_string(self, *keys):
        """ Get location info as a string. """
        keys = keys or self.LOCATION_KEYS
        place = self.get('place', {}).copy()
        try:
            loc = place.pop('location')
            loc.update(place)
        except KeyError:
            loc = place
        values = [str(loc[x]) for x in keys if x in loc]
        return ' '.join(values) or None

    def timezone(self):
        """ Get timezone from event. """
        try:
            start = datetime.strptime(self.get('start_time'),
                                      '%Y-%m-%dT%H:%M:%S%z')
            return start.tzname()
        except TypeError:
            return None

    def to_google(self):
        """ Convert event to Google format. """
        return {
            'summary': self.get('name'),
            'description': self.get('description'),
            'location': self.location_string(),
            'start': {
                'dateTime': self.get('start_time'),
                'timeZone': self.timezone()
            },
            'end': {
                'dateTime': self.get('end_time', self.get('start_time')),
                'timeZone': self.timezone()
            },
            'extendedProperties': {
                'shared': {
                    'facebookId': self.get('id')
                }
            }
        }
