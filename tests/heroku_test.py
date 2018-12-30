from unittest import mock

from fest import heroku


@mock.patch('fest.GoogleCalendar.sync')
def test_main(mock_sync):
    heroku.main()
    mock_sync.assert_called_once()
    mock_sync.return_value.execute.assert_called_once_with(dryrun=False)
