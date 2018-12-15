# Facebook Event State Transfer

[![build](https://travis-ci.org/amancevice/fest.svg?branch=master)](https://travis-ci.org/amancevice/fest)
[![codecov](https://codecov.io/gh/amancevice/fest/branch/master/graph/badge.svg)](https://codecov.io/gh/amancevice/fest)
[![pypi](https://badge.fury.io/py/fest.svg)](https://badge.fury.io/py/fest)

Sync public facebook page events to Google Calendar.

## Prerequisites

Before beginning, you will need to create and configure a [facebook app](./docs/facebook.md#facebook) to acquire the access keys to use Graph API.

For Google, you will need to set up a [service account](./docs/google.md#google) for to authenticate with Google APIs.

## Installation

Install `fest` using pip:

```bash
pip install fest
```

### Basic Use

Use clients for facebook's Graph API and Google's Calendar API to create `FacebookPage` and `GoogelCalendar` objects, then synchronize:

```python
import facebook
from googleapiclient import discovery

import fest

# Connect to Graph API & Calendar API
graphapi = facebook.GraphAPI('<facebook-page-token>')
calendarapi = discovery.build('calendar', 'v3', cache_discovery=False)

# Get Page/Calendar objects
page = fest.FacebookPage(graphapi, '<facebook-page-name-or-id>')
gcal = fest.GoogleCalendar(calendarapi, '<google-calendar-id>')

# Sync Calendar <= Page
req = gcal.sync(page, time_filter='upcoming')
res = req.execute()
```

### Deployment

A [terraform module](https://github.com/amancevice/terraform-aws-facebook-gcal-sync) module is provided to deploy this tool as a Lambda function on AWS and invoke it on a cron using CloudWatch.
