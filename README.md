# Facebook Event State Transfer

[![Build Status](https://travis-ci.com/amancevice/fest.svg?branch=master)](https://travis-ci.com/amancevice/fest)
[![PyPI Version](https://badge.fury.io/py/fest.svg)](https://badge.fury.io/py/fest)
[![Test Coverage](https://api.codeclimate.com/v1/badges/d0ba2f4ce151723edcc1/test_coverage)](https://codeclimate.com/github/amancevice/fest/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/d0ba2f4ce151723edcc1/maintainability)](https://codeclimate.com/github/amancevice/fest/maintainability)

Sync public facebook page events to Google Calendar.

## Prerequisites

Before beginning you will need to create and configure a [facebook app](./docs/facebook.md#facebook) and use it to acquire a page access token for Graph API.

You will also need to set up a Google [service account](./docs/google.md#google) to acquire a credentials file to authenticate with Google APIs.

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

## Deployment

Several methods of deployment are provided.

### AWS

A pair of [terraform](https://github.com/amancevice/terraform-aws-facebook-gcal-sync) [modules](https://github.com/amancevice/terraform-aws-facebook-gcal-sync-secrets) module are provided to deploy this tool as a Lambda function on AWS and invoke it on a cron using CloudWatch.

```hcl
module secrets {
  source                  = "amancevice/facebook-gcal-sync-secrets/aws"
  facebook_page_token     = "<your-page-access-token>"
  facebook_secret_name    = "facebook/MyPage"
  google_secret_name      = "google/MySvcAcct"
  google_credentials_file = "<path-to-credentials-JSON-file>"
}

module facebook_gcal_sync {
  source               = "amancevice/facebook-gcal-sync/aws"
  facebook_page_id     = "<facebook-page-id>"
  facebook_secret_name = "${module.secrets.facebook_secret_name}"
  google_calendar_id   = "<google-calendar-id>"
  google_secret_name   = "${module.secrets.google_secret_name}"
}
```

### Heroku

A [terraform module](https://github.com/amancevice/terraform-heroku-facebook-gcal-sync) module is provided to deploy this tool as a Heroku application.

```hcl
module facebook_gcal_sync {
  source                  = "amancevice/facebook-gcal-sync/heroku"
  app_name                = "<unique-app-name"
  facebook_page_id        = "<facebook-page-id>"
  google_calendar_id      = "<google-calendar-id>"
  google_credentials_file = "<path-to-google-service-credentials>"
  facebook_page_token     = "<facebook-page-access-token>"
}
```


Alternatively, deploy with one click:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
