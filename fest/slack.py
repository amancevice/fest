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

    def get_channel(self, channel_id):
        """ Get SlackChannel object.

            :param str channel_id: Slack channel ID
            :returns object: SlackChannel object
        """
        return SlackChannel(self, id=channel_id)

    def post_message(self, channel_id, message, dryrun=False):
        """ Post message to Slack channel.

            :param str channel: Slack channel ID
            :param dict message: message JSON to post.
            :param bool dryrun: Do not send POST
        """
        if dryrun:
            return self.logger.debug(
                'DRYRUN POST %s %s',
                channel_id,
                json.dumps(message))
        self.logger.info('POST %s %s', channel_id, json.dumps(message))
        return self.service.api_call('chat.postMessage', channel_id, **message)


class SlackChannel(bases.BaseObject):
    """ Slack channel obejct. """
    @staticmethod
    def get_todays_message(google_events):
        """ Get message for today's events.

            :param list google_events: GoogleEvent object(s)
            :returns str: Text for today's events
        """
        if not any(google_events):
            return 'There are no events today'
        elif len(google_events) == 1:
            return 'There is *1* event today'
        return 'There are *{}* events today'.format(len(google_events))

    @staticmethod
    def get_attachments(google_events, **kwargs):
        """ Get attachments for events.

            :param list google_events: GoogleEvent object(s)
            :returns str: Text for today's events
        """
        return [dict(x.to_slack(**kwargs)) for x in google_events]

    @staticmethod
    def get_subscription(google_url, ical_url, help_url=None, **kwargs):
        """ Helper to convert a GoogleCalendar to a SlackSubscription.

            :param str google_url: Link to subscribe via Google
            :param str ical_url: Link to subscribe via iCalendar
            :param str help_url: Optional link to get help
            :returns dict: Subscription attachment
        """
        # Message body
        title = 'Subscribe to this Calendar!'
        text = u'Choose _\u2039\u2039 Google \u203a\u203a_ if you already '\
               u'use Google Calendar\nChoose _\u2039\u2039 iCalendar \u203a'\
               u'\u203a_ if you use something else\n'\
               u'_Subscribing via the \u2039\u2039 Google \u203a\u203a '\
               u'button will only work from a computer!_'
        fallback = 'Unable to display the subscription links'
        mrkdwn_in = ['text']

        # Action buttons
        google = {
            'type': 'button',
            'name': 'google',
            'text': 'Google',
            'url': google_url}
        ical = {
            'type': 'button',
            'name': 'icalendar',
            'text': 'iCalendar',
            'url': ical_url}
        actions = [google, ical]
        if help_url:
            help_action = {
                'type': 'button',
                'name': 'not_sure',
                'text': "I'm not sure",
                'url': help_url}
            actions.append(help_action)

        # Create attachment
        attachment = dict(
            title=title,
            text=text,
            mrkdwn_in=mrkdwn_in,
            fallback=fallback,
            actions=actions,
            **kwargs)
        return attachment

    def post_today(self, google_calendar, help_url=None, dryrun=False,
                   **kwargs):
        """ Post today's events to channel.

            :param object google_calendar: GoogleCalendar object
            :param str help_url: URL for help link
            :param bool dryrun: Do not send POST
        """
        google_events = google_calendar.get_today()
        text = self.get_todays_message(google_events)
        attachments = self.get_attachments(google_events, **kwargs)
        subscription = self.get_subscription(
            google_url=google_calendar.google_url,
            ical_url=google_calendar.ical_url,
            help_url=help_url,
            **kwargs)
        message = {'text': text, 'attachments': attachments + [subscription]}
        return self.service.post_message(self['id'], message, dryrun=dryrun)


class SlackAttachment(bases.BaseObject):
    """ Slack Event Attachment. """
    @staticmethod
    def from_google(google_event, service=None, **kwargs):
        """ Helper to convert a GoogleEvent to a SlackAttachment.

            :param object google_event: GoogleEvent instance
            :param object service: Optional SlackAPI service instance
            :returns object: SlackAttachment instance
        """
        # Attachment link
        title_text = google_event.get('summary')
        title_link = google_event.get('htmlLink')
        title = '<{link}|{text}>'.format(link=title_link, text=title_text)
        fallback = 'Unable to display event'

        # Attachment body (start/end)
        text = ''
        start = google_event.get('start') or {}
        start = start.get('dateTime') or start.get('date')
        end = google_event.get('end') or {}
        end = end.get('dateTime') or end.get('date')
        if start and end:
            start = dateutil.parser.parse(start)
            end = dateutil.parser.parse(end)
            if start.date() == end.date():
                text = '{date} from {start} to {end}'.format(
                    date=start.strftime('%b %-d'),
                    start=start.strftime('%-I:%M %p'),
                    end=end.strftime('%-I:%M %p'))
            else:
                text = '{start} through {end}'.format(
                    start=start.strftime('%b %-d'),
                    end=end.strftime('%b %-d'))

        # Attachment body (location)
        if google_event.get('location'):
            loc_text = google_event.get('location')
            loc_link = 'https://maps.google.com/maps?q={}'.format(
                loc_text.replace(',', '').replace(' ', '+'))
            text += ' at <{loc_link}|{loc_text}>'.format(
                loc_link=loc_link, loc_text=loc_text)

        # Attachment
        attachment = SlackAttachment(
            service, title=title, text=text, fallback=fallback, **kwargs)
        return attachment


cloud.GoogleEvent.to_slack = SlackAttachment.from_google
