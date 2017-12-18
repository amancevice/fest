# Facebook Event State Transfer

**THIS APP IS EXTREMELY ALPHA**

[![build](https://travis-ci.org/amancevice/fest.svg?branch=master)](https://travis-ci.org/amancevice/fest)
[![codecov](https://codecov.io/gh/amancevice/fest/branch/master/graph/badge.svg)](https://codecov.io/gh/amancevice/fest)

Sync facebook events to other services.

*Note, only Google Calendar is supported at the moment*

## Installation

Install `fest` as a pip, or use the provided `docker-compose` configuration.

```bash
pip install fest

# or

docker-compose pull fest
```

## Prerequisites

Before you can access facebook's Graph API you will need to set up a [developer](https://developers.facebook.com) account with facebook.

You will also need to set up an account with Google's [Cloud Platform](https://console.developers.google.com).

### Create a Facebook App

Create a facebook app and take note of its `App ID` and `App Secret` values. You will need them later.

### Create a Google Project

The Google project is more complicated than the facebook app because there are a few routes you could take. This guide assumes you will create a new calendar from scratch using a service account. The calendar can be shared with your personal Google account in order to have manual override control.

First, you will need to create a new project in the developer console and give it access to the Google Calendar API.

Once the project is given access to the Calendar API, you will need to create credentials. From the `credentials` tab click the "Create credentials" dropdown and select "Service account key". Give the account a name and a role of "Owner". Use JSON for the key type.

After the credentials are created download the client secret JSON file and store it in a safe place.

### Gather Keys

The easiest way to manage access is to store your credentials for facebook/Google projects as environmental variables.

Example:

```bash
# facebook
export FACEBOOK_APP_ID='<facebook-app-id>'
export FACEBOOK_APP_SECRET='<facebook-app-secret>'
export FACEBOOK_PAGE_ID='<facebook-page-id-or-alias>'

# Google
export GOOGLE_ACCOUNT_TYPE='service_account'
export GOOGLE_CALENDAR_ID='<google-calendar-id>'
export GOOGLE_CLIENT_EMAIL='<google-service-client-email>'
export GOOGLE_CLIENT_ID='<google-client-id>'
export GOOGLE_PRIVATE_KEY='<google-private-key-multi-line-string'
export GOOGLE_PRIVATE_KEY_ID='<google-private-key-id'
export GOOGLE_SCOPE='https://www.googleapis.com/auth/calendar'
```

## Create Calendar

If you need to create a calendar into which facebook events will be synced, you can use the `fest` CLI. You will need to supply the timezone of the calendar:

```bash
fest create --tz America/New_York
```

Save the output ID from this process and add it to your environment as `GOOGLE_CALENDAR_ID`.

## Sync Calendar

If this is your first time syncing, you can use the `--sync-all` flag to sync the entire calendar.

Omitting this flag only syncs 'upcoming' events from facebook.

```bash
fest sync --sync-all
```

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
