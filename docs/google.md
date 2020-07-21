# Google

This guide will walk you through creating a Google Project & service account that will be used to write to a Google Calendar.

## Creating a Project

Use the [new project wizard](https://console.developers.google.com/start/api?id=calendar) provided by Google to create or select a project in the Google Developers Console and automatically turn on the API. Click **Continue**, then **Go to credentials**.

## Add a Service Account

On the **Add credentials to your project page**, click the **Cancel** button.

Click the **Create credentials** dropdown on the subsequent screen and select **Service account key**.

Under the **Service account** dropdown, select **New service account**. Give the service account and name and a role of **Project -> Viewer**.

Select `JSON` as the **Key type** and click **Create**.

The `client_secret.json` file will automatically be downloaded to your computer. **Do not lose this file** as it will not be regenerated.

## Use Service Account

After downloading the `client_secret.json` credentials file, put it in a safe place on your file system and set the value of the environmental variable `GOOGLE_APPLICATION_CREDENTIALS`, as specified by the [docs](https://cloud.google.com/docs/authentication/getting-started#setting_the_environment_variable).

Create an instance of the Google Calendar API client:

```python
from googleapiclient import discovery

calendarapi = discovery.build('calendar', 'v3', cache_discovery=False)
```

Use this client as an input to `fest.GoogleCalendar`:

```python
import fest

gcal = fest.GoogleCalendar(calendarapi, '<google-calendar-id>')
```
