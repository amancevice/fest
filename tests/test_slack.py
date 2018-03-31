import fest.slack
import mock


@mock.patch('fest.slack.SlackAPI.from_credentials')
def test_slack_api_from_env(mock_creds):
    slack = fest.slack.SlackAPI.from_env()
    mock_creds.assert_called_once_with()


def test_slack_api_from_credentials():
    slack = fest.slack.SlackAPI.from_credentials('TOKEN')
    assert slack.service.token == 'TOKEN'


def test_slack_api_get_channel():
    slack = fest.slack.SlackAPI(mock.MagicMock())
    ret = slack.get_channel('CHANNEL')
    exp = fest.slack.SlackChannel(slack, id='CHANNEL')
    assert ret == exp


def test_slack_api_post_message():
    slack = fest.slack.SlackAPI(mock.MagicMock())
    slack.post_message('CHANNEL', {'text': 'TEXT'})
    slack.service.api_call.assert_called_once_with(
        'chat.postMessage', 'CHANNEL', text='TEXT')


def test_slack_api_post_message_dryrun():
    slack = fest.slack.SlackAPI(mock.MagicMock())
    slack.post_message('CHANNEL', {'text': 'TEXT'}, dryrun=True)
    slack.service.api_call.assert_not_called()


@mock.patch('fest.cloud.GoogleCalendar.get_today')
def test_slack_channel_post_today(mock_today):
    channel = fest.slack.SlackChannel(mock.MagicMock(), id='CHANNEL')
    gcal = fest.cloud.GoogleCalendar(mock.MagicMock(), id='cal_id')
    gcal.service.get_calendar_google_url.return_value = 'https://example.com'
    gcal.service.get_calendar_ical_url.return_value = 'https://example.com'
    mock_today.return_value = [
        fest.cloud.GoogleEvent(gcal.service, **{
            "summary": "Event Title",
            "htmlLink": "https://www.google.com/calendar/event?eid=eid",
            "location": "Somewhere",
            "start": {
                "dateTime": "2018-03-30T19:00:00-07:00",
            },
            "end": {
                "dateTime": "2018-03-30T21:00:00-07:00",
            },
        })
    ]
    channel.post_today(gcal, help_url='https://example.com', color='#b71c1c')
    channel.service.post_message.assert_called_once_with(
        'CHANNEL',
        {
            'text': 'There is *1* event today',
            'attachments': [
                {
                    'title': '<https://www.google.com/calendar/event?eid=eid|'
                             'Event Title>',
                    'text': 'Mar 30 from 7:00 PM to 9:00 PM at '
                            '<https://maps.google.com/maps?q=Somewhere|'
                            'Somewhere>',
                    'fallback': 'Unable to display event',
                    'color': '#b71c1c'
                }, {
                    'title': 'Subscribe to this Calendar!',
                    'text': u'Choose _\u2039\u2039 Google \u203a\u203a_ if '
                            u'you already use Google Calendar\nChoose _'
                            u'\u2039\u2039 iCalendar \u203a\u203a_ if you use '
                            u'something else\n_Subscribing via the \u2039'
                            u'\u2039 Google \u203a\u203a button will only '
                            u'work from a computer!_',
                    'mrkdwn_in': ['text'],
                    'fallback': 'Unable to display the subscription links',
                    'actions': [
                        {
                            'type': 'button',
                            'name': 'google',
                            'text': 'Google',
                            'url': 'https://example.com'
                        }, {
                            'type': 'button',
                            'name': 'icalendar',
                            'text': 'iCalendar',
                            'url': 'https://example.com'
                        }, {
                            'type': 'button',
                            'name': 'not_sure',
                            'text': "I'm not sure",
                            'url': 'https://example.com'
                        }
                    ],
                    'color': '#b71c1c'
                }
            ]
        }, dryrun=False)


def test_get_todays_message_no_events():
    channel = fest.slack.SlackChannel(mock.MagicMock(), id='CHANNEL')
    ret = channel.get_todays_message([])
    exp = 'There are no events today'
    assert ret == exp


def test_get_todays_message_one_event():
    channel = fest.slack.SlackChannel(mock.MagicMock(), id='CHANNEL')
    ret = channel.get_todays_message([1])
    exp = 'There is *1* event today'
    assert ret == exp


def test_get_todays_message_many_events():
    channel = fest.slack.SlackChannel(mock.MagicMock(), id='CHANNEL')
    ret = channel.get_todays_message([1, 2])
    exp = 'There are *2* events today'
    assert ret == exp


def test_get_attachments():
    events = [mock.MagicMock()]
    channel = fest.slack.SlackChannel(mock.MagicMock(), id='CHANNEL')
    channel.get_attachments(events, color='#b71c1c')
    events[0].to_slack.assert_called_once_with(color='#b71c1c')


def test_get_subscription():
    google_url = 'https://example.com'
    ical_url = 'https://example.com'
    help_url = 'https://example.com'
    channel = fest.slack.SlackChannel(mock.MagicMock(), id='CHANNEL')
    ret = channel.get_subscription(
        google_url, ical_url, help_url, color='#b71c1c')
    exp = {
        'title': 'Subscribe to this Calendar!',
        'text': u'Choose _\u2039\u2039 Google \u203a\u203a_ if you already '
                u'use Google Calendar\nChoose _\u2039\u2039 iCalendar \u203a'
                u'\u203a_ if you use something else\n_Subscribing via the '
                u'\u2039\u2039 Google \u203a\u203a button will only work from '
                u'a computer!_',
        'mrkdwn_in': ['text'],
        'fallback': 'Unable to display the subscription links',
        'actions': [
            {
                'type': 'button',
                'name': 'google',
                'text': 'Google',
                'url': 'https://example.com'
            }, {
                'type': 'button',
                'name': 'icalendar',
                'text': 'iCalendar',
                'url': 'https://example.com'
            }, {
                'type': 'button',
                'name': 'not_sure',
                'text': "I'm not sure",
                'url': 'https://example.com'
            }
        ],
        'color': '#b71c1c'
    }
    assert ret == exp


def test_slack_attachment_from_google():
    event = {
        'start': {
            'dateTime': '2017-03-31T12:00:00+00:00'
        },
        'end': {
            'dateTime': '2017-03-31T13:00:00+00:00'
        },
        'location': 'Someplace',
        'summary': 'This is an event',
        'htmlLink': 'https://example.com'
    }
    ret = fest.slack.SlackAttachment.from_google(event, color='#b71c1c')
    exp = {
        'color': '#b71c1c',
        'fallback': 'Unable to display event',
        'title': '<https://example.com|This is an event>',
        'text': 'Mar 31 from 12:00 PM to 1:00 PM at '
                '<https://maps.google.com/maps?q=Someplace|Someplace>'
    }
    assert ret == exp


def test_slack_attachment_from_google_multiday():
    event = {
        'start': {
            'dateTime': '2017-03-31T12:00:00+00:00'
        },
        'end': {
            'dateTime': '2017-04-01T13:00:00+00:00'
        },
        'location': 'Someplace',
        'summary': 'This is an event',
        'htmlLink': 'https://example.com'
    }
    ret = fest.slack.SlackAttachment.from_google(event, color='#b71c1c')
    exp = {
        'color': '#b71c1c',
        'fallback': 'Unable to display event',
        'title': '<https://example.com|This is an event>',
        'text': 'Mar 31 through Apr 1 at '
                '<https://maps.google.com/maps?q=Someplace|Someplace>'
    }
    assert ret == exp
