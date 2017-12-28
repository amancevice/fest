"""
Google Cloud tools.
"""
import os

import httplib2
from apiclient import discovery
from oauth2client import service_account
from fest import graph
from fest import bases

GOOGLE_ACCOUNT_TYPE = os.getenv('GOOGLE_ACCOUNT_TYPE')
GOOGLE_CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')
GOOGLE_CLIENT_EMAIL = os.getenv('GOOGLE_CLIENT_EMAIL')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_PRIVATE_KEY = os.getenv('GOOGLE_PRIVATE_KEY')
GOOGLE_PRIVATE_KEY_ID = os.getenv('GOOGLE_PRIVATE_KEY_ID')
GOOGLE_SCOPE = os.getenv('GOOGLE_SCOPE')


class GoogleCloud(object):
    """ Google Cloud Service.

        :param object service: Google Cloud service resource
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

            :param list[str] scopes: List of service scopes
            :param str service_type: Google service type
            :param str private_key_id: Google private key ID
            :param str private_key: Google private key
            :param str client_email: Google client email
            :param str client_id: Google client ID
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

    def create_calendar(self, facebook_page, tz):
        """ Create calendar from FacebookPage object.

            :param object facebook_page: Facebook page object
            :param str tz: Timezone of facebook page
        """
        # pylint: disable=invalid-name,no-member
        service = self.service.calendars()
        request = service.insert(body=facebook_page.to_google(tz))
        return GoogleCalendar(self.service, **request.execute())

    def delete_calendar(self, google_id):
        """ Create calendar from FacebookPage object.

            :param str google_id: Google calendar ID
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

            :param str facebook_id: ID of facebook page
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
            yield GoogleCalendar(self.service, **item)
        try:
            request = service.list(syncToken=result['nextSyncToken'])
            result = request.execute()
            for item in result.get('items', []):
                yield GoogleCalendar(self.service, **item)
        except KeyError:
            pass


class GoogleCalendar(bases.BaseObject):
    """ Google Calendar Object.

        :param object service: GoogleCloud instance
    """
    def add_event(self, facebook_event):
        """ Add facebook event.

            :param object facebook_event: FacebookEvent instance
        """
        insert_event = facebook_event.to_google()
        service = self.service.events()
        request = service.insert(calendarId=self['id'],
                                 body=insert_event.struct)
        return request.execute()

    def add_owner(self, email):
        """ Give ownership to user by email.

            :param str email: Owner email address
        """
        acl = {'scope': {'type': 'user', 'value': email},
               'kind': 'calendar#aclRule',
               'role': 'owner'}
        service = self.service.acl()
        request = service.insert(calendarId=self['id'], body=acl)
        return request.execute()

    def clear_events(self):
        """ Clears the calendar of ALL events. """
        batch = self.service.new_batch_http_request()
        service = self.service.events()
        for event in self.iter_events():
            request = service.delete(calendarId=self['id'],
                                     eventId=event['id'])
            batch.add(request)
        return batch.execute()

    def get_events(self):
        """ Get events in calendar.

            :returns list[object]: List of GoogleEvent
        """
        return list(self.iter_events())

    def get_event(self, google_id):
        """ Get event by Google ID.

            :param str google_id: ID of facebook page
            :returns object: GoogleEvent instance
        """
        service = self.service.events()
        request = service.get(calendarId=self['id'], eventId=google_id)
        return GoogleEvent(self.service, **request.execute())

    def get_facebook_event(self, facebook_id):
        """ Get event by facebook ID.

            Searches 'extendedProperties :: private :: facebookId'

            :param str facebook_id: ID of facebook page
            :returns object: GoogleEvent instance
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
                                       pageToken=result['nextPageToken'])
                result = request.execute()
                for item in result.get('items', []):
                    yield GoogleEvent(self.service, **item)
                if not any(result.get('items', [])):
                    break
            except KeyError:
                break

    def patch_event(self, facebook_event, google_event):
        """ Patch facebook event.

            :param object facebook_event: FacebookEvent instance
            :param object google_event: GoogleEvent instance
        """
        patch_event = facebook_event.to_google()
        service = self.service.events()
        request = service.patch(calendarId=self['id'],
                                eventId=google_event['id'],
                                body=patch_event.struct)
        return request.execute()

    def sync_event(self, facebook_event):
        """ Synchronize facebook event with calendar.

            :param object facebook_event: Facebook event instance
        """
        # Attempt to patch existing event
        for google_event in self.iter_events():
            if google_event.facebook_id == facebook_event['id']:
                # Apply patch
                if google_event.facebook_digest != facebook_event.digest():
                    return self.patch_event(facebook_event, google_event)
                # No op
                return None
        # Add event if no events can be patched
        return self.add_event(facebook_event)

    def sync_events(self, *facebook_events):
        """ Synchronize facebook events with calendar.

            :param tuple facebook_events: Facebook event instances
        """
        eventmap = {x.facebook_id: x for x in self.iter_events()}
        batch = self.service.new_batch_http_request()
        service = self.service.events()

        # Add or patch facebook events
        for facebook_event in facebook_events:
            # Patch event if digests differ (otherwise no op)
            if facebook_event['id'] in eventmap:
                google_event = eventmap[facebook_event['id']]
                if google_event.facebook_digest != facebook_event.digest():
                    patch_event = facebook_event.to_google()
                    request = service.patch(calendarId=self['id'],
                                            eventId=google_event['id'],
                                            body=patch_event.struct)
                    batch.add(request)
            # Insert new event
            elif facebook_event['id'] not in eventmap:
                insert_event = facebook_event.to_google()
                request = service.insert(calendarId=self['id'],
                                         body=insert_event.struct)
                batch.add(request)

        # Execute batch request
        batch.execute()


class GoogleEvent(bases.BaseObject):
    """ Google Event Object. """
    @property
    def facebook_id(self):
        """ Helper to return facebook ID of event.

            :returns str: FacebookEvent ID
        """
        extended_properties = self.get('extendedProperties', {})
        private = extended_properties.get('shared', {})
        return private.get('facebookId')

    @property
    def facebook_digest(self):
        """ Helper to return facebook digest of event.

            :returns str: FacebookEvent ID
        """
        extended_properties = self.get('extendedProperties', {})
        private = extended_properties.get('shared', {})
        return private.get('digest')

    @staticmethod
    def from_facebook(facebook_event, service=None):
        """ Helper to convert a FacebookEvent to a GoogleEvent.

            :param object facebook_event: FacebookEvent instance
            :param object service: Optional GoogleCloud service instance
            :returns object: GoogleEvent instance
        """
        start_time = facebook_event.start_time()
        end_time = facebook_event.end_time()
        google_event = GoogleEvent(
            service=service,
            summary=facebook_event.get('name'),
            description=facebook_event.get('description'),
            location=facebook_event.location_string(),
            start={'dateTime': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
                   'timeZone': facebook_event.timezone()},
            end={'dateTime': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
                 'timeZone': facebook_event.timezone()},
            extendedProperties={
                'shared': {'facebookId': facebook_event.get('id'),
                           'digest': facebook_event.digest()}})
        return google_event


graph.FacebookEvent.to_google = GoogleEvent.from_facebook
