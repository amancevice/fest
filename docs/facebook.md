# Facebook

This guide will walk you through creating a facebook app & obtaining its ID and secret.

*Note that there is an assumption here that the facebook data you are attempting to access is public.*

## Create Developer Account

Create a facebook developer account at [developers.facebook.com](https://developers.facebook.com).

## Create App

In the top-right corner click the **My Apps** dropdown and select **Add a new app**.

Fill in a name for the app and click **Create App ID**.

## Get Access Keys

Once your app has been created and you are directed to your app's homepage, select **Dashboard** from the left menu. Copy the **App ID** and **App Secret** values.

The `fest` tool makes use of environmental variables to manage access to facebook's Graph API. This is not required but certainly makes it easier to deploy the app in service like heroku.

The following variables can be exported using values from the dashboard:

```bash
export FACEBOOK_APP_ID='<facebook-app-id>'
export FACEBOOK_APP_SECRET='<facebook-app-secret>'
```

### Additional Settings

You may also wish to export the following variable:

```bash
export FACEBOOK_PAGE_ID='<facebook-page-id-or-alias>'
```

This variable will enable your app to bind to a single facebook page.
