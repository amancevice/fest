from unittest import mock

import pytest

from fest import facebook
from fest import google


def test_google_page_iter_events():
    mockapi = mock.MagicMock()
    mockapi.events.return_value.list.return_value.execute.side_effect = [
        {
            "items": [{"id": "1"}, {"id": "2"}],
            "nextPageToken": "fizz",
        },
        {
            "items": [{"id": "3"}, {"id": "4"}],
        },
    ]
    gcal = google.GoogleCalendar(mockapi, "MyGCal")
    ret = gcal.get_events().filter(lambda x: x["id"] < "4").execute()
    exp = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
    assert ret == exp


def test_google_page_sync():
    mockf = mock.MagicMock()
    mockg = mock.MagicMock()

    fevents = [
        {
            "id": "1",
            "start_time": "2018-12-12T12:00:00-0500",
            "end_time": "2018-12-12T13:00:00-0500",
            "description": "some description 1",
            "name": "Event 1",
            "place": {
                "name": "Boston Public Library",
                "location": {
                    "city": "Boston",
                    "country": "United States",
                    "state": "MA",
                    "street": "700 Boylston St",
                    "zip": "02116",
                },
            },
        },
        {
            "id": "2",
            "start_time": "2018-12-13T12:00:00-0500",
            "end_time": "2018-12-13T13:00:00-0500",
            "description": "some description 2",
            "name": "Event 2",
            "place": {
                "name": "Boston Public Library",
                "location": {
                    "city": "Boston",
                    "country": "United States",
                    "state": "MA",
                    "street": "700 Boylston St",
                    "zip": "02116",
                },
            },
        },
        {
            "id": "3",
            "start_time": "2018-12-14T12:00:00-0500",
            "end_time": "2018-12-14T13:00:00-0500",
            "description": "some description 3",
            "name": "Event 3",
            "place": {
                "name": "Boston Public Library",
                "location": {
                    "city": "Boston",
                    "country": "United States",
                    "state": "MA",
                    "street": "700 Boylston St",
                    "zip": "02116",
                },
            },
        },
    ]
    gevents = [
        {
            "id": "1",
            "summary": "Event 1",
            "extendedProperties": {
                "private": {
                    "facebookId": "1",
                    "facebookPageId": "MyPage",
                    "facebookDigest": "c572922673ad8110b615238f8c48cd38ee156bdc",
                }
            },
        },
        {
            "id": "2",
            "summary": "Event 2",
            "extendedProperties": {
                "private": {
                    "facebookId": "2",
                    "facebookPageId": "MyPage",
                    "facebookDigest": "OUTDATED",
                }
            },
        },
        {
            "id": "4",
            "summary": "Event 4",
            "extendedProperties": {
                "private": {
                    "facebookId": "4",
                    "facebookPageId": "MyPage",
                    "facebookDigest": "",
                }
            },
        },
    ]
    mockf.get_object.side_effect = [{"data": fevents}]
    mockf.get_objects.side_effect = [{x["id"]: x for x in fevents}]
    mockg.events.return_value.list.return_value.execute.side_effect = [
        {"items": gevents}
    ]
    gcal = google.GoogleCalendar(mockg, "MyGCal")
    page = facebook.FacebookPage(mockf, "MyPage")
    gcal.sync(page, time_filter="upcoming").execute()
    mockg.events.return_value.insert.assert_called_once_with(
        calendarId="MyGCal",
        body={
            "summary": "Event 3",
            "description": "some description 3\n\nhttps://www.facebook.com/3",
            "location": "Boston Public Library "
            "700 Boylston St "
            "Boston MA United States 02116",
            "start": {
                "dateTime": "2018-12-14T12:00:00-05:00",
                "timeZone": "UTC-05:00",
            },
            "end": {
                "dateTime": "2018-12-14T13:00:00-05:00",
                "timeZone": "UTC-05:00",
            },
            "extendedProperties": {
                "private": {
                    "facebookDigest": "6a1960a370ba8f16031d729ebfdbccb1110b5fd7",
                    "facebookId": "3",
                    "facebookPageId": "MyPage",
                },
            },
        },
    )
    mockg.events.return_value.update.assert_called_once_with(
        calendarId="MyGCal",
        eventId="2",
        body={
            "summary": "Event 2",
            "description": "some description 2\n\nhttps://www.facebook.com/2",
            "location": "Boston Public Library "
            "700 Boylston St "
            "Boston MA United States 02116",
            "start": {
                "dateTime": "2018-12-13T12:00:00-05:00",
                "timeZone": "UTC-05:00",
            },
            "end": {
                "dateTime": "2018-12-13T13:00:00-05:00",
                "timeZone": "UTC-05:00",
            },
            "extendedProperties": {
                "private": {
                    "facebookDigest": "505f25b09ebde5a6e2587849d364d118ad740454",
                    "facebookId": "2",
                    "facebookPageId": "MyPage",
                },
            },
        },
    )
    mockg.events.return_value.delete.assert_called_once_with(
        calendarId="MyGCal",
        eventId="4",
    )


@mock.patch("fest.utils.digest")
def test_google_page_sync_multibatch(mock_digest):
    mock_digest.return_value = "<digest>"
    mockf = mock.MagicMock()
    mockg = mock.MagicMock()
    items = range(0, 99)
    mockf.get_object.side_effect = mockf.get_objects.side_effect = [
        {
            "data": [
                {
                    "id": str(x),
                    "start_time": "2018-12-12T12:00:00-0500",
                    "end_time": "2018-12-12T13:00:00-0500",
                    "description": f"some description {x}",
                    "name": f"Event {x}",
                    "place": {
                        "name": "Boston Public Library",
                        "location": {
                            "city": "Boston",
                            "country": "United States",
                            "state": "MA",
                            "street": "700 Boylston St",
                            "zip": "02116",
                        },
                    },
                }
                for x in items
            ],
        },
    ]
    mockg.events.return_value.list.return_value.execute.side_effect = [
        {
            "items": [],
        },
    ]
    gcal = google.GoogleCalendar(mockg, "MyGCal")
    page = facebook.FacebookPage(mockf, "MyPage")
    gcal.sync(page, time_filter="upcoming").execute()
    mockg.events.return_value.insert.assert_has_calls(
        [
            mock.call(
                calendarId="MyGCal",
                body={
                    "summary": f"Event {x}",
                    "description": f"some description {x}\n\nhttps://www.facebook.com/{x}",
                    "location": "Boston Public Library "
                    "700 Boylston St "
                    "Boston MA United States 02116",
                    "start": {
                        "dateTime": "2018-12-12T12:00:00-05:00",
                        "timeZone": "UTC-05:00",
                    },
                    "end": {
                        "dateTime": "2018-12-12T13:00:00-05:00",
                        "timeZone": "UTC-05:00",
                    },
                    "extendedProperties": {
                        "private": {
                            "facebookDigest": "<digest>",
                            "facebookId": str(x),
                            "facebookPageId": "MyPage",
                        },
                    },
                },
            )
            for x in items
        ]
    )
    mockg.new_batch_http_request.return_value.execute.assert_has_calls(
        [
            mock.call(),
            mock.call(),
        ]
    )


def test_google_page_sync_no_op():
    mockf = mock.MagicMock()
    mockg = mock.MagicMock()

    mockf.get_object.side_effect = mockf.get_objects.side_effect = [
        {
            "data": [],
        },
    ]
    gcal = google.GoogleCalendar(mockg, "MyGCal")
    page = facebook.FacebookPage(mockf, "MyPage")
    sync = gcal.sync(page, time_filter="upcoming")
    sync.filter(lambda x: x).execute()
    mockg.new_batch_http_request.assert_not_called()


def test_callback():
    mockapi = mock.MagicMock()
    gcal = google.GoogleCalendar(mockapi, "MyGCal")
    page = facebook.FacebookPage(mockapi, "MyPage")
    sync = gcal.sync(page, time_filter="upcoming")
    callback = sync.callbackgen("POST")
    res = {
        "extendedProperties": {
            "private": {"facebookId": "1"},
        },
    }
    callback("id", res, None)
    assert sync.responses["POST"] == {"1": res}


def test_callback_err():
    mockapi = mock.MagicMock()
    gcal = google.GoogleCalendar(mockapi, "MyGCal")
    page = facebook.FacebookPage(mockapi, "MyPage")
    sync = gcal.sync(page, time_filter="upcoming")
    callback = sync.callbackgen([])
    with pytest.raises(ValueError):
        callback("id", "response", ValueError)
