# Facebook Event State Transfer

[![build](https://travis-ci.org/amancevice/fest.svg?branch=master)](https://travis-ci.org/amancevice/fest)
[![codecov](https://codecov.io/gh/amancevice/fest/branch/master/graph/badge.svg)](https://codecov.io/gh/amancevice/fest)
[![pypi](https://badge.fury.io/py/fest.svg)](https://badge.fury.io/py/fest)

Sync public facebook events to other services.

**Supported Services**

* Google Calendar
* The Events Calendar plugin for WordPress
* Slack

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
    client_id='<client_id>',
    token_uri='https://accounts.google.com/o/oauth2/token')

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

## TODO

* Full test coverage
* Add iCalendar layer to translation
* Add Terraform modules to for AWS Lambda, &c.
