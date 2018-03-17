# Facebook Event State Transfer

**THIS APP IS EXTREMELY ALPHA**

[![build](https://travis-ci.org/amancevice/fest.svg?branch=master)](https://travis-ci.org/amancevice/fest)
[![codecov](https://codecov.io/gh/amancevice/fest/branch/master/graph/badge.svg)](https://codecov.io/gh/amancevice/fest)
[![pypi](https://badge.fury.io/py/fest.svg)](https://badge.fury.io/py/fest)

Sync public facebook events to other services.

**Supported Services**

* Google Calendar
* The Events Calendar plugin for WordPress

## Prerequisites

Before beginning, you will need to create and configure a [facebook app](./docs/facebook.md#facebook) to acquire the access keys to use Graph API.

For Google, you will need to set up a [Google Cloud Service](./docs/google.md#google-cloud) account.

For WordPress, you will need to install the [Application Passwords](https://wordpress.org/plugins/application-passwords/) and [The Events Calendar](https://wordpress.org/plugins/event-tickets/) plugins. Read the [WordPress](./docs/wordpress.md#wordpress) docs for more information.

## Installation

Install `fest` using pip:

```bash
pip install fest
```

Use extras to install support for supported sync endpoint(s):

```bash
pip install fest[google]     # Installs Google pips
pip install fest[wordpress]  # Installs WordPress pips
pip install fest[all]        # Installs all pips
```

### Basic Use

Get facebook events

```python
import fest.graph

# Connect to Graph API & get page
graph = fest.graph.GraphAPI.from_credentials(
    app_id='<app_id>',
    app_secret='<app_secret>')
page = graph.get_page('<page_id_or_alias>')

# Get upcoming events
upcoming = page.get_events(time_filter='upcoming')

# Iterate over all events
for event in page.iter_events():
    print(event)
```

Sync to Google

```python
import fest.cloud

# Connect to Google Cloud
cloud = fest.cloud.CalendarAPI.from_credentials(
    scopes=['https://www.googleapis.com/auth/calendar'],
    service_type='service_account',
    private_key_id='<private_key_id>',
    private_key='<private_key>',
    client_email='<client_email>',
    client_id='<client_id>')

# Get Google Calendar
gcal = cloud.get_calendar('<google-calendar-id>')

# Sync events
gcal.sync_events({'upcoming': upcoming})
```

Sync to The Events Calendar

```python
import fest.tribe

# Connect to WordPress/Tribe
tribe = fest.tribe.TribeAPI.from_credentials(
    wordpress_endpoint='<wordpress-endpoint>',
    wordpress_username='<wordpress-username>',
    wordpress_app_password='<wordpress-app-password>',
    tribe_endpoint='<tribe-rest-api-endpoint>')

# Sync events
tribe.sync_events({'upcoming': upcoming})
```

## Deployment

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

Deploy this app to heroku and use the heroku scheduler to run the sync job on a cron.

Once the app is deployed, you will need to configure the environmental variables above. Use the heroku web console, or the terminal.

For facebook:

```bash
heroku config:set FACEBOOK_APP_ID='<facebook-app-id>'
heroku config:set FACEBOOK_APP_SECRET='<facebook-app-secret>'
heroku config:set FACEBOOK_PAGE_NAME='<facebook-page-id-or-alias>'
```

For Google:

```bash
heroku config:set GOOGLE_ACCOUNT_TYPE='service_account'
heroku config:set GOOGLE_CALENDAR_ID='<optional-google-calendar-id>'
heroku config:set GOOGLE_CLIENT_EMAIL='<google-service-client-email>'
heroku config:set GOOGLE_CLIENT_ID='<google-client-id>'
heroku config:set GOOGLE_PRIVATE_KEY='<google-private-key-multi-line-string'
heroku config:set GOOGLE_PRIVATE_KEY_ID='<google-private-key-id'
heroku config:set GOOGLE_SCOPE='https://www.googleapis.com/auth/calendar'
```

For WordPress:

```bash
heroku config:set WORDPRESS_ENDPOINT='<wordpress-host>/xmlrpc.php'
heroku config:set WORDPRESS_USERNAME='<wordpress-user>'
heroku config:set WORDPRESS_APP_PASSWORD='<wordpress-app-password>'
```

For The Events Calendar Plugin:

```bash
heroku config:set TRIBE_ENDPOINT='<wordpress-host>/wp-json/tribe/events/v1'
```

If your event posts have custom fields they can be configured using ENV variables where the variable is prefixed with `WP_CUSTOM_FIELD_`.

Ex:

```bash
WP_CUSTOM_FIELD_FIZZ='buzz'  # {'key': 'fizz', 'value': 'buzz'}
WP_CUSTOM_FIELD_JAZZ='funk'  # {'key': 'jazz', 'value': 'funk'}
```

## TODO

* Full test coverage
* Add iCalendar layer to translation
* Add Terraform modules to for AWS Lambda, &c.
