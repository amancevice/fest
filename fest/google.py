"""
Google Cloud tools
"""
import os

import httplib2
from apiclient import discovery
from oauth2client import service_account

GOOGLE_ACCOUNT_TYPE = os.getenv('GOOGLE_ACCOUNT_TYPE')
GOOGLE_CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')
GOOGLE_CLIENT_EMAIL = os.getenv('GOOGLE_CLIENT_EMAIL')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_PRIVATE_KEY = os.getenv('GOOGLE_PRIVATE_KEY')
GOOGLE_PRIVATE_KEY_ID = os.getenv('GOOGLE_PRIVATE_KEY_ID')
GOOGLE_SCOPE = os.getenv('GOOGLE_SCOPE')


class CalendarAPI(object):
    """ Google Calendar API Service.

        :param service: Google Cloud service resource
        :type service: googleapiclient.discovery.Resource
    """
    @classmethod
    def from_env(cls):
        """ Create CalendarAPI object from ENV variables. """
        return cls.from_credentials()

    @classmethod
    def from_credentials(cls, scopes=None, service_type=None,
                         private_key_id=None, private_key=None,
                         client_email=None, client_id=None):
        """ Create CalendarAPI object from credentials

            :param scopes: List of service scopes
            :param service_type: Google service type
            :param private_key_id: Google private key ID
            :param private_key: Google private key
            :param client_email: Google client email
            :param client_id: Google client ID
            :type scopes: list
            :type service_type: str
            :type private_key_id: str
            :type private_key: str
            :type client_email: str
            :type client_id: str
        """
        # pylint: disable=too-many-arguments
        keyfile_dict = {
            'type': service_type or GOOGLE_ACCOUNT_TYPE,
            'private_key_id': private_key_id or GOOGLE_PRIVATE_KEY_ID,
            'private_key': private_key or GOOGLE_PRIVATE_KEY,
            'client_email': client_email or GOOGLE_CLIENT_EMAIL,
            'client_id': client_id or GOOGLE_CLIENT_ID
        }
        credentials = \
            service_account.ServiceAccountCredentials.from_json_keyfile_dict(
                keyfile_dict, scopes=scopes or [GOOGLE_SCOPE])
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3',
                                  http=http,
                                  cache_discovery=False)
        return cls(service)

    def __init__(self, service):
        self.service = service

    def create_calendar(self, facebook_page, tz=None):
        """ Create calendar from FacebookPage object.

            :param facebook_page: Facebook page object
            :param tz: Time zone of facebook page
            :type facebook_page: fest.graph.FacebookPage
            :type tz: str
        """
        # pylint: disable=invalid-name,no-member
        service = self.service.calendars()
        request = service.insert(body=facebook_page.to_google(tz))
        return GoogleCalendar(self.service, **request.execute())

    def delete_calendar(self, google_id):
        """ Create calendar from FacebookPage object.

            :param google_id: Google calendar ID
            :type google_id: str
        """
        # pylint: disable=invalid-name,no-member
        service = self.service.calendars()
        request = service.delete(calendarId=google_id)
        return request.execute()

    def get_calendars(self):
        """ Get list of Google Calendars. """
        return list(self.iter_calendars())

    def get_calendar(self, google_id):
        """ Get calendar. """
        service = self.service.calendars()  # pylint: disable=no-member
        request = service.get(calendarId=google_id)
        return GoogleCalendar(self.service, **request.execute())

    def get_facebook_calendar(self, facebook_id):
        """ Get Google Calendar by facebook page ID.

            Searches descriptions for "facebook#<facebook_id>.

            :param facebook_id: ID of facebook page
            :type facebook_id: str
        """
        key = 'facebook#{}'.format(facebook_id)
        for cal in self.iter_calendars():
            if key in cal['description']:
                return cal
        return None

    def iter_calendars(self):
        """ Iterate over Google Calendars. """
        service = self.service.calendarList()  # pylint: disable=no-member
        request = service.list()
        result = request.execute()
        for item in result.get('items', []):
            yield GoogleCalendar(self.service, item)
        try:
            request = service.list(syncToken=result['nextSyncToken'])
            result = request.execute()
            for item in result.get('items', []):
                yield GoogleCalendar(self.service, item)
        except KeyError:
            pass


class GoogleObject(dict):
    """ Google Object. """
    def __init__(self, service, *args, **kwargs):
        self.service = service
        super(GoogleObject, self).__init__(*args, **kwargs)


class GoogleCalendar(GoogleObject):
    """ Google Calendar Object. """
    def add_events(self, *facebook_events):
        """ Add facebook events. """
        batch = self.service.new_batch_http_request()
        events = self.service.events()
        for event in facebook_events:
            batch.add(events.insert(calendarId=self['id'],
                                    body=event.to_google()))
        return batch.execute()

    def add_event(self, facebook_event):
        """ Add facebook event. """
        events = self.service.events()
        request = events.insert(calendarId=self['id'],
                                body=facebook_event.to_google())
        return request.execute()

    def add_owner(self, email):
        """ Give ownership to user by email. """
        acl = {'scope': {'type': 'user', 'value': email},
               'kind': 'calendar#aclRule',
               'role': 'owner'}
        service = self.service.acl()
        request = service.insert(calendarId=self['id'], body=acl)
        return request.execute()

    def clear_events(self):
        """ Clears the calendar of ALL events. """
        batch = self.service.new_batch_http_request()
        for event in self.iter_events():
            service = self.service.events()
            request = service.delete(calendarId=self['id'],
                                     eventId=event['id'])
            batch.add(request)
        return batch.execute()

    def get_events(self):
        """ Get events in calendar. """
        return list(self.iter_events())

    def get_event(self, google_id):
        """ Get event by Google ID.

            :param google_id: ID of facebook page
            :type google_id: str
        """
        service = self.service.events()
        request = service.get(calendarId=self['id'], eventId=google_id)
        return GoogleEvent(self.service, **request.execute())

    def get_facebook_event(self, facebook_id):
        """ Get event by facebook ID.

            Searches 'extendedProperties :: private :: facebookId'

            :param facebook_id: ID of facebook page
            :type facebook_id: str
        """
        for event in self.iter_events():
            if facebook_id == event.facebook_id:
                return event
        return None

    def iter_events(self):
        """ Iterate over all Google Calendar events. """
        service = self.service.events()
        request = service.list(calendarId=self['id'])
        result = request.execute()
        for item in result.get('items', []):
            yield GoogleEvent(self.service, **item)
        while True:
            try:
                request = service.list(calendarId=self['id'],
                                       pageToken=result['nextPageToken'],)
                result = request.execute()
                for item in result.get('items', []):
                    yield GoogleEvent(self.service, **item)
                if not any(result.get('items', [])):
                    break
            except KeyError:
                break

    def sync_page(self, facebook_page, tz=None):
        """ Synchronize FacebookPage object events with this calendar.

            :param facebook_page: Facebook page object
            :param tz: Time zone of facebook page
            :type facebook_page: fest.graph.FacebookPage
            :type tz: str
        """
        # pylint: disable=invalid-name
        batch = self.service.new_batch_http_request()
        calendars = self.service.calendars()
        events = self.service.events()
        batch.add(calendars.patch(calendarId=self['id'],
                                  body=facebook_page.to_google(tz)))
        for event in facebook_page.iter_events():
            batch.add(events.insert(calendarId=self['id'],
                                    body=event.to_google()))
        return batch.execute()


class GoogleEvent(GoogleObject):
    """ Google Event Object. """
    @property
    def facebook_id(self):
        """ Helper to return facebook ID of event. """
        extended_properties = self.get('extendedProperties', {})
        private = extended_properties.get('private', {})
        return private.get('facebookId')
