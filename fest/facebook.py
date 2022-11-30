"""
facebook
"""
import urllib
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from copy import deepcopy

from fest import utils

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
MAX_OBJECTS = 50  # facebook-imposed limit


class FacebookPage:
    """
    Facebook Page object.

    :param object graphapi: GraphAPI client
    :param str page_id: facebook page ID/Alias
    """

    def __init__(self, graphapi, page_id):
        self.graphapi = graphapi
        self.id = page_id  # pylint: disable=invalid-name
        self.logger = utils.logger(self)

    def get_events(self, **args):
        """
        Get events as Future.
        """
        return utils.Future(self.iter_events(**args))

    def get_objects(self, ids, **args):
        """
        Get objects as Future.
        """
        return utils.Future(self.iter_objects(ids, **args))

    def iter_events(self, **args):
        """
        Yield events from pages of GraphAPI `get_object` results.
        Recurring events are exploded into individual objects.
        """
        # Get initial response
        path = f"{self.id}/events"
        params = urllib.parse.urlencode(args)
        self.logger.info("GET /%s?%s", path, params)
        response = self.graphapi.get_object(path, **args)

        # Yield items in this page
        for event in response["data"]:
            yield from self.explode_event(event, **args)

        # Yield items from subsequent pages
        try:
            args.update(after=response["paging"]["cursors"]["after"])
            yield from self.iter_events(**args)
        except KeyError:
            pass

    def iter_objects(self, ids, **args):
        """
        Yield objects from GraphAPI `get_objects` results.
        """
        # Split `ids` into chunks of `MAX_OBJECTS` for Graph API
        chunks = list(range(0, len(ids), MAX_OBJECTS)) + [len(ids)]

        # Yield objects from chunks
        for left, right in zip(chunks[:-1], chunks[1:]):
            self.logger.info("GET /%s", ",".join(ids[left:right]))
            objs = self.graphapi.get_objects(ids[left:right], **args)
            yield from objs.values()

    @staticmethod
    def explode_event(event, **args):
        """
        Yield recurring facebook event as individual copies.
        """
        # Yield recurring events
        try:
            for event_time in event["event_times"]:
                start_time = datetime.strptime(
                    event_time["start_time"],
                    DATETIME_FORMAT,
                )
                end_time = datetime.strptime(
                    event_time["end_time"],
                    DATETIME_FORMAT,
                )

                # Only yield upcoming/past events if `time_filter` specified
                time_filter = args.get("time_filter")
                now = datetime.utcnow().replace(tzinfo=timezone.utc)
                if (
                    (time_filter is None)
                    or (time_filter == "upcoming" and start_time >= now)
                    or (time_filter == "past" and end_time <= now)
                ):
                    this_event = deepcopy(event)
                    del this_event["event_times"]
                    this_event.update(event_time)
                    yield this_event

        # Yield single event
        except KeyError:
            yield event

    @staticmethod
    def location_string(event):
        """
        Get event location info as a string.
        """
        place = event.get("place", {}).copy()
        try:
            loc = place["location"].copy()
            loc.update(name=place["name"])
        except KeyError:
            loc = place
        keys = ("name", "street", "city", "state", "country", "zip")
        values = [str(loc[x]) for x in keys if x in loc]
        return " ".join(values) or None

    def to_google(self, event):
        """
        Convert a facebook event to a Google Calendar event.
        """
        facebook_id = event["id"]
        summary = event.get("name")
        desc = event.get("description")
        url = f"https://www.facebook.com/{facebook_id}"
        description = f"{desc}\n\n{url}"
        start_time = datetime.strptime(event["start_time"], DATETIME_FORMAT)
        try:
            end_time = datetime.strptime(event["end_time"], DATETIME_FORMAT)
        except KeyError:
            end_time = start_time + timedelta(hours=1)
        time_zone = start_time.tzname() or end_time.tzname()
        start_time = start_time.isoformat()
        end_time = end_time.isoformat()
        location = self.location_string(event)
        digest = utils.digest(event)
        google_event = {
            "summary": summary,
            "description": description,
            "location": location,
            "start": {
                "dateTime": start_time,
                "timeZone": time_zone,
            },
            "end": {
                "dateTime": end_time,
                "timeZone": time_zone,
            },
            "extendedProperties": {
                "private": {
                    "facebookDigest": digest,
                    "facebookId": facebook_id,
                    "facebookPageId": self.id,
                },
            },
        }
        return google_event
