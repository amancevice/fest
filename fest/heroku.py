"""
Heroku app
"""
import json
import logging
import os

import facebook
from google.oauth2 import service_account  # pylint: disable=no-name-in-module
from googleapiclient import discovery

import fest

FACEBOOK_PAGE_ID = os.environ["FACEBOOK_PAGE_ID"]
GOOGLE_CALENDAR_ID = os.environ["GOOGLE_CALENDAR_ID"]

# Get facebook/Google secrets
FACEBOOK_PAGE_TOKEN = os.environ["FACEBOOK_PAGE_TOKEN"]
GOOGLE_SERVICE_ACCOUNT = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"])
GOOGLE_CREDENTIALS = service_account.Credentials.from_service_account_info(
    GOOGLE_SERVICE_ACCOUNT
)

# Get facebook/Google clients
GRAPHAPI = facebook.GraphAPI(FACEBOOK_PAGE_TOKEN)
CALENDARAPI = discovery.build(
    "calendar",
    "v3",
    cache_discovery=False,
    credentials=GOOGLE_CREDENTIALS,
)

# Configure logging
logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s")


def main(page_id=None, cal_id=None, dryrun=False):
    """
    Heroku entrypoint.
    """
    page_id = page_id or FACEBOOK_PAGE_ID
    cal_id = cal_id or GOOGLE_CALENDAR_ID

    # Initialize facebook page & Google Calendar
    page = fest.FacebookPage(GRAPHAPI, page_id)
    gcal = fest.GoogleCalendar(CALENDARAPI, cal_id)
    page.logger.setLevel("INFO")
    gcal.logger.setLevel("INFO")

    # Sync
    sync = gcal.sync(page, time_filter="upcoming").execute(dryrun=dryrun)

    # Return created/updated/deleted objects
    return sync.responses


if __name__ == "__main__":
    print(json.dumps(main()))  # pragma: no cover
