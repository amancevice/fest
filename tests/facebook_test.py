from unittest import mock

from fest import facebook


def test_facebook_page_iter_events():
    mockapi = mock.MagicMock()
    mockapi.get_object.side_effect = [
        {
            "data": [{"id": "1"}, {"id": "2"}],
            "paging": {"cursors": {"after": "fizz"}},
        },
        {
            "data": [{"id": "3"}, {"id": "4"}],
        },
    ]
    page = facebook.FacebookPage(mockapi, "MyPage")
    ret = page.get_events().execute()
    exp = [{"id": "1"}, {"id": "2"}, {"id": "3"}, {"id": "4"}]
    assert ret == exp


def test_facebook_page_iter_objects():
    mockapi = mock.MagicMock()
    results = {str(x): {"id": str(x)} for x in range(0, 100)}
    mockapi.get_objects.side_effect = [
        {k: v for k, v in list(results.items())[:50]},
        {k: v for k, v in list(results.items())[50:]},
    ]
    page = facebook.FacebookPage(mockapi, "MyPage")
    ret = page.get_objects(list(results.keys())).execute()
    exp = list(results.values())
    assert ret == exp


def test_facebook_page_explode_event():
    ret = list(
        facebook.FacebookPage.explode_event(
            {
                "id": "1",
                "start_time": "2018-12-10T12:00:00-0500",
                "event_times": [
                    {
                        "id": "2",
                        "start_time": "2018-12-10T12:00:00-0500",
                        "end_time": "2018-12-10T13:00:00-0500",
                    },
                    {
                        "id": "3",
                        "start_time": "2018-12-11T12:00:00-0500",
                        "end_time": "2018-12-11T13:00:00-0500",
                    },
                ],
            },
            time_filter="past",
        )
    )
    exp = [
        {
            "id": "2",
            "start_time": "2018-12-10T12:00:00-0500",
            "end_time": "2018-12-10T13:00:00-0500",
        },
        {
            "id": "3",
            "start_time": "2018-12-11T12:00:00-0500",
            "end_time": "2018-12-11T13:00:00-0500",
        },
    ]
    assert ret == exp


def test_facebook_event_location_string():
    ret = facebook.FacebookPage.location_string(
        {
            "place": {
                "location": {
                    "city": "Cambridge",
                    "country": "United States",
                    "latitude": 42.36364,
                    "longitude": -71.103733,
                    "state": "MA",
                    "street": "45 Pearl St",
                    "zip": "02139",
                },
                "name": "Cambridge Public Library - Central Square Branch",
            }
        }
    )
    exp = (
        "Cambridge Public Library - Central Square Branch "
        "45 Pearl St Cambridge MA United States 02139"
    )
    assert ret == exp


def test_facebook_event_location_string_err():
    ret = facebook.FacebookPage.location_string(
        {"place": {"name": "Cambridge Public Library - Central Square Branch"}}
    )
    exp = "Cambridge Public Library - Central Square Branch"
    assert ret == exp


def test_facebook_page_to_google():
    event = {
        "description": "desc",
        "end_time": "2018-02-11T16:00:00-0500",
        "id": "1234567890",
        "name": "name",
        "place": {
            "name": "place",
        },
        "start_time": "2018-02-11T11:00:00-0500",
    }
    ret = facebook.FacebookPage(None, "MyPage").to_google(event)
    exp = {
        "description": "desc\n\nhttps://www.facebook.com/1234567890",
        "start": {"dateTime": "2018-02-11T11:00:00-05:00", "timeZone": "UTC-05:00"},
        "extendedProperties": {
            "private": {
                "facebookPageId": "MyPage",
                "facebookDigest": "ca00a6786b8bb6acd2488080d70ea861b0db84f3",
                "facebookId": "1234567890",
            }
        },
        "end": {"dateTime": "2018-02-11T16:00:00-05:00", "timeZone": "UTC-05:00"},
        "summary": "name",
        "location": "place",
    }
    assert ret == exp


def test_facebook_page_to_google_no_end():
    event = {
        "description": "desc",
        "id": "1234567890",
        "name": "name",
        "place": {
            "name": "place",
        },
        "start_time": "2018-02-11T11:00:00-0500",
    }
    ret = facebook.FacebookPage(None, "MyPage").to_google(event)
    exp = {
        "description": "desc\n\nhttps://www.facebook.com/1234567890",
        "start": {"dateTime": "2018-02-11T11:00:00-05:00", "timeZone": "UTC-05:00"},
        "extendedProperties": {
            "private": {
                "facebookPageId": "MyPage",
                "facebookDigest": "262e76ded1c9944e4c08d84939b5ef354b2574c7",
                "facebookId": "1234567890",
            }
        },
        "end": {"dateTime": "2018-02-11T12:00:00-05:00", "timeZone": "UTC-05:00"},
        "summary": "name",
        "location": "place",
    }
    assert ret == exp
