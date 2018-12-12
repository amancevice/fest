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
        self.created = []
        self.updated = []
        self.deleted = []

    @staticmethod
    def callbackgen(collection):
        """ Generate callback function to collect responses. """
        def callback(_, res, err):
            if err:
                raise err
            collection.append(res)
        return callback

    def batchgen(self, requests, callback):
        """ Generate batched requests with callback. """
        total = len(requests)
        chunks = list(range(0, total, MAX_BATCH_REQUESTS)) + [total]
        for left, right in zip(chunks[:-1], chunks[1:]):
            chunk = requests[left:right]
            batch = self.calendar.batch(callback)
            for request in chunk:
                batch.add(request)
            yield batch

    def execbatches(self, batches, method, dryrun=False):
        """ Execute batches. """
        total = len(batches)
        for count, batch in enumerate(batches):
            self.calendar.logger.info(
                'BATCH %s %d/%d',
                method,
                count + 1,
                total,
            )
            if not dryrun:
                batch.execute()

    def execute(self, dryrun=False):
        """ Execute sync future. """
        # Get facebook events
        facebook_events = {x['id']: x for x in self.request.execute()}
        if not any(facebook_events):
            self.calendar.logger.info('NO-OP')
            return {
                'created': self.created,
                'updated': self.updated,
                'deleted': self.deleted,
            }

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
                privateExtendedProperty=f'facebookPageId={self.page.id}',
            )
        }

        # Assemble batched requests
        create = []
        update = []
        delete = []
        events = self.calendar.events()
        for facebook_id, source in facebook_events.items():
            digest = utils.digest(source)
            if facebook_id not in google_events:
                create.append(events.insert(
                    calendarId=self.calendar.calendar_id,
                    body=self.page.to_google(source),
                ))
            elif digest != google_events[facebook_id]['digest']:
                update.append(events.update(
                    calendarId=self.calendar.calendar_id,
                    eventId=google_events[facebook_id]['google_id'],
                    body=self.page.to_google(source),
                ))
        for facebook_id in google_events.keys() - facebook_events.keys():
            delete.append(events.delete(
                calendarId=self.calendar.calendar_id,
                eventId=google_events[facebook_id]['google_id'],
            ))

        # Execute batched requests
        self.execbatches(
            list(self.batchgen(create, self.callbackgen(self.created))),
            'POST',
            dryrun,
        )
        self.execbatches(
            list(self.batchgen(update, self.callbackgen(self.updated))),
            'PATCH',
            dryrun,
        )
        self.execbatches(
            list(self.batchgen(delete, self.callbackgen(self.deleted))),
            'DELETE',
            dryrun,
        )
        return {
            'created': self.created,
            'updated': self.updated,
            'deleted': self.deleted,
        }

    def filter(self, func):
        """ Fitler request. """
        self.request = self.request.filter(func)
        return self
