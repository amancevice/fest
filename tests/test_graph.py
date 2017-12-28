import fest.graph
import mock


def test_graph_api_init():
    graph = fest.graph.GraphAPI('APP_ID', 'APP_SECRET')
    assert graph.app_id == 'APP_ID'
    assert graph.app_secret == 'APP_SECRET'


@mock.patch('facebook.GraphAPI.get_app_access_token')
def test_graph_api_authenticate(mock_tok):
    graph = fest.graph.GraphAPI('APP_ID', 'APP_SECRET')
    graph.authenticate()
    mock_tok.assert_called_once_with('APP_ID', 'APP_SECRET')


@mock.patch('facebook.GraphAPI.get_app_access_token')
@mock.patch('facebook.GraphAPI.get_object')
def test_graph_api_get_page(mock_obj, mock_tok):
    graph = fest.graph.GraphAPI('APP_ID', 'APP_SECRET')
    page = graph.get_page('page_id')
    mock_obj.assert_called_once_with(
        'page_id?fields=about,location,mission,name')


@mock.patch('facebook.GraphAPI.get_app_access_token')
@mock.patch('fest.graph.GraphAPI.iter_events')
def test_graph_api_get_events(mock_iter, mock_tok):
    mock_iter.return_value = iter(['a', 'b', 'c', 'd'])
    graph = fest.graph.GraphAPI('APP_ID', 'APP_SECRET')
    events = graph.get_events('page_id')
    assert events == ['a', 'b', 'c', 'd']


@mock.patch('facebook.GraphAPI.get_app_access_token')
@mock.patch('facebook.GraphAPI.get_object')
def test_graph_api_iter_events(mock_obj, mock_tok):
    mock_obj.return_value = {'data': [{'a': 'b'}, {'c': 'd'}]}
    graph = fest.graph.GraphAPI('APP_ID', 'APP_SECRET')
    events = list(graph.iter_events('page_id'))
    assert events == [{'a': 'b'}, {'c': 'd'}]


def test_facebook_event_init():
    graph = fest.graph.GraphAPI('APP_ID', 'APP_SECRET')
    obj = fest.graph.FacebookEvent(graph)
    assert obj.service == graph
