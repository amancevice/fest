# Facebook Event State Transfer

![pypi](https://img.shields.io/pypi/v/fest?color=yellow&logo=python&logoColor=eee&style=flat-square)
![python](https://img.shields.io/pypi/pyversions/fest?logo=python&logoColor=eee&style=flat-square)
[![pytest](https://img.shields.io/github/workflow/status/amancevice/fest/pytest?logo=github&style=flat-square)](https://github.com/amancevice/fest/actions)
[![coverage](https://img.shields.io/codeclimate/coverage/amancevice/fest?logo=code-climate&style=flat-square)](https://codeclimate.com/github/amancevice/fest/test_coverage)
[![maintainability](https://img.shields.io/codeclimate/maintainability/amancevice/fest?logo=code-climate&style=flat-square)](https://codeclimate.com/github/amancevice/fest/maintainability)

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
# WARNING Be extremely cautious when using secret versions in terraform
# NEVER store secrets in plaintext and encrypt your remote state
# I recommend applying the secret versions in a separate workspace with no remote backend,
# or curating them manually in the console or AWS CLI.
resource "aws_secretsmanager_secret_version" "facebook" {
  secret_id     = module.facebook_gcal_sync.facebook_secret.id
  secret_string = "my-facebook-app-token"
}

resource "aws_secretsmanager_secret_version" "google" {
  secret_id     = module.facebook_gcal_sync.google_secret.id
  secret_string = file("./path/to/my/svc/acct/creds.json")
}

module facebook_gcal_sync {
  source  = "amancevice/facebook-gcal-sync/aws"
  version = "~> 1.0"

  facebook_page_id     = "<facebook-page-id>"
  facebook_secret_name = "facebook/my-app"
  google_calendar_id   = "<google-calendar-id>"
  google_secret_name   = "google/my-svc-acct"
}
```

### Heroku

A [terraform module](https://github.com/amancevice/terraform-heroku-facebook-gcal-sync) module is provided to deploy this tool as a Heroku application.

```hcl
module facebook_gcal_sync {
  source                  = "amancevice/facebook-gcal-sync/heroku"
  app_name                = "<unique-app-name>"
  facebook_page_id        = "<facebook-page-id>"
  google_calendar_id      = "<google-calendar-id>"
  google_credentials_file = "<path-to-google-service-credentials>"
  facebook_page_token     = "<facebook-page-access-token>"
}
```


Alternatively, deploy with one click:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
