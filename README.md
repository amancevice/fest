# Facebook Event State Transfer

**THIS APP IS EXTREMELY ALPHA**

[![build](https://travis-ci.org/amancevice/fest.svg?branch=master)](https://travis-ci.org/amancevice/fest)
[![codecov](https://codecov.io/gh/amancevice/fest/branch/master/graph/badge.svg)](https://codecov.io/gh/amancevice/fest)
[![pypi](https://badge.fury.io/py/fest.svg)](https://badge.fury.io/py/fest)

Sync public facebook events to other services.

*Note, only Google Calendar is supported at the moment*

## Prerequisites

Before beginning, you will need to create and configure facebook and Google Cloud accounts:

* [Facebook Developer](./docs/facebook.md#facebook)
* [Google Cloud Service](./docs/google.md#google-cloud)

## Installation

Install `fest` using pip:

```bash
pip install fest
```

Or, use the provided `docker-compose` configuration to use the [fest CLI](./docs/cli.md#fest-cli) in a Docker container.

## Basic Use

The easiest way to manage access is to store your credentials for facebook/Google projects as environmental variables. See the above instructions on how to configure these variables.

For these examples the credentials will be explicitly passed.

### Getting Facebook Page Events

```python
import fest

# Connect to Graph API & get page
graph = fest.GraphAPI('<app_id>', '<app_secret>')
page = graph.get_page('<page_id_or_alias>')

# Get ALL events
events = page.get_events()  

# Get UPCOMING events
upcoming = page.get_events(time_filter='upcoming')
```

### Creating Google Calendar from Facebook Page

Using the service account described above, you can create a Google Calender from a facebook page:

```python
# Connect to Google Cloud
cloud = fest.CalendarAPI.from_credentials(
    scopes=['https://www.googleapis.com/auth/calendar'],
    service_type='service_account',
    private_key_id='<private_key_id>',
    private_key='<private_key>',
    client_email='<client_email>',
    client_id='<client_id>')

# Get facebook page
page = graph.get_page('<page_id_or_alias>')

# Create calendar
gcal = cloud.create_calendar(page, tz='America/New_York')
```

### Grant Ownership of the new Calendar

Because the service account is not a human, it may help to add a human owner to the calendar to manually manage other components of the calendar:

```python
gcal.add_owner('owner.email@gmail.com')
```

### Sync All Facebook Events

With the facebook page and Google Calendar in hand, synching all events is easy:

```python
gcal.sync_page(page, tz='America/New_York')
```

This will sync ALL events into the new calendar &mdash; regardless of prior state.

To clear a calendar:

```python
gcal.clear_events()
```

### Updates

Events written to the Google Calendar are tagged with their original facebook ID. You can use this value to filter out previously synced events:

```python
# Get upcoming facebook events
upcoming = page.get_events(time_filter='upcoming')

# Filter out events that have already been loaded
events = [x for x in events if gcal.get_facebook_event(x['id']) is None]
```

### Fest CLI

See [CLI documentation](./docs/cli#fest-cli)

## Deployment

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

Deploy this app to heroku and use the heroku scheduler to run the sync job on a cron.

Once the app is deployed, you will need to configure the environmental variables above. Use the heroku web console, or the terminal:

```bash
heroku config:set FACEBOOK_APP_ID='<facebook-app-id>'
heroku config:set FACEBOOK_APP_SECRET='<facebook-app-secret>'
heroku config:set FACEBOOK_PAGE_ID='<facebook-page-id-or-alias>'
heroku config:set GOOGLE_ACCOUNT_TYPE='service_account'
heroku config:set GOOGLE_CALENDAR_ID='<optional-google-calendar-id>'
heroku config:set GOOGLE_CLIENT_EMAIL='<google-service-client-email>'
heroku config:set GOOGLE_CLIENT_ID='<google-client-id>'
heroku config:set GOOGLE_PRIVATE_KEY='<google-private-key-multi-line-string'
heroku config:set GOOGLE_PRIVATE_KEY_ID='<google-private-key-id'
heroku config:set GOOGLE_SCOPE='https://www.googleapis.com/auth/calendar'
```

Finally, go into the heroku scheduler config and set the cron job to use the script:

```bash
python -m fest.main sync
```

## TODO

* Full test coverage
* Add iCalendar layer to translation
* Add Terraform modules to for AWS Lambda, &c.
