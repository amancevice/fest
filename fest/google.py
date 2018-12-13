"""
Google Calendar.
"""
import urllib

from fest import utils

MAX_BATCH_REQUESTS = 50


class GoogleCalendar:
    """ Google Calendar

        :param object calendarapi: Google Calendar API client
        :param str calendar_id: Google Calendar ID
    """
    def __init__(self, calendarapi, calendar_id):
        self.calendarapi = calendarapi
        self.calendar_id = calendar_id
        self.logger = utils.logger(self)
        self.batch = calendarapi.new_batch_http_request
        self.events = calendarapi.events

    def get_events(self, **kwargs):
        """ Get Google Calendar events. """
        return utils.Future(self.iter_events(**kwargs))

    def iter_events(self, **kwargs):
        """ Yield calendar event objects. """
        # Get initial response
        params = urllib.parse.urlencode(kwargs)
        self.logger.info('GET /%s?%s', self.calendar_id, params)
        events = self.events()
        request = events.list(calendarId=self.calendar_id, **kwargs)
        response = request.execute()

        # Yield items in this page
        items = response.get('items') or []
        yield from items

        # Yield items from subsequent pages
        try:
            kwargs.update(pageToken=response['nextPageToken'])
            yield from self.iter_events(**kwargs)
        except KeyError:
            pass

    def sync(self, page, **kwargs):
        """ Get GoogleSyncFuture instance. """
        return GoogleSyncFuture(page.get_events(**kwargs), page, self)


class GoogleSyncFuture:
    """ FacebookPage => GoogleCalendar sync future. """
    def __init__(self, request, page, calendar):
        self.request = request
        self.page = page
        self.calendar = calendar
        self.create = {}
        self.update = {}
        self.delete = {}

    @staticmethod
    def callbackgen(collection):
        """ Generate callback function to collect responses. """
        def callback(_, res, err):
            if err:
                raise err
            facebook_id = res['extendedProperties']['private']['facebookId']
            collection[facebook_id] = res
        return callback

    def batchgen(self, method, requests):
        """ Generate batched requests with callback. """
        if any(requests):
            count = 0
            batch = self.calendar.batch(self.callbackgen(requests))
            for request in requests.values():
                batch.add(method(**request))
                count += 1
                if count == MAX_BATCH_REQUESTS:
                    count = 0
                    yield batch
                    batch = self.calendar.batch(self.callbackgen(requests))
            yield batch

    def execbatch(self, verb, method, requests, dryrun=False):
        """ Execute batches. """
        batchgen = self.batchgen(method, requests)
        batches = list(batchgen)
        for i, batch in enumerate(batches):
            self.calendar.logger.info(
                '%s BATCH %d/%d',
                verb,
                i + 1,
                len(batches) % MAX_BATCH_REQUESTS,
            )
            if not dryrun:
                batch.execute()

    def execute(self, dryrun=False):
        """ Execute sync future. """
        # Get facebook events
        facebook_events = {x['id']: x for x in self.request.execute()}
        if not any(facebook_events):
            self.calendar.logger.info('NO-OP')
            return self

        # Get Google Calendar events
        start_times = [
            x['start_time'] for x in facebook_events.values()
            if 'start_time' in x
        ]
        end_times = [
            x['end_time'] for x in facebook_events.values()
            if 'end_time' in x
        ]
        google_events = {
            x['extendedProperties']['private']['facebookId']: {
                'digest': x['extendedProperties']['private']['facebookDigest'],
                'google_id': x['id'],
            }
            for x in self.calendar.iter_events(
                timeMin=min(start_times + end_times),
                timeMax=max(start_times + end_times),
                singleEvents=True,
                privateExtendedProperty=f'facebookPageId={self.page.id}',
            )
        }

        # Get create/update/delete request payloads
        for facebook_id, event in facebook_events.items():
            digest = utils.digest(event)
            if facebook_id not in google_events:
                self.create[facebook_id] = {
                    'calendarId': self.calendar.calendar_id,
                    'body': self.page.to_google(event),
                }

            elif digest != google_events[facebook_id]['digest']:
                self.update[facebook_id] = {
                    'calendarId': self.calendar.calendar_id,
                    'eventId': google_events[facebook_id]['google_id'],
                    'body': self.page.to_google(event),
                }
        for facebook_id in google_events.keys() - facebook_events.keys():
            self.delete[facebook_id] = {
                'calendarId': self.calendar.calendar_id,
                'eventId': google_events[facebook_id]['google_id'],
            }

        # Execute batched requests
        events = self.calendar.events()
        self.execbatch('POST', events.insert, self.create, dryrun)
        self.execbatch('PATCH', events.update, self.update, dryrun)
        self.execbatch('DELETE', events.delete, self.delete, dryrun)
        return self

    def filter(self, func):
        """ Fitler request. """
        self.request = self.request.filter(func)
        return self

    def to_dict(self):
        """ Return created/updated/deleted events as dict. """
        return {
            'created': self.create,
            'updated': self.update,
            'deleted': self.delete,
        }
