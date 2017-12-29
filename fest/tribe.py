"""
The Events Calendar tools.
"""
import base64
import os

import requests
import wordpress_xmlrpc as wp
from fest import bases
from fest import graph

WORDPRESS_ENDPOINT = os.getenv('WORDPRESS_ENDPOINT')
WORDPRESS_USERNAME = os.getenv('WORDPRESS_USERNAME')
WORDPRESS_APP_PASSWORD = os.getenv('WORDPRESS_APP_PASSWORD')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
TRIBE_ENDPOINT = os.getenv('TRIBE_ENDPOINT')


class WordPress(wp.Client):
    """ WordPress XML RPC client.

        :param str url: XML RPC endpoint
        :param str username: WordPress app username
        :param str password: WordPress app password
    """
    def __init__(self, url=None, username=None, password=None, blog_id=0,
                 transport=None):
        # pylint: disable=too-many-arguments
        endpoint = url or WORDPRESS_ENDPOINT
        username = username or WORDPRESS_USERNAME
        password = password or WORDPRESS_APP_PASSWORD
        super(WordPress, self).__init__(
            endpoint, username, password, blog_id, transport)

    def get_tribe(self, endpoint=None, static_custom_fields=None):
        """ Get Tribe client. """
        return TribeCalendar(self, endpoint, static_custom_fields)

    def get_post(self, post_id):
        """ Get tribe event post by post_id. """
        request = wp.methods.posts.GetPost(post_id)
        return self.call(request)

    def get_posts(self, **kwargs):
        """ Get list of tribe event posts. """
        return list(self.iter_posts(**kwargs))

    def iter_posts(self, **kwargs):
        """ Iterate over tribe event posts. """
        request = wp.methods.posts.GetPosts(kwargs)
        for post in self.call(request):
            yield post


class TribeAPI(object):
    """ The Events Calendar client

        :param object wordpress: WordPress XML RPC client instance
        :param str endpoint: URL of tribe events REST service
    """
    STATIC_CUSTOM_FIELDS = []

    def __init__(self, wordpress=None, endpoint=None,
                 static_custom_fields=None):
        self.wordpress = wordpress or WordPress()
        self.endpoint = endpoint or TRIBE_ENDPOINT
        self.static_custom_fields = static_custom_fields or \
            self.STATIC_CUSTOM_FIELDS

    @classmethod
    def set_static_custom_fields(cls, custom_fields):
        """ Set STATIC_CUSTOM_FIELDS value for TribeEvent instances.

            :param list[dict] custom_fields: Custom fields for WordPress post
        """
        cls.STATIC_CUSTOM_FIELDS = custom_fields

    def add_event(self, facebook_event, custom_fields=None):
        """ Add facebook event.

            :param object facebook_event: FacebookEvent instance
            :param list[dict] custom_fields: Custom fields for WordPress post
        """
        # Create WordPress post
        post = wp.WordPressPost()
        post.custom_fields = (custom_fields or []) + self.static_custom_fields
        post.custom_fields += [
            {'key': 'facebook_id', 'value': facebook_event['id']},
            {'key': 'facebook_digest', 'value': facebook_event.digest()}]
        post.post_status = 'publish'
        post.post_type = 'tribe_events'
        post.slug = facebook_event['id']
        post.title = facebook_event['name']
        request = wp.methods.posts.NewPost(post)
        post.id = self.wordpress.call(request)

        # Create tribe event
        insert_event = facebook_event.to_tribe(self)
        url = "{}/events/{}".format(self.endpoint, post.id)
        headers = self.basic_auth()
        return requests.post(url, headers=headers, json=insert_event.struct)

    def basic_auth(self):
        """ Helper to get basic auth header. """
        auth = "{}:{}".format(self.wordpress.username, self.wordpress.password)
        token = base64.standard_b64encode(auth.encode('utf-8'))
        return {'Authorization': 'Basic {}'.format(token.decode('utf-8'))}

    def get_event(self, post_id):
        """ Get tribe event by post_id. """
        request = wp.methods.posts.GetPost(post_id)
        return TribeEvent(self, self.wordpress.call(request))

    def get_events(self, **kwargs):
        """ Get list of tribe events. """
        return list(self.iter_events(**kwargs))

    def get_facebook_event(self, facebook_id):
        """ Get event by facebook ID.

            Searches custom_fields for 'facebook_id'

            :param str facebook_id: ID of facebook page
            :returns object: GoogleEvent instance
        """
        for tribe_event in self.iter_events():
            if facebook_id == tribe_event.facebook_id:
                return tribe_event
        return None

    def iter_events(self, **kwargs):
        """ Iterate over tribe events. """
        kwargs.setdefault('post_type', 'tribe_events')
        kwargs.setdefault('number', 1000)
        for post in self.wordpress.iter_posts(**kwargs):

            # Get Tribe event
            url = "{}/events/{}".format(self.endpoint, post.id)
            headers = self.basic_auth()
            response = requests.get(url, headers=headers)

            # Yield TribeEvent instance
            yield TribeEvent(self, post, **response.json())

    def patch_event(self, facebook_event, tribe_event):
        """ Patch facebook event.

            :param object facebook_event: FacebookEvent instance
            :param object tribe_event: TribeEvent instance
        """
        # Patch WordPress post
        post = tribe_event.post
        post.custom_fields = [x for x in post.custom_fields
                              if x['key'] not in
                              ['facebook_id', 'facebook_digest']]
        post.custom_fields += [
            {'key': 'facebook_id', 'value': facebook_event['id']},
            {'key': 'facebook_digest', 'value': facebook_event.digest()}]
        post.post_status = 'publish'
        post.post_type = 'tribe_events'
        post.slug = facebook_event['id']
        post.title = facebook_event['name']
        request = wp.methods.posts.EditPost(post.id, post)

        # Update tribe event
        if self.wordpress.call(request):
            patch_event = facebook_event.to_tribe(self)
            url = "{}/events/{}".format(self.endpoint, post.id)
            headers = self.basic_auth()
            return requests.post(url, headers=headers, json=patch_event.struct)
        return None

    def sync_event(self, facebook_event):
        """ Synchronize facebook event with tribe calendar.

            :param object facebook_event: Facebook event instance
        """
        # Attempt to patch existing event
        for tribe_event in self.iter_events():
            if tribe_event.facebook_id == facebook_event['id']:
                # Apply patch
                if tribe_event.facebook_digest != facebook_event.digest():
                    return self.patch_event(facebook_event, tribe_event)
                # No op
                return None
        # Add event if no events can be patched
        return self.add_event(facebook_event)

    def sync_events(self, *facebook_events):
        """ Synchronize facebook events with tribe calendar.

            :param tuple facebook_events: Facebook event instances
        """
        for facebook_event in facebook_events:
            self.sync_event(facebook_event)


class TribeEvent(bases.BaseObject):
    """ Tribe Event Object. """
    def __init__(self, service, post, **service_object):
        super(TribeEvent, self).__init__(service, **service_object)
        self.post = post

    @property
    def facebook_id(self):
        """ Helper to return facebook ID of event.

            :returns str: FacebookEvent ID
        """
        facebook_fields = {x['key']: x['value']
                           for x in self.post.custom_fields
                           if x['key'].startswith('facebook_')}
        return facebook_fields.get('facebook_id')

    @property
    def facebook_digest(self):
        """ Helper to return facebook digest of event.

            :returns str: FacebookEvent ID
        """
        facebook_fields = {x['key']: x['value']
                           for x in self.post.custom_fields
                           if x['key'].startswith('facebook_')}
        return facebook_fields.get('facebook_digest')

    @staticmethod
    def from_facebook(facebook_event, service=None, post=None):
        """ Helper to convert a FacebookEvent to a TribeEvent.

            :param object facebook_event: FacebookEvent instance
            :param object service: Optional TribeClient instance
            :param object post: Optional WordPressPost instance
            :returns object: TribeEvent instance
        """
        start_date = facebook_event.start_time().strftime('%Y-%m-%d %H:%M:%S')
        end_date = facebook_event.end_time().strftime('%Y-%m-%d %H:%M:%S')
        return TribeEvent(service,
                          post,
                          title=facebook_event['name'],
                          start_date=start_date,
                          end_date=end_date,
                          description=facebook_event.get('description'),
                          timezone=facebook_event.timezone(),
                          slug=facebook_event['id'])


graph.FacebookEvent.to_tribe = TribeEvent.from_facebook
