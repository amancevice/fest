# Google Cloud

This guide will walk you through creating a Google Project & service account that will be used to write to a Google Calendar.

## Creating a Project

Use the [new project wizard](https://console.developers.google.com/start/api?id=calendar) provided by Google to create or select a project in the Google Developers Console and automatically turn on the API. Click **Continue**, then **Go to credentials**.

## Add a Service Account

On the **Add credentials to your project page**, click the **Cancel** button.

Click the **Create credentials** dropdown on the subsequent screen and select **Service account key**.

Under the **Service account** dropdown, select **New service account**. Give the service account and name and a role of **Project -> Viewer**.

Select `JSON` as the **Key type** and click **Create**.

The `client_secret.json` file will automatically be downloaded to your computer. **Do not lose this file** as it will not be regenerated.

## Get Access Keys

The `fest` tool makes use of environmental variables to manage access to Google Cloud services. This is not required but certainly makes it easier to deploy the app in service like heroku.

The following variables can be exported using values from `client_secret.json`

```bash
export GOOGLE_CLIENT_EMAIL='<google-service-client-email>'
export GOOGLE_CLIENT_ID='<google-client-id>'
export GOOGLE_PRIVATE_KEY='<google-private-key-multi-line-string'
export GOOGLE_PRIVATE_KEY_ID='<google-private-key-id'
export GOOGLE_TOKEN_URI='https://accounts.google.com/o/oauth2/token'
```

## Additional Settings

You may also wish to export the following variables:

```bash
export GOOGLE_SCOPE='https://www.googleapis.com/auth/calendar'
```

These variables will enable your app to bind to the correct Google Calendar and give it permission to read/write events.
