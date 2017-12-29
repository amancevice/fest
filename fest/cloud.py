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


class CalendarAPI(bases.BaseAPI):
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

    def add_event(self, calendar_id, facebook_event):
        """ Add facebook event.

            :param str calendar_id: Google Calendar ID
            :param object facebook_event: FacebookEvent instance
        """
        insert_event = facebook_event.to_google()
        service = self.service.events()
        request = service.insert(calendarId=calendar_id,
                                 body=insert_event.struct)
        self.logger.info('CREATE %s/%s', calendar_id, facebook_event['id'])
        return request.execute()

    def add_owner(self, calendar_id, email):
        """ Give ownership to user by email.

            :param str calendar_id: Google Calendar ID
            :param str email: Owner email address
        """
        acl = {'scope': {'type': 'user', 'value': email},
               'kind': 'calendar#aclRule',
               'role': 'owner'}
        service = self.service.acl()
        request = service.insert(calendarId=calendar_id, body=acl)
        self.logger.info('ADD OWNER %s/%s', calendar_id, email)
        return request.execute()

    def clear_events(self, calendar_id):
        """ Clears the calendar of ALL events.

            :param str calendar_id: Google Calendar ID
        """
        batch = self.service.new_batch_http_request()
        service = self.service.events()
        for event in self.iter_events(calendar_id):
            request = service.delete(calendarId=calendar_id,
                                     eventId=event['id'])
            self.logger.warning('DELETE %s/%s', calendar_id, event['id'])
            batch.add(request)
        return batch.execute()

    def create_calendar(self, facebook_page, tz):
        """ Create calendar from FacebookPage object.

            :param object facebook_page: Facebook page object
            :param str tz: Timezone of facebook page
        """
        # pylint: disable=invalid-name,no-member
        service = self.service.calendars()
        request = service.insert(body=facebook_page.to_google(tz))
        self.logger.info('CREATE %s %s', facebook_page['id'], tz)
        return GoogleCalendar(self.service, **request.execute())

    def delete_calendar(self, calendar_id):
        """ Create calendar from FacebookPage object.

            :param str calendar_id: Google Calendar ID
        """
        # pylint: disable=invalid-name,no-member
        service = self.service.calendars()
        request = service.delete(calendarId=calendar_id)
        self.logger.warning('DELETE %s', calendar_id)
        return request.execute()

    def get_calendars(self):
        """ Get list of Google Calendars. """
        return list(self.iter_calendars())

    def get_calendar(self, calendar_id):
        """ Get calendar.

            :param str calendar_id: Google Calendar ID
        """
        service = self.service.calendars()  # pylint: disable=no-member
        request = service.get(calendarId=calendar_id)
        self.logger.info('GET %s', calendar_id)
        return GoogleCalendar(self, **request.execute())

    def get_event(self, calendar_id, event_id):
        """ Get event by Google ID.

            :param str calendar_id: Google Calendar ID
            :param str event_id: Google Event ID
            :returns object: GoogleEvent instance
        """
        service = self.service.events()
        request = service.get(calendarId=calendar_id, eventId=event_id)
        self.logger.info('GET %s/%s', calendar_id, event_id)
        return GoogleEvent(self, **request.execute())

    def get_events(self, calendar_id):
        """ Get events in calendar.

            :param str calendar_id: Google Calendar ID
            :returns list[object]: List of GoogleEvent
        """
        return list(self.iter_events(calendar_id))

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

    def get_facebook_event(self, calendar_id, facebook_id):
        """ Get event by facebook ID.

            Searches 'extendedProperties :: private :: facebookId'

            :param str calendar_id: Google calendar ID
            :param str facebook_id: facebook page ID
            :returns object: GoogleEvent instance
        """
        for google_event in self.iter_events(calendar_id):
            if facebook_id == google_event.facebook_id:
                return google_event
        return None

    def iter_calendars(self):
        """ Iterate over Google Calendars. """
        service = self.service.calendarList()  # pylint: disable=no-member
        request = service.list()
        result = request.execute()
        for item in result.get('items', []):
            self.logger.info('GET %s', item['id'])
            yield GoogleCalendar(self, **item)
        try:
            request = service.list(pageToken=result['nextPageToken'])
            result = request.execute()
            for item in result.get('items', []):
                self.logger.info('GET %s', item['id'])
                yield GoogleCalendar(self, **item)
        except KeyError:
            pass

    def iter_events(self, calendar_id):
        """ Iterate over all Google Calendar events.

            :param str calendar_id: Google Calendar ID
        """
        service = self.service.events()
        request = service.list(calendarId=calendar_id)
        self.logger.info('GET %s/events', calendar_id)
        result = request.execute()
        for item in result.get('items', []):
            yield GoogleEvent(self, **item)
        while True:
            try:
                request = service.list(calendarId=calendar_id,
                                       pageToken=result['nextPageToken'])
                self.logger.info('GET %s/events %s',
                                 calendar_id,
                                 result['nextPageToken'])
                result = request.execute()
                for item in result.get('items', []):
                    yield GoogleEvent(self, **item)
                if not any(result.get('items', [])):
                    break
            except KeyError:
                break

    def patch_event(self, calendar_id, event_id, facebook_event):
        """ Patch facebook event.

            :param str calendar_id: Google Calendar ID
            :param str event_id: Google Event ID
            :param object facebook_event: FacebookEvent instance
        """
        patch = facebook_event.to_google()
        service = self.service.events()
        request = service.patch(calendarId=calendar_id,
                                eventId=event_id,
                                body=patch.struct)
        self.logger.info('PATCH %s/%s[%s]',
                         calendar_id,
                         event_id,
                         facebook_event['id'])
        return request.execute()

    def sync_event(self, calendar_id, facebook_event):
        """ Synchronize facebook event with calendar.

            :param str calendar_id: Google Calendar ID
            :param object facebook_event: Facebook event instance
        """
        # Attempt to patch existing event
        for google_event in self.iter_events(calendar_id):
            if google_event.facebook_id == facebook_event['id']:
                # Apply patch
                if google_event.facebook_digest != facebook_event.digest():
                    return self.patch_event(calendar_id,
                                            google_event['id'],
                                            facebook_event)
                # No op
                return None
        # Add event if no events can be patched
        return self.add_event(calendar_id, facebook_event)

    def sync_events(self, calendar_id, facebook_events, dryrun=False):
        """ Synchronize facebook events with calendar.

            :param str calendar_id: Google Calendar ID
            :param list[object] facebook_events: FacebookEvent instances
            :param bool dryrun: Toggle execute batch request
        """
        eventmap = {x.facebook_id: x for x in self.iter_events(calendar_id)}
        batch = self.service.new_batch_http_request()
        service = self.service.events()

        # Add or patch facebook events
        for facebook_event in facebook_events:
            # Patch event if digests differ (otherwise no op)
            if facebook_event['id'] in eventmap:
                google_event = eventmap[facebook_event['id']]
                if google_event.facebook_digest != facebook_event.digest():
                    patch = facebook_event.to_google()
                    request = service.patch(calendarId=calendar_id,
                                            eventId=google_event['id'],
                                            body=patch.struct)
                    batch.add(request)
                    self.logger.info('PATCH %s/%s[%s]',
                                     calendar_id,
                                     google_event['id'],
                                     facebook_event['id'])
                else:
                    self.logger.debug('NO-OP %s/%s[%s]',
                                      calendar_id,
                                      google_event['id'],
                                      facebook_event['id'])
            # Insert new event
            else:
                insert = facebook_event.to_google()
                request = service.insert(calendarId=calendar_id,
                                         body=insert.struct)
                batch.add(request)
                self.logger.info('CREATE %s/%s[%s]',
                                 calendar_id,
                                 google_event['id'],
                                 facebook_event['id'])

        # Execute batch request
        if dryrun is False:
            self.logger.info('EXECUTE')
            return batch.execute()
        self.logger.debug('DRYRUN')
        return None


class GoogleCalendar(bases.BaseObject):
    """ Google Calendar Object.

        :param object service: GoogleCloud instance
    """
    def add_event(self, facebook_event):
        """ Add facebook event.

            :param object facebook_event: FacebookEvent instance
        """
        return self.service.add_event(self['id'], facebook_event)

    def add_owner(self, email):
        """ Give ownership to user by email.

            :param str email: Owner email address
        """
        return self.service.add_owner(self['id'], email)

    def clear_events(self):
        """ Clears the calendar of ALL events. """
        return self.service.clear_events(self['id'])

    def get_events(self):
        """ Get events in calendar.

            :returns list[object]: List of GoogleEvent
        """
        return list(self.iter_events())

    def get_event(self, event_id):
        """ Get event by Google ID.

            :param str event_id: ID of facebook page
            :returns object: GoogleEvent instance
        """
        return self.service.get_event(self['id'], event_id)

    def get_facebook_event(self, facebook_id):
        """ Get event by facebook ID.

            Searches 'extendedProperties :: private :: facebookId'

            :param str facebook_id: ID of facebook page
            :returns object: GoogleEvent instance
        """
        return self.service.get_facebook_event(self['id'], facebook_id)

    def iter_events(self):
        """ Iterate over all Google Calendar events. """
        return self.service.iter_events(self['id'])

    def patch_event(self, event_id, facebook_event):
        """ Patch facebook event.

            :param object event_id: Google Event ID
            :param object facebook_event: FacebookEvent instance
        """
        return self.service.patch_event(self['id'], event_id, facebook_event)

    def sync_event(self, facebook_event):
        """ Synchronize facebook event with calendar.

            :param object facebook_event: Facebook event instance
        """
        return self.service.sync_event(self['id'], facebook_event)

    def sync_events(self, facebook_events, dryrun=False):
        """ Synchronize facebook events with calendar.

            :param list[object] facebook_events: Facebook event instances
            :param bool dryrun: Toggle execute batch request
        """
        return self.service.sync_events(self['id'], facebook_events, dryrun)


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
