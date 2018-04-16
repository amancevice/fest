from datetime import datetime

from dateutil import parser as dateparser
import facebook
import fest.graph
import mock


class MockGraphAPI(facebook.GraphAPI):
    def get_object(self, *args, **kwargs):
        if self.access_token == 'expired_token':
            raise facebook.GraphAPIError('TEST ERROR')
        resp = {'data': [{'a': 'b'}, {'c': 'd'}],
                'paging': {'cursors': {'after': 'ABCDEF12345'}}}
        if kwargs.get('after') == 'ABCDEF12345':
            resp['paging']['cursors']['after'] = 'GHIJKL67890'
        elif kwargs.get('after') == 'GHIJKL67890':
            del resp['paging']
        return resp


def test_iter_paging():
    graph = fest.graph.GraphAPI(MockGraphAPI())
    events = list(graph.get_events('page_id'))

    assert events == [fest.graph.FacebookEvent(graph, a='b'),
                      fest.graph.FacebookEvent(graph, c='d'),
                      fest.graph.FacebookEvent(graph, a='b'),
                      fest.graph.FacebookEvent(graph, c='d'),
                      fest.graph.FacebookEvent(graph, a='b'),
                      fest.graph.FacebookEvent(graph, c='d')]


def test_facebook_object_url():
    fbobj = fest.graph.FacebookObject(None, id='1234567890')
    assert fbobj.url == 'https://www.facebook.com/1234567890'


@mock.patch('fest.graph.GraphAPI.from_token')
def test_graph_api_from_env(mock_creds):
    graph = fest.graph.GraphAPI.from_env()
    mock_creds.assert_called_once_with()


@mock.patch('facebook.GraphAPI.get_object')
def test_graph_api_get_page(mock_obj):
    graph = fest.graph.GraphAPI.from_token('page_token')
    page = graph.get_page('page_id')
    mock_obj.assert_called_once_with(
        'page_id?fields=about,location,mission,name')


@mock.patch('fest.graph.GraphAPI.iter_events')
def test_graph_api_get_events(mock_iter):
    mock_iter.return_value = iter(['a', 'b', 'c', 'd'])
    graph = fest.graph.GraphAPI.from_token('page_token')
    events = graph.get_events('page_id')
    assert events == ['a', 'b', 'c', 'd']


@mock.patch('facebook.GraphAPI.get_object')
def test_graph_api_iter_events(mock_obj):
    mock_obj.return_value = {'data': [{'a': 'b'}, {'c': 'd'}]}
    graph = fest.graph.GraphAPI.from_token('page_token')
    events = list(graph.iter_events(
        'page_id', event_state_filter=['canceled'], time_filter='upcoming'))
    assert events == [{'a': 'b'}, {'c': 'd'}]


@mock.patch('fest.graph.GraphAPI.get_object')
def test_graph_api_get_event(mock_obj):
    graph = fest.graph.GraphAPI.from_token('page_token')
    graph.get_event('1234567890')
    mock_obj.assert_called_once_with(
        '1234567890?fields='
        'cover,description,end_time,id,name,place,start_time')


def test_facebook_page_description_string():
    page = fest.graph.FacebookPage(mock.MagicMock(),
                                   id='1234567890',
                                   about='ABOUT.',
                                   mission='MISSION.')
    assert page.description_string() == \
        'ABOUT.\nMISSION.\nhttps://www.facebook.com/1234567890'


def test_facebook_page_location_string():
    page = fest.graph.FacebookPage(
        mock.MagicMock(),
        location={
            'name': 'Globex Corp.',
            'street': '15201 Maple Systems Rd',
            'city': 'Cypress Creek',
            'state': 'OR'})
    assert page.location_string() == 'Globex Corp. 15201 Maple Systems Rd '\
                                     'Cypress Creek OR'


@mock.patch('fest.graph.GraphAPI')
def test_facebook_page_get_events(mock_graph):
    page = fest.graph.FacebookPage(mock_graph, id='1234567890')
    page.get_events(time_filter='upcoming')
    mock_graph.get_events.assert_called_once_with(
        '1234567890', time_filter='upcoming')


@mock.patch('fest.graph.GraphAPI')
def test_facebook_page_iter_events(mock_graph):
    page = fest.graph.FacebookPage(mock_graph, id='1234567890')
    page.iter_events(time_filter='upcoming')
    mock_graph.iter_events.assert_called_once_with(
        '1234567890', time_filter='upcoming')


@mock.patch('fest.graph.GraphAPI')
def test_facebook_page_get_event(mock_graph):
    page = fest.graph.FacebookPage(mock_graph, id='1234567890')
    event = page.get_event('1234567890')
    mock_graph.get_event.assert_called_once_with('1234567890')


def test_facebook_event_init():
    graph = fest.graph.GraphAPI.from_token('page_token')
    obj = fest.graph.FacebookEvent(graph)
    assert obj.service == graph


def test_facebook_event_location_string():
    event = fest.graph.FacebookEvent(None, **{
        "place": {
            "location": {
                "city": "Cambridge",
                "country": "United States",
                "latitude": 42.36364,
                "longitude": -71.103733,
                "state": "MA",
                "street": "45 Pearl St",
                "zip": "02139"
            },
            "name": "Cambridge Public Library - Central Square Branch"}})
    assert event.location_string() == 'Cambridge Public Library - '\
        'Central Square Branch 45 Pearl St Cambridge MA United States 02139'


def test_facebook_event_location_string_err():
    event = fest.graph.FacebookEvent(None, **{
        "place": {
            "name": "Cambridge Public Library - Central Square Branch"}})
    assert event.location_string() == \
        'Cambridge Public Library - Central Square Branch'


def test_facebook_event_timezone():
    start_time = '2018-01-04T15:00:00-0500'
    event = fest.graph.FacebookEvent(None, start_time=start_time)
    assert event.timezone() == 'UTC-05:00'


def test_facebook_event_timezone_err():
    start_time = '2018-01-04T15:00:00'
    event = fest.graph.FacebookEvent(None, start_time=start_time)
    assert event.timezone() is None


def test_facebook_event_start():
    start_time = '2018-01-04T15:00:00-0500'
    event = fest.graph.FacebookEvent(None, start_time=start_time)
    assert event.start_time() == dateparser.parse(start_time)


def test_facebook_event_end_time():
    end_time = '2018-01-04T15:00:00-0500'
    event = fest.graph.FacebookEvent(None, end_time=end_time)
    assert event.end_time() == dateparser.parse(end_time)


def test_facebook_event_end_time_err():
    start_time = '2018-01-04T15:00:00-0500'
    end_time = '2018-01-04T16:00:00-0500'
    event = fest.graph.FacebookEvent(None, start_time=start_time)
    assert event.end_time() == dateparser.parse(end_time)


def test_facebook_event_source_id():
    event = fest.graph.FacebookEvent(None, **{'id': '1234567890'})
    assert event.source_id == event['id']


def test_facebook_event_source_digest():
    event = fest.graph.FacebookEvent(None, fizz='buzz')
    assert event.source_digest == event.digest()


@mock.patch('facebook.GraphAPI.get_object')
def test_graph_api_iter_events_recurring(mock_obj):
    mock_obj.return_value = {
        'data': [
            {'a': 'b'},
            {'c': 'd'},
            {'event_times': [
                {'e': 'f'},
                {'g': 'h'}
            ]}
        ]
    }
    graph = fest.graph.GraphAPI.from_token('page_token')
    events = list(graph.iter_events('page_id', time_filter='upcoming'))
    assert events == [{'a': 'b'}, {'c': 'd'}, {'e': 'f'}, {'g': 'h'}]
