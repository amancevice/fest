import os
from unittest import mock

os.environ["FACEBOOK_PAGE_ID"] = "MyPage"
os.environ["GOOGLE_CALENDAR_ID"] = "id@group.calendar.google.com"
os.environ["FACEBOOK_PAGE_TOKEN"] = "token"
os.environ["GOOGLE_SERVICE_ACCOUNT"] = "{}"

with mock.patch(
    "google.oauth2.service_account.Credentials." "from_service_account_info"
):
    from fest import heroku


@mock.patch("fest.GoogleCalendar.sync")
def test_main(mock_sync):
    heroku.main()
    mock_sync.assert_called_once()
    mock_sync.return_value.execute.assert_called_once_with(dryrun=False)
