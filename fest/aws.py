"""
AWS Lambda Entrypoints.
"""
import os

import fest

FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
GOOGLE_CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')


def sync_events(event=None, _=None):
    """ Entrypoint for AWS Lambda.

        Example payload:

        {
            "facebook_id": "<page-id>",
            "google_id": "<calendar-id>",
            "time_filter": "<optional-time-filter>"
        }
    """
    # Read event
    event = event or {}
    facebook_id = event.get('facebook_id') or FACEBOOK_PAGE_ID
    google_id = event.get('google_id') or GOOGLE_CALENDAR_ID
    time_filter = event.get('time_filter')

    # Get google calendar
    cloud = fest.CalendarAPI.from_env()
    gcal = cloud.get_calendar(google_id)
    gevents = gcal.get_events()

    # Get facebook events
    graph = fest.GraphAPI()
    page = graph.get_page(facebook_id)
    events = page.get_events(time_filter=time_filter)

    # Merge events
    gids = set(x.facebook_id for x in gevents)
    fids = set(x['id'] for x in events if x['id'] not in gids)
    sync = [x for x in events if x['id'] in fids]

    # Sync
    for item in sync:
        gcal.add_event(item)
