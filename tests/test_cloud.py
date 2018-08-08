from datetime import datetime

import googleapiclient
import fest.cloud
import fest.graph
import pytz
import mock


class MockCalendarAPI(fest.cloud.CalendarAPI):
    def __init__(self, service=None):
        super(MockCalendarAPI, self).__init__(service or mock.MagicMock())


class MockCalendarListRequest(googleapiclient.http.HttpRequest):
    def __init__(self, pageToken):
        self.pageToken = pageToken

    def execute(self, http=None, num_retries=0):
        import ipdb; ipdb.set_trace()


class MockCalendarListResource(googleapiclient.discovery.Resource):
    def __init__(self, *args, **kwargs):
        pass

    def list(self, pageToken=None, **kwargs):
        return MockCalendarListRequest(pageToken)


class MockCloudService(googleapiclient.discovery.Resource):
    def __init__(self, *args, **kwargs):
        pass

    def calendarList(self):
        return MockCalendarListResource()


@mock.patch('fest.cloud.CalendarAPI.from_credentials')
def test_calendar_api_from_env(mock_creds):
    cloud = fest.cloud.CalendarAPI.from_env()
    mock_creds.assert_called_once_with()


@mock.patch('apiclient.discovery.build')
@mock.patch('google.oauth2.service_account.Credentials'
            '.from_service_account_info')
def test_calendar_api_from_credentials(mock_keys, mock_build):
    scopes = ['https://www.googleapis.com/auth/calendar']
    private_key_id = 'my_private_key_id'
    private_key = 'my_private_key'
    client_email = 'email@project.iam.gserviceaccount.com'
    client_id = '1234567890987654321'
    token_uri = 'https://accounts.google.com/o/oauth2/token'
    cloud = fest.cloud.CalendarAPI.from_credentials(
        scopes=scopes,
        private_key_id=private_key_id,
        private_key=private_key,
        client_email=client_email,
        client_id=client_id,
        token_uri=token_uri)
    mock_keys.assert_called_once_with({
        'private_key_id': private_key_id,
        'private_key': private_key,
        'client_email': client_email,
        'client_id': client_id,
        'token_uri': token_uri})
    mock_keys.return_value.with_scopes.assert_called_once_with(scopes)
    mock_build.assert_called_once_with(
        'calendar', 'v3',
        credentials=mock_keys.return_value.with_scopes.return_value,
        cache_discovery=False)


def test_cloud_add_event():
    event = mock.MagicMock()
    cloud = MockCalendarAPI()
    cloud.add_event('cal_id', event)
    event.to_google.assert_called_once_with()
    cloud.service.events.assert_called_once_with()
    cloud.service.events.return_value.insert.assert_called_once_with(
        calendarId='cal_id', body=event.to_google.return_value.struct)
    cloud.service\
         .events.return_value\
         .insert.return_value\
         .execute.assert_called_once_with()


def test_cloud_add_owner():
    cloud = MockCalendarAPI()
    cloud.add_owner('cal_id', 'owner@me.com')
    cloud.service.acl.assert_called_once_with()
    cloud.service.acl.return_value.insert.assert_called_once_with(
        calendarId='cal_id',
        body={'scope': {'type': 'user', 'value': 'owner@me.com'},
              'kind': 'calendar#aclRule', 'role': 'owner'})
    cloud.service\
         .acl.return_value\
         .insert.return_value\
         .execute.assert_called_once_with()


@mock.patch('fest.cloud.CalendarAPI.iter_events')
def test_cloud_clear_events(mock_iter):
    events = {'id': '1'}, {'id': '2'}, {'id': '3'}
    mock_iter.return_value = iter(events)
    cloud = MockCalendarAPI()
    cloud.clear_events('cal_id')
    cloud.service.new_batch_http_request.assert_called_once_with()
    cloud.service.events.assert_called_once_with()
    calls = cloud.service.events.return_value.delete.call_args_list
    for event, call in zip(events, calls):
        assert call == mock.call(calendarId='cal_id', eventId=event['id'])
    cloud.service\
         .new_batch_http_request.return_value\
         .execute.assert_called_once_with()


def test_cloud_create_calendar():
    cal = mock.MagicMock()
    cloud = MockCalendarAPI()
    cloud.create_calendar(cal, 'America/Los_Angeles')
    cal.to_google.assert_called_once_with('America/Los_Angeles')
    cloud.service.calendars.assert_called_once_with()
    cloud.service\
         .calendars.return_value\
         .insert.assert_called_once_with(body=cal.to_google.return_value)
    cloud.service\
         .calendars.return_value\
         .insert.return_value\
         .execute.assert_called_once_with()


def test_cloud_delete_calendar():
    cloud = MockCalendarAPI()
    cloud.delete_calendar('cal_id')
    cloud.service.calendars.assert_called_once_with()
    cloud.service\
         .calendars.return_value\
         .delete.assert_called_once_with(calendarId='cal_id')
    cloud.service\
         .calendars.return_value\
         .delete.return_value\
         .execute.assert_called_once_with()


def test_cloud_delete_event():
    cloud = MockCalendarAPI()
    cloud.delete_event('cal_id', 'event_id')
    cloud.service.events.assert_called_once_with()
    cloud.service\
         .events.return_value\
         .delete.assert_called_once_with(calendarId='cal_id',
                                         eventId='event_id')


@mock.patch('fest.cloud.CalendarAPI.iter_calendars')
def test_cloud_get_calendars(mock_iter):
    cloud = MockCalendarAPI()
    cloud.get_calendars()
    mock_iter.assert_called_once_with()


def test_cloud_get_calendar():
    cloud = MockCalendarAPI()
    cloud.get_calendar('cal_id')
    cloud.service.calendars.assert_called_once_with()
    cloud.service\
         .calendars.return_value\
         .get.assert_called_once_with(calendarId='cal_id')
    cloud.service\
         .calendars.return_value\
         .get.return_value\
         .execute.assert_called_once_with()


@mock.patch('fest.cloud.CalendarAPI.iter_calendars')
def test_cloud_get_calendar_by_facebook_id(mock_iter):
    cals = [{'id': '1', 'description': 'https://www.facebook.com/1234567890'},
            {'id': '2', 'description': 'https://www.facebook.com/9876543210'},
            {'id': '3', 'description': 'https://www.facebook.com/7777777777'}]
    mock_iter.return_value = iter(cals)
    cloud = MockCalendarAPI()
    ret = cloud.get_calendar_by_facebook_id('7777777777')
    assert ret == cals[-1]


@mock.patch('fest.cloud.CalendarAPI.iter_calendars')
def test_cloud_get_calendar_by_facebook_id_none(mock_iter):
    cals = [{'id': '1', 'description': 'facebook#1234567890'},
            {'id': '2', 'description': 'facebook#9876543210'},
            {'id': '3', 'description': 'facebook#7777777777'}]
    mock_iter.return_value = iter(cals)
    cloud = MockCalendarAPI()
    ret = cloud.get_calendar_by_facebook_id('9999999999')
    assert ret is None


def test_cloud_get_calendar_google_url():
    cloud = MockCalendarAPI()
    ret = cloud.get_calendar_google_url('9999999999')
    assert ret == 'https://calendar.google.com/calendar/r?cid=OTk5OTk5OTk5OQ'


def test_cloud_get_calendar_ical_url():
    cloud = MockCalendarAPI()
    ret = cloud.get_calendar_ical_url('999999999')
    assert ret == \
        'webcal://calendar.google.com/calendar/ical/999999999/public/basic.ics'


def test_cloud_get_event():
    cloud = MockCalendarAPI()
    cloud.get_event('cal_id', 'event_id')
    cloud.service.events.assert_called_once_with()
    cloud.service\
         .events.return_value\
         .get.assert_called_once_with(calendarId='cal_id', eventId='event_id')
    cloud.service\
         .events.return_value\
         .get.return_value\
         .execute.assert_called_once_with()


@mock.patch('fest.cloud.CalendarAPI.iter_events')
def test_cloud_get_events(mock_iter):
    cloud = MockCalendarAPI()
    cloud.get_events('cal_id')
    mock_iter.assert_called_once_with('cal_id')


@mock.patch('fest.cloud.CalendarAPI.iter_events')
def test_cloud_get_event_by_source_id(mock_iter):
    cloud = MockCalendarAPI()
    events = [{'id': '1', 'extendedProperties': {'shared': {'sourceId': 'A'}}},
              {'id': '2', 'extendedProperties': {'shared': {'sourceId': 'B'}}},
              {'id': '3', 'extendedProperties': {'shared': {'sourceId': 'C'}}}]
    mock_iter.return_value = \
        iter([fest.cloud.GoogleEvent(cloud, **x) for x in events])
    ret = cloud.get_event_by_source_id('cal_id', 'C')
    assert ret == events[-1]


@mock.patch('fest.cloud.CalendarAPI.iter_events')
def test_cloud_get_event_by_source_id_none(mock_iter):
    cloud = MockCalendarAPI()
    events = [{'id': '1', 'extendedProperties': {'shared': {'sourceId': 'A'}}},
              {'id': '2', 'extendedProperties': {'shared': {'sourceId': 'B'}}},
              {'id': '3', 'extendedProperties': {'shared': {'sourceId': 'C'}}}]
    mock_iter.return_value = \
        iter([fest.cloud.GoogleEvent(cloud, **x) for x in events])
    ret = cloud.get_event_by_source_id('cal_id', 'D')
    assert ret is None


@mock.patch('fest.cloud.CalendarAPI.iter_events')
@mock.patch('pytz.UTC.localize')
def test_cloud_get_today(mock_astz, mock_iter):
    mock_astz.return_value = datetime(2018, 3, 30, 12, tzinfo=pytz.utc)
    cloud = MockCalendarAPI()
    cloud.get_today('cal_id', 'America/Los_Angeles')
    mock_iter.assert_called_once_with('cal_id',
                                      timeMax='2018-03-31T00:00:00-07:00',
                                      timeMin='2018-03-30T00:00:00-07:00')


def test_cloud_patch_event():
    event = mock.MagicMock()
    cloud = MockCalendarAPI()
    cloud.patch_event('cal_id', 'event_id', event)
    event.to_google.assert_called_once_with()
    cloud.service.events.assert_called_once_with()
    cloud.service\
         .events.return_value\
         .patch.assert_called_once_with(
             calendarId='cal_id',
             eventId='event_id',
             body=event.to_google.return_value.struct)
    cloud.service\
         .events.return_value\
         .patch.return_value\
         .execute.assert_called_once_with()


def test_calendar_from_facebook():
    page = fest.graph.FacebookPage(
        None,
        about='About page',
        id='1234567890',
        location={
            'city': 'Boston',
            'country': 'United States',
            'latitude': 42.3578,
            'longitude': -71.0617,
            'state': 'MA',
            'zip': '02205'
        },
        mission='Mission statement',
        name='Page name')
    gcal = fest.cloud.GoogleCalendar.from_facebook(page, 'America/New_York')
    assert gcal.struct == {
        'description': 'About page\n'
                       'Mission statement\n'
                       'https://www.facebook.com/1234567890',
        'location': 'Boston MA United States 02205',
        'summary': 'Page name',
        'timeZone': 'America/New_York'}


def test_calendar_add_event():
    event = mock.MagicMock()
    gcal = fest.cloud.GoogleCalendar(mock.MagicMock(), id='cal_id')
    gcal.add_event(event)
    gcal.service.add_event.assert_called_once_with('cal_id', event)


def test_calendar_add_owner():
    gcal = fest.cloud.GoogleCalendar(mock.MagicMock(), id='cal_id')
    gcal.add_owner('owner@me.com')
    gcal.service.add_owner.assert_called_once_with('cal_id', 'owner@me.com')


def test_calendar_clear_events():
    gcal = fest.cloud.GoogleCalendar(mock.MagicMock(), id='cal_id')
    gcal.clear_events()
    gcal.service.clear_events.assert_called_once_with('cal_id')


def test_calendar_get_events():
    gcal = fest.cloud.GoogleCalendar(mock.MagicMock(), id='cal_id')
    gcal.get_events()
    gcal.service.iter_events.assert_called_once_with('cal_id')


def test_calendar_get_event():
    gcal = fest.cloud.GoogleCalendar(mock.MagicMock(), id='cal_id')
    gcal.get_event('event_id')
    gcal.service.get_event.assert_called_once_with('cal_id', 'event_id')


def test_calendar_get_event_by_source_id():
    gcal = fest.cloud.GoogleCalendar(mock.MagicMock(), id='cal_id')
    gcal.get_event_by_source_id('1234567890')
    gcal.service.get_event_by_source_id.assert_called_once_with(
        'cal_id', '1234567890')


def test_calendar_get_today():
    gcal = fest.cloud.GoogleCalendar(
        mock.MagicMock(), id='cal_id', timeZone='America/Los_Angeles')
    gcal.get_today()
    gcal.service.get_today.assert_called_once_with(
        'cal_id', 'America/Los_Angeles')


def test_calendar_google_url():
    gcal = fest.cloud.GoogleCalendar(mock.MagicMock(), id='9999999999')
    gcal.google_url
    gcal.service.get_calendar_google_url.assert_called_once_with('9999999999')


def test_calendar_ical_url():
    gcal = fest.cloud.GoogleCalendar(mock.MagicMock(), id='9999999999')
    gcal.ical_url
    gcal.service.get_calendar_ical_url.assert_called_once_with('9999999999')


def test_calendar_iter_events():
    gcal = fest.cloud.GoogleCalendar(mock.MagicMock(), id='cal_id')
    gcal.iter_events()
    gcal.service.iter_events.assert_called_once_with('cal_id')


def test_calendar_patch_event():
    event = mock.MagicMock()
    gcal = fest.cloud.GoogleCalendar(mock.MagicMock(), id='cal_id')
    gcal.patch_event('event_id', event)
    gcal.service.patch_event.assert_called_once_with(
        'cal_id', 'event_id', event)


def test_calendar_sync_event():
    event = mock.MagicMock()
    gcal = fest.cloud.GoogleCalendar(mock.MagicMock(), id='cal_id')
    gcal.sync_event(event)
    gcal.service.sync_event.assert_called_once_with('cal_id', event)


def test_calendar_sync_events():
    events = mock.MagicMock()
    gcal = fest.cloud.GoogleCalendar(mock.MagicMock(), id='cal_id')
    gcal.sync_events(events)
    gcal.service.sync_events.assert_called_once_with(
        'cal_id', events, False, False)


def test_event_source_id():
    gevent = fest.cloud.GoogleEvent(
        mock.MagicMock,
        id='event_id',
        extendedProperties={
            'shared': {'sourceId': 'source_id', 'digest': 'x'}})
    assert gevent.source_id == 'source_id'


def test_event_source_digest():
    gevent = fest.cloud.GoogleEvent(
        mock.MagicMock,
        id='event_id',
        extendedProperties={
            'shared': {'sourceId': 'source_id', 'digest': 'x'}})
    assert gevent.source_digest == 'x'


@mock.patch('fest.bases.BaseObject.digest')
def test_event_from_facebook(mock_dig):
    event = fest.graph.FacebookEvent(
        mock.MagicMock(),
        description='desc',
        end_time='2018-02-11T16:00:00-0500',
        id='1234567890',
        name='name',
        place={'name': 'place'},
        start_time='2018-02-11T11:00:00-0500')
    gevent = fest.cloud.GoogleEvent.from_facebook(event)
    assert gevent.struct == {
        'description': 'desc\n\nhttps://www.facebook.com/1234567890',
        'start': {
            'dateTime': '2018-02-11T11:00:00',
            'timeZone': 'UTC-05:00'
        },
        'extendedProperties': {
            'shared': {
                'digest': mock_dig.return_value,
                'sourceId': '1234567890'
            }
        },
        'end': {
            'dateTime': '2018-02-11T16:00:00',
            'timeZone': 'UTC-05:00'
        },
        'summary': 'name',
        'location': 'place'
    }


def test_cloud_iter_calendars():
    cloud = MockCalendarAPI()
    cloud.service\
         .calendarList.return_value\
         .list.return_value\
         .execute.return_value = {'items': [{'id': '1'}, {'id': '2'}]}
    assert list(cloud.iter_calendars()) == [
        fest.cloud.GoogleCalendar(cloud, id='1'),
        fest.cloud.GoogleCalendar(cloud, id='2')]


def test_cloud_iter_events():
    cloud = MockCalendarAPI()
    cloud.service\
         .events.return_value\
         .list.return_value\
         .execute.return_value = {'items': [{'id': '1'}, {'id': '2'}]}
    assert list(cloud.iter_events('cal_id')) == [
        fest.cloud.GoogleEvent(cloud, id='1'),
        fest.cloud.GoogleEvent(cloud, id='2')]


@mock.patch('fest.cloud.CalendarAPI.iter_events')
@mock.patch('fest.cloud.CalendarAPI.patch_event')
def test_cloud_sync_event_patch(mock_patch, mock_iter):
    cloud = MockCalendarAPI()
    mock_iter.return_value = iter([
        fest.cloud.GoogleEvent(
            cloud,
            id='1',
            extendedProperties={
                'shared': {
                    'sourceId': 'A',
                    'digest': 'abcdefg'}})])
    mock_event = mock.MagicMock()
    mock_event.source_id = 'A'
    mock_event.digest.return_value = '1234567'
    cloud.sync_event('cal_id', mock_event)
    mock_patch.assert_called_once_with('cal_id', '1', mock_event)


@mock.patch('fest.cloud.CalendarAPI.iter_events')
@mock.patch('fest.cloud.CalendarAPI.add_event')
def test_cloud_sync_event_add(mock_add, mock_iter):
    cloud = MockCalendarAPI()
    mock_iter.return_value = iter([])
    mock_event = mock.MagicMock()
    mock_event.source_id = 'A'
    mock_event.digest.return_value = '1234567'
    cloud.sync_event('cal_id', mock_event)
    mock_add.assert_called_once_with('cal_id', mock_event)


@mock.patch('fest.cloud.CalendarAPI.iter_events')
@mock.patch('fest.cloud.CalendarAPI.patch_event')
@mock.patch('fest.cloud.CalendarAPI.add_event')
def test_cloud_sync_event_no_op(mock_add, mock_patch, mock_iter):
    cloud = MockCalendarAPI()
    mock_iter.return_value = iter([
        fest.cloud.GoogleEvent(
            cloud,
            id='1',
            extendedProperties={
                'shared': {
                    'sourceId': 'A',
                    'digest': 'abcdefg'}})])
    mock_event = mock.MagicMock()
    mock_event.source_id = 'A'
    mock_event.digest.return_value = 'abcdefg'
    cloud.sync_event('cal_id', mock_event)
    mock_patch.assert_not_called()
    mock_add.assert_not_called()


@mock.patch('fest.cloud.CalendarAPI.iter_events')
def test_cloud_sync_events(mock_iter):
    cloud = MockCalendarAPI()
    mock_iter.return_value = iter([
        fest.cloud.GoogleEvent(
            cloud,
            id='1',
            extendedProperties={
                'shared': {
                    'sourceId': 'A',
                    'digest': 'abcdefg'}}),
        fest.cloud.GoogleEvent(
            cloud,
            id='2',
            extendedProperties={
                'shared': {
                    'sourceId': 'C',
                    'digest': 'qwertyu'}})])
    mock_event1 = mock.MagicMock()
    mock_event1.source_id = 'A'
    mock_event1.digest.return_value = 'abcdefg'
    mock_event2 = mock.MagicMock()
    mock_event2.source_id = 'A'
    mock_event2.digest.return_value = '1234567'
    mock_event3 = mock.MagicMock()
    mock_event3.source_id = 'B'
    mock_event3.digest.return_value = '9876543'
    mock_event4 = mock.MagicMock()
    mock_event4.source_id = 'C'
    mock_event4.digest.return_value = 'qwertyu'
    cloud.sync_events('cal_id', {
        'upcoming': [mock_event1, mock_event2, mock_event3],
        'canceled': [mock_event4]})
    cloud.service\
         .events.return_value\
         .patch.assert_called_once_with(
             calendarId='cal_id',
             eventId='1',
             body=mock_event2.to_google.return_value.struct)
    cloud.service\
         .events.return_value\
         .insert.assert_called_once_with(
             calendarId='cal_id',
             body=mock_event3.to_google.return_value.struct)
    cloud.service\
         .events.return_value\
         .delete.assert_called_once_with(
             calendarId='cal_id',
             eventId='2')
    cloud.service\
         .new_batch_http_request.return_value\
         .execute.assert_called_once_with()


@mock.patch('fest.cloud.CalendarAPI.iter_events')
def test_cloud_sync_events_dryrun(mock_iter):
    cloud = MockCalendarAPI()
    mock_iter.return_value = iter([
        fest.cloud.GoogleEvent(
            cloud,
            id='1',
            extendedProperties={
                'shared': {
                    'sourceId': 'A',
                    'digest': 'abcdefg'}})])
    mock_event1 = mock.MagicMock()
    mock_event1.source_id = 'A'
    mock_event1.digest.return_value = 'abcdefg'
    mock_event2 = mock.MagicMock()
    mock_event2.source_id = 'A'
    mock_event2.digest.return_value = '1234567'
    mock_event3 = mock.MagicMock()
    mock_event3.source_id = 'B'
    mock_event3.digest.return_value = '9876543'
    cloud.sync_events('cal_id',
                      {'upcoming': [mock_event1, mock_event2, mock_event3]},
                      dryrun=True)
    cloud.service\
         .events.return_value\
         .patch.assert_called_once_with(
             calendarId='cal_id',
             eventId='1',
             body=mock_event2.to_google.return_value.struct)
    cloud.service\
         .events.return_value\
         .insert.assert_called_once_with(
             calendarId='cal_id',
             body=mock_event3.to_google.return_value.struct)
    cloud.service\
         .new_batch_http_request.return_value\
         .execute.assert_not_called()
