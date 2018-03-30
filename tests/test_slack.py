import fest.slack
import mock


@mock.patch('fest.slack.SlackAPI.from_credentials')
def test_slack_api_from_env(mock_creds):
    slack = fest.slack.SlackAPI.from_env()
    mock_creds.assert_called_once_with()


def test_slack_api_from_credentials():
    slack = fest.slack.SlackAPI.from_credentials('TOKEN')
    assert slack.service.token == 'TOKEN'


def test_slack_api_post_message():
    slack = fest.slack.SlackAPI(mock.MagicMock())
    slack.post_message({'text': 'TEXT'}, 'CHANNEL')
    slack.service.api_call.assert_called_once_with(
        'chat.postMessage', channel='CHANNEL', text='TEXT')


def test_slack_message_from_google_no_events():
    gcal = mock.MagicMock()
    gcal.url = 'https://example.com'
    message = fest.slack.SlackMessage.from_google(gcal)
    kwargs = {
        "attachments": [
            {
                "actions": [
                    {
                        "name": "google",
                        "text": "Google",
                        "type": "button"
                    },
                    {
                        "name": "icalendar",
                        "text": "iCalendar",
                        "type": "button"
                    },
                    {
                        "name": "not_sure",
                        "text": "I'm not sure",
                        "type": "button"
                    }
                ],
                "fallback": "Unable to display the subscription links",
                "text": u"Choose \u2039\u2039 Google \u203a\u203a if you use "
                        u"already have a Google Calendar\nChoose \u2039\u2039 "
                        u"iCalendar \u203a\u203a if you use something else",
                "title": "Subscribe to this <https://example.com|Calendar>!"
            }
        ],
        "text": u"There are no events today\n_Subscribing via the "
                u"\u2039\u2039 Google \u203a\u203a button will only work "
                u"from a computer!_"
    }
    assert message == fest.slack.SlackMessage(mock.MagicMock(), **kwargs)


def test_slack_message_from_google_one_event():
    gcal = mock.MagicMock()
    gcal.url = 'https://example.com'
    gcal.get_today.return_value = [
        {
            "summary": "Event Title",
            "htmlLink": "https://www.google.com/calendar/event?eid=eid",
            "location": "Somewhere",
            "start": {
                "dateTime": "2018-03-30T19:00:00-07:00",
            },
            "end": {
                "dateTime": "2018-03-30T21:00:00-07:00",
            },
        }
    ]
    message = fest.slack.SlackMessage.from_google(gcal)
    kwargs = {
        "attachments": [
            {
                "fallback": "Unable to display event",
                "text": "Mar 30 from 7:00 PM to 9:00 PM at "
                        "<https://maps.google.com/maps?q=Somewhere|Somewhere>",
                "title": "<https://www.google.com/calendar/event?eid=eid|"
                         "Event Title>"
            },
            {
                "actions": [
                    {
                        "name": "google",
                        "text": "Google",
                        "type": "button"
                    },
                    {
                        "name": "icalendar",
                        "text": "iCalendar",
                        "type": "button"
                    },
                    {
                        "name": "not_sure",
                        "text": "I'm not sure",
                        "type": "button"
                    }
                ],
                "fallback": "Unable to display the subscription links",
                "text": u"Choose \u2039\u2039 Google \u203a\u203a if you use "
                        u"already have a Google Calendar\nChoose \u2039\u2039 "
                        u"iCalendar \u203a\u203a if you use something else",
                "title": "Subscribe to this <https://example.com|Calendar>!"
            }
        ],
        "text": u"There is *1* event today\n_Subscribing via the "
                u"\u2039\u2039 Google \u203a\u203a button will only work "
                u"from a computer!_"
    }
    assert message == fest.slack.SlackMessage(mock.MagicMock(), **kwargs)


def test_slack_message_from_google_one_event_multiday():
    gcal = mock.MagicMock()
    gcal.url = 'https://example.com'
    gcal.get_today.return_value = [
        {
            "summary": "Event Title",
            "htmlLink": "https://www.google.com/calendar/event?eid=eid",
            "location": "Somewhere",
            "start": {
                "dateTime": "2018-03-30T19:00:00-07:00",
            },
            "end": {
                "dateTime": "2018-03-31T21:00:00-07:00",
            },
        }
    ]
    message = fest.slack.SlackMessage.from_google(gcal)
    kwargs = {
        "attachments": [
            {
                "fallback": "Unable to display event",
                "text": "Mar 30 through Mar 31 at "
                        "<https://maps.google.com/maps?q=Somewhere|Somewhere>",
                "title": "<https://www.google.com/calendar/event?eid=eid|"
                         "Event Title>"
            },
            {
                "actions": [
                    {
                        "name": "google",
                        "text": "Google",
                        "type": "button"
                    },
                    {
                        "name": "icalendar",
                        "text": "iCalendar",
                        "type": "button"
                    },
                    {
                        "name": "not_sure",
                        "text": "I'm not sure",
                        "type": "button"
                    }
                ],
                "fallback": "Unable to display the subscription links",
                "text": u"Choose \u2039\u2039 Google \u203a\u203a if you use "
                        u"already have a Google Calendar\nChoose \u2039\u2039 "
                        u"iCalendar \u203a\u203a if you use something else",
                "title": "Subscribe to this <https://example.com|Calendar>!"
            }
        ],
        "text": u"There is *1* event today\n_Subscribing via the "
                u"\u2039\u2039 Google \u203a\u203a button will only work "
                u"from a computer!_"
    }
    assert message == fest.slack.SlackMessage(mock.MagicMock(), **kwargs)


def test_slack_message_from_google_two_events():
    gcal = mock.MagicMock()
    gcal.url = 'https://example.com'
    gcal.get_today.return_value = [
        {
            "summary": "Event Title",
            "htmlLink": "https://www.google.com/calendar/event?eid=eid",
            "location": "Somewhere",
            "start": {
                "dateTime": "2018-03-30T19:00:00-07:00",
            },
            "end": {
                "dateTime": "2018-03-30T21:00:00-07:00",
            },
        },
        {
            "summary": "Event Title",
            "htmlLink": "https://www.google.com/calendar/event?eid=eid",
            "location": "Somewhere",
            "start": {
                "dateTime": "2018-03-30T19:00:00-07:00",
            },
            "end": {
                "dateTime": "2018-03-30T21:00:00-07:00",
            },
        }
    ]
    message = fest.slack.SlackMessage.from_google(gcal)
    kwargs = {
        "attachments": [
            {
                "fallback": "Unable to display event",
                "text": "Mar 30 from 7:00 PM to 9:00 PM at "
                        "<https://maps.google.com/maps?q=Somewhere|Somewhere>",
                "title": "<https://www.google.com/calendar/event?eid=eid|"
                         "Event Title>"
            },
            {
                "fallback": "Unable to display event",
                "text": "Mar 30 from 7:00 PM to 9:00 PM at "
                        "<https://maps.google.com/maps?q=Somewhere|Somewhere>",
                "title": "<https://www.google.com/calendar/event?eid=eid|"
                         "Event Title>"
            },
            {
                "actions": [
                    {
                        "name": "google",
                        "text": "Google",
                        "type": "button"
                    },
                    {
                        "name": "icalendar",
                        "text": "iCalendar",
                        "type": "button"
                    },
                    {
                        "name": "not_sure",
                        "text": "I'm not sure",
                        "type": "button"
                    }
                ],
                "fallback": "Unable to display the subscription links",
                "text": u"Choose \u2039\u2039 Google \u203a\u203a if you use "
                        u"already have a Google Calendar\nChoose \u2039\u2039 "
                        u"iCalendar \u203a\u203a if you use something else",
                "title": "Subscribe to this <https://example.com|Calendar>!"
            }
        ],
        "text": u"There are *2* events today\n_Subscribing via the "
                u"\u2039\u2039 Google \u203a\u203a button will only work "
                u"from a computer!_"
    }
    assert message == fest.slack.SlackMessage(mock.MagicMock(), **kwargs)


def test_slack_attachment_from_google():
    pass


def test_slack_subattachment_from_google():
    gcal = mock.MagicMock()
    gcal.url = 'https://example.com'
    message = fest.slack.SlackSubAttachment.from_google(gcal)
    kwargs = {
        "actions": [
            {
                "name": "google",
                "text": "Google",
                "type": "button"
            },
            {
                "name": "icalendar",
                "text": "iCalendar",
                "type": "button"
            },
            {
                "name": "not_sure",
                "text": "I'm not sure",
                "type": "button"
            }
        ],
        "fallback": "Unable to display the subscription links",
        "text": u"Choose \u2039\u2039 Google \u203a\u203a if you use "
                u"already have a Google Calendar\nChoose \u2039\u2039 "
                u"iCalendar \u203a\u203a if you use something else",
        "title": "Subscribe to this <https://example.com|Calendar>!"
    }
    assert message == fest.slack.SlackSubAttachment(mock.MagicMock(), **kwargs)


def test_slack_subattachment_from_google_no_url():
    gcal = mock.MagicMock()
    gcal.url = None
    message = fest.slack.SlackSubAttachment.from_google(gcal)
    kwargs = {
        "actions": [
            {
                "name": "google",
                "text": "Google",
                "type": "button"
            },
            {
                "name": "icalendar",
                "text": "iCalendar",
                "type": "button"
            },
            {
                "name": "not_sure",
                "text": "I'm not sure",
                "type": "button"
            }
        ],
        "fallback": "Unable to display the subscription links",
        "text": u"Choose \u2039\u2039 Google \u203a\u203a if you use "
                u"already have a Google Calendar\nChoose \u2039\u2039 "
                u"iCalendar \u203a\u203a if you use something else",
        "title": "Subscribe to this Calendar!"
    }
    assert message == fest.slack.SlackSubAttachment(mock.MagicMock(), **kwargs)
