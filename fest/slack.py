"""
Slack API tools.
"""
import json
import os

import dateutil.parser
import slackclient
from fest import bases
from fest import cloud

SLACK_TOKEN = os.getenv('SLACK_API_TOKEN')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL')


class SlackAPI(bases.BaseAPI):
    """ Slack API Service.

        :param object service: SlackClient instance
    """
    @classmethod
    def from_env(cls):
        """ Create CalendarAPI object from ENV variables. """
        return cls.from_credentials()

    @classmethod
    def from_credentials(cls, token=None):
        """ Create SlackAPI object from credentials

            :param str token: Slack API token
        """
        service = slackclient.SlackClient(token or SLACK_TOKEN)
        return cls(service)

    def post_message(self, message, channel=None):
        """ Post message to Slack channel.

            :param dict message: message JSON to post.
            :param str channel: Slack channel ID
        """
        channel = channel or SLACK_CHANNEL
        self.logger.info('POST %s %s', channel, json.dumps(message))
        return self.service.api_call(
            'chat.postMessage', channel=channel, **message)


class SlackMessage(bases.BaseObject):
    """ Slack Message. """
    @staticmethod
    def from_google(google_calendar, service=None, **kwargs):
        """ Helper to convert a GoogleCalendar to a SlackMessage.

            :param object google_event: GoogleEvent instance
            :param object service: Optional SlackAPI service instance
            :returns object: SlackAttachment instance
        """
        events = google_calendar.get_today()
        if not any(events):
            text = 'There are no events today\n'
        elif len(events) == 1:
            text = 'There is *1* event today\n'
        else:
            text = 'There are *{}* events today\n'.format(len(events))
        text += \
            u'_Subscribing via the \u2039\u2039 Google \u203a\u203a button '\
            u'will only work from a computer!_'
        sub = SlackSubAttachment.from_google(google_calendar, **kwargs)
        attachments = [SlackAttachment.from_google(x, **kwargs)
                       for x in events] + [sub]
        attachments = [dict(x) for x in attachments]
        message = SlackMessage(service, text=text, attachments=attachments)
        return message


class SlackAttachment(bases.BaseObject):
    """ Slack Event Attachment. """
    @staticmethod
    def from_google(google_event, service=None, **kwargs):
        """ Helper to convert a GoogleEvent to a SlackAttachment.

            :param object google_event: GoogleEvent instance
            :param object service: Optional SlackAPI service instance
            :returns object: SlackAttachment instance
        """
        fallback = 'Unable to display event'
        title_text = google_event.get('summary')
        title_link = google_event.get('htmlLink')
        title = '<{link}|{text}>'.format(link=title_link, text=title_text)
        start = google_event.get('start') or {}
        start = dateutil.parser.parse(start.get('dateTime') or
                                      start.get('date'))
        end = google_event.get('end') or {}
        end = dateutil.parser.parse(end.get('dateTime') or end.get('date'))
        if start.date() == end.date():
            text = '{date} from {start} to {end}'.format(
                date=start.strftime('%b %-d'),
                start=start.strftime('%-I:%M %p'),
                end=end.strftime('%-I:%M %p'))
        else:
            text = '{start} through {end}'.format(
                start=start.strftime('%b %-d'),
                end=end.strftime('%b %-d'))
        if google_event.get('location'):
            loc_text = google_event.get('location')
            loc_link = 'https://maps.google.com/maps?q={}'.format(
                loc_text.replace(',', '').replace(' ', '+'))
            text += ' at <{loc_link}|{loc_text}>'.format(loc_link=loc_link,
                                                         loc_text=loc_text)
        attachment = SlackAttachment(
            service, title=title, text=text, fallback=fallback, **kwargs)
        return attachment


class SlackSubAttachment(bases.BaseObject):
    """ Slack Calendar Subscription Attachment. """
    @staticmethod
    def from_google(google_calendar, service=None, **kwargs):
        """ Helper to convert a GoogleCalendar to a
            SlackSubAttachment.

            :param object google_calendar: GoogleCalendar instance
            :param object service: Optional SlackAPI service instance
            :returns object: SlackAttachment instance
        """
        url = google_calendar.url
        if url:
            title = 'Subscribe to this <{url}|Calendar>!'.format(url=url)
        else:
            title = 'Subscribe to this Calendar!'
        text = u'Choose \u2039\u2039 Google \u203a\u203a if you use already '\
               u'have a Google Calendar\nChoose \u2039\u2039 iCalendar \u203a'\
               u'\u203a if you use something else'
        fallback = 'Unable to display the subscription links'
        actions = [
            {'type': 'button', 'name': 'google', 'text': 'Google'},
            {'type': 'button', 'name': 'icalendar', 'text': 'iCalendar'},
            {'type': 'button', 'name': 'not_sure', 'text': "I'm not sure"}]
        attachment = SlackSubAttachment(
            service,
            title=title,
            text=text,
            fallback=fallback,
            actions=actions,
            **kwargs)
        return attachment


cloud.GoogleCalendar.to_slack = SlackMessage.from_google
cloud.GoogleEvent.to_slack = SlackAttachment.from_google
