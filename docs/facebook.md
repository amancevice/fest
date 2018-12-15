# Facebook

This guide will walk you through creating a facebook app & obtaining its ID and secret.

*Note that there is an assumption here that the facebook page you are attempting to access is public.*

## Create Developer Account

Create a facebook developer account at [developers.facebook.com](https://developers.facebook.com).

## Create App

In the top-right corner click the **My Apps** dropdown and select **Add a new app**.

Fill in a name for the app and click **Create App ID**.

## Get Page Token

Once your app has been created and you have admin rights to your facebook page you will need to create a [page token](https://developers.facebook.com/docs/facebook-login/access-tokens/#pagetokens). You can do this from the [Graph API Explorer](https://developers.facebook.com/tools/explorer/).

Select your app from the top-leftmost dropdown, then select your page from the "Get Token" dropdown. Press the blue button with the letter `i` to the left of the token to open the "Access Token Info" tooltip. Click the "Open in Access Token Tool" button to open the token tool window. Click "Extend Access Token" to get a long-lived token.

## Use token

Create an instance of the Graph API client using this token:

```python
import facebook

graphapi = facebook.GraphAPI('<your-token>')
```

Use this client as an input to `fest.FacebookPage`:

```python
import fest

page = fest.FacebookPage(graphapi, 'MyPageID')
```
