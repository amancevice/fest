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


class TribeAPI(bases.BaseAPI):
    """ WordPress TribeAPI Object.

        :param object service: WordPress XML-RPC Client instance
    """
    @classmethod
    def from_env(cls):
        """ Create CalendarAPI object from ENV variables. """
        return cls.from_credentials()

    @classmethod
    def from_credentials(cls, wordpress_endpoint=None, wordpress_username=None,
                         wordpress_app_password=None, tribe_endpoint=None):
        """ Create CalendarAPI object from credentials

            :param str wordpress_endpoint: WordPress XML-RPC endpoint
            :param str wordpress_username: WordPress XML-RPC username
            :param str wordpress_app_password: WordPress XML-RPC app password
            :param str tribe_endpoint: Tribe REST API endpoint
        """
        service = wp.Client(wordpress_endpoint or WORDPRESS_ENDPOINT,
                            wordpress_username or WORDPRESS_USERNAME,
                            wordpress_app_password or WORDPRESS_APP_PASSWORD)
        service.tribe_endpoint = tribe_endpoint or TRIBE_ENDPOINT
        return cls(service)

    def add_event(self, source_event):
        """ Add event.

            :param object source_event: Event instance
        """
        event = source_event.to_tribe()
        post = event['post']
        tribe_event = event['tribe_event']

        # Create WordPress post
        request = wp.methods.posts.NewPost(post)
        self.logger.info('CREATE %s', source_event['id'])
        post.id = self.service.call(request)

        # Create tribe event
        tribe_endpoint = "{}/events/{}".format(self.service.tribe_endpoint,
                                               post.id)
        self.logger.info('POST %s', tribe_endpoint)
        return requests.post(tribe_endpoint,
                             headers=self.basic_auth(),
                             json=tribe_event)

    def basic_auth(self):
        """ Helper to get basic auth header. """
        auth = "{}:{}".format(self.service.username, self.service.password)
        token = base64.standard_b64encode(auth.encode('utf-8'))
        return {'Authorization': 'Basic {}'.format(token.decode('utf-8'))}

    def delete_event(self, post_id):
        """ Delete event.

            :param str post_id: WordPress post ID
        """
        # Delete tribe event
        tribe_endpoint = "{}/events/{}".format(self.service.tribe_endpoint,
                                               post_id)
        self.logger.info('DELETE %s', tribe_endpoint)
        requests.delete(tribe_endpoint, headers=self.basic_auth())

        # Delete WordPress post
        return self.delete_post(post_id)

    def delete_post(self, post_id):
        """ Delete tribe event post by post_id.

            :param str post_id: WordPress post ID
        """
        request = wp.methods.posts.DeletePost(post_id)
        self.logger.info('DELETE %s', post_id)
        return self.service.call(request)

    def get_event(self, post_id):
        """ Get tribe event post by post_id.

            :param str post_id: WordPress post ID
        """
        post = self.get_post(post_id)
        tribe_endpoint = "{}/events/{}".format(self.service.tribe_endpoint,
                                               post_id)
        self.logger.info('GET %s', tribe_endpoint)
        response = requests.get(tribe_endpoint, headers=self.basic_auth())
        tribe_event = response.json()
        return TribeEvent(self, post=post, tribe_event=tribe_event)

    def get_events(self, **kwargs):
        """ Get events in calendar.

            :returns list[object]: List of WordPressPost instances
        """
        return list(self.iter_events(**kwargs))

    def get_post(self, post_id):
        """ Get tribe event post by post_id.

            :param str post_id: WordPress post ID
        """
        request = wp.methods.posts.GetPost(post_id)
        self.logger.info('GET %s', post_id)
        post = self.service.call(request)
        body = {k: v for k, v in post.struct.items() if v is not None}
        return WordPressPost(body)

    def get_posts(self, **kwargs):
        """ Get list of tribe event posts. """
        return list(self.iter_posts(**kwargs))

    def iter_events(self, **kwargs):
        """ Iterate over all Google Calendar events. """
        for post in self.iter_posts(**kwargs):
            tribe_endpoint = "{}/events/{}".format(self.service.tribe_endpoint,
                                                   post.id)
            self.logger.info('GET %s', tribe_endpoint)
            response = requests.get(tribe_endpoint, headers=self.basic_auth())
            tribe_event = response.json()
            yield TribeEvent(self, post=post, tribe_event=tribe_event)

    def iter_posts(self, **kwargs):
        """ Iterate over tribe event posts. """
        # Get pages in batches of 100
        kwargs.setdefault('post_type', 'tribe_events')
        kwargs.setdefault('number', 100)
        kwargs.setdefault('offset', 0)
        while True:
            request = wp.methods.posts.GetPosts(kwargs)
            self.logger.info('GET %s', kwargs)
            posts = self.service.call(request)
            if not any(posts):
                break  # no more posts returned
            for post in posts:
                body = {k: v for k, v in post.struct.items() if v is not None}
                yield WordPressPost(body)
            kwargs['offset'] = kwargs['offset'] + kwargs['number']

    def patch_event(self, post, source_event):
        """ Patch event.

            :param str post: WordPressPost instance
            :param object source_event: Event instance
        """
        # Patch digest
        for field in post.custom_fields:
            if field['key'] == 'facebook_digest':
                field['value'] = source_event.digest()
        request = wp.methods.posts.EditPost(post.id, post)
        self.logger.info('EDIT %s :: %s', post.id, source_event['id'])
        if self.service.call(request):
            event = source_event.to_tribe()
            tribe_event = event['tribe_event']
            tribe_endpoint = "{}/events/{}".format(self.service.tribe_endpoint,
                                                   post.id)
            self.logger.info('POST %s', tribe_endpoint)
            return requests.post(tribe_endpoint,
                                 headers=self.basic_auth(),
                                 json=tribe_event)
        self.logger.error('ERROR %s :: %s', post.id, source_event['id'])
        return None

    def sync_event(self, source_event):
        """ Synchronize event with tribe.

            :param object source_event: Event instance
        """
        # Attempt to patch existing event
        for post in self.iter_posts():
            if post.source_id == source_event.source_id:
                # Apply patch
                if post.source_digest != source_event.digest():
                    return self.patch_event(post, source_event)
                # No op
                self.logger.debug('NO-OP %s :: %s',
                                  post.id,
                                  source_event.source_id)
                return None
        # Add event if no events can be patched
        return self.add_event(source_event)

    def sync_events(self, source_events, force=False, dryrun=False):
        """ Synchronize events with calendar.

            :param dict source_events: Source event dictionary
            :param bool force: Force patching without checking digest
            :param bool dryrun: Toggle execute batch request
        """
        postmap = {x.source_id: x for x in self.iter_posts()}

        upcoming = source_events.get('upcoming') or []
        canceled = source_events.get('canceled') or []

        # Add or patch events
        for source_event in upcoming:
            # Patch event if digests differ (otherwise no op)
            if source_event.source_id in postmap:
                post = postmap[source_event.source_id]
                if force or post.source_digest != source_event.digest():
                    if dryrun is False:
                        self.patch_event(post, source_event)
                    else:
                        self.logger.debug('DRYRUN PATCH %s :: %s',
                                          post.id,
                                          source_event.source_id)
                else:
                    self.logger.debug('NO-OP %s :: %s',
                                      post.id,
                                      source_event.source_id)

            # Insert new event
            else:
                if dryrun is False:
                    self.add_event(source_event)
                else:
                    self.logger.debug('DRYRUN CREATE %s',
                                      source_event.source_id)

        # Delete canceled events
        for source_event in canceled:
            # Ignore events not in the postmap
            if source_event.source_id in postmap:
                post = postmap[source_event.source_id]
                if dryrun is False:
                    self.delete_event(post)
                else:
                    self.logger.info('DRYRUN DELETE %s :: %s',
                                     post.id,
                                     source_event.source_id)


class WordPressPost(wp.WordPressPost):
    """ WordPressPost object. """
    def __init__(self, xmlprc=None):
        super(WordPressPost, self).__init__(xmlprc)
        for env in os.environ:
            if env.startswith('WP_CUSTOM_FIELD_'):
                key = env.replace('WP_CUSTOM_FIELD_', '').lower()
                value = os.getenv(env)
                self.set_custom_field(key, value)

    @property
    def source_fields(self):
        """ Get custom facebook fields.

            :returns dict: {'facebook_<key>': '<value>'}
        """
        return {x['key']: x['value'] for x in self.struct['custom_fields']
                if x['key'].startswith('facebook_')}

    @property
    def source_id(self):
        """ Helper to return facebook ID of event.

            :returns str: FacebookEvent ID
        """
        return self.source_fields.get('facebook_id')

    @property
    def source_digest(self):
        """ Helper to return facebook digest of event.

            :returns str: FacebookEvent ID
        """
        return self.source_fields.get('facebook_digest')

    def set_custom_field(self, key, value):
        """ Helper to set/update custom field. """
        # pylint: disable=no-member
        keys = {x['key']: i for i, x in enumerate(self.custom_fields)}
        if key in keys:
            self.custom_fields[keys[key]]['value'] = value
        else:
            self.custom_fields.append({'key': key, 'value': value})


class TribeEvent(bases.BaseObject):
    """ WordPressPost object.
    """
    @staticmethod
    def from_facebook(facebook_event, service=None):
        """ Helper to convert a FacebookEvent to a WordPressPost.

            :param object facebook_event: FacebookEvent instance
            :param object service: Optional TribeAPI service instance
            :returns object: WordPressPost instance
        """
        # WordPress post
        post = WordPressPost({
            'custom_fields': [
                {'key': 'facebook_id', 'value': facebook_event['id']},
                {'key': 'facebook_digest', 'value': facebook_event.digest()}],
            'post_status': 'publish',
            'post_type': 'tribe_events',
            'slug': facebook_event['id'],
            'title': facebook_event['name']})

        # Tribe Event
        image_url = facebook_event.get('cover', {}).get('source')
        desc = facebook_event.get('description') or facebook_event.get('name')
        if image_url and desc:
            desc = '<img src="{}"/>\n'.format(image_url) + desc
        start_date = facebook_event.start_time().strftime('%Y-%m-%d %H:%M:%S')
        end_date = facebook_event.end_time().strftime('%Y-%m-%d %H:%M:%S')
        tribe_event = {'description': desc,
                       'end_date': end_date,
                       'slug': facebook_event.get('id'),
                       'start_date': start_date,
                       'timezone': facebook_event.timezone(),
                       'title': facebook_event.get('name'),
                       'website': facebook_event.url}
        return TribeEvent(service, post=post, tribe_event=tribe_event)


graph.FacebookEvent.to_tribe = TribeEvent.from_facebook
