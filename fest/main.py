"""
CLI Entrypoint
"""
import click
from fest import __version__
from fest import graph as facebook
from fest import google


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__, '-v', '--version')
@click.option('--facebook-app-id',
              envvar='FACEBOOK_APP_ID',
              help='TODO')
@click.option('--facebook-app-secret',
              envvar='FACEBOOK_APP_SECRET',
              help='TODO')
@click.option('--google-account-type',
              envvar='GOOGLE_ACCOUNT_TYPE',
              help='TODO')
@click.option('--google-client-email',
              envvar='GOOGLE_CLIENT_EMAIL',
              help='TODO')
@click.option('--google-client-id',
              envvar='GOOGLE_CLIENT_ID',
              help='TODO')
@click.option('--google-private-key',
              envvar='GOOGLE_PRIVATE_KEY',
              help='TODO')
@click.option('--google-private-key-id',
              envvar='GOOGLE_PRIVATE_KEY_ID',
              help='TODO')
@click.option('--google-scope',
              envvar='GOOGLE_SCOPE',
              help='TODO')
@click.pass_context
def fest(ctx, facebook_app_id, facebook_app_secret, google_account_type,
         google_client_email, google_client_id, google_private_key,
         google_private_key_id, google_scope):
    """ Export Facebook Page Events to other services.

        See https://github.com/amancevice/fest for details & instructions.
    """
    # pylint: disable=too-many-arguments
    ctx.obj = {}
    ctx.obj['graph'] = facebook.GraphAPI(app_id=facebook_app_id,
                                         app_secret=facebook_app_secret)
    ctx.obj['cloud'] = google.CalendarAPI(scopes=[google_scope],
                                          service_type=google_account_type,
                                          private_key_id=google_private_key_id,
                                          private_key=google_private_key,
                                          client_email=google_client_email,
                                          client_id=google_client_id)


@fest.command('clear')
@click.option('-f', '--force',
              default=False,
              is_flag=True,
              prompt='Are you sure?')
@click.option('-g', '--google-id',
              envvar='GOOGLE_CALENDAR_ID',
              help='Google Calendar ID')
@click.pass_context
def fest_clear(ctx, force, google_id):
    """ Clear a linked Google Calendar. """
    cloud = ctx.obj['cloud']
    gcal = cloud.get_calendar(google_id)
    if force is True:
        gcal.clear_events()


@fest.command('sync')
@click.option('-f', '--facebook-id',
              envvar='FACEBOOK_PAGE_ID',
              help='Facebook Page ID')
@click.option('-g', '--google-id',
              envvar='GOOGLE_CALENDAR_ID',
              help='Google Calendar ID')
@click.option('-a', '--sync-all',
              help='Sync all events, not just upcoming',
              is_flag=True)
@click.pass_context
def fest_sync(ctx, facebook_id, google_id, sync_all):
    """ Sync a facebook page. """
    click.echo('Fetching Google Events: {}'.format(google_id))
    gcal = ctx.obj['cloud'].get_calendar(google_id)
    gevents = gcal.get_events()

    click.echo('Fetching Facebook Events: {}'.format(facebook_id))
    page = ctx.obj['graph'].get_page(facebook_id)
    time_filter = None if sync_all else 'upcoming'
    events = page.get_events(time_filter=time_filter)

    click.echo('Merging Events')
    gids = set(x.facebook_id for x in gevents)
    fids = set(x['id'] for x in events if x['id'] not in gids)
    sync = [x for x in events if x['id'] in fids]

    click.echo('Syncing {} Events'.format(len(sync)))
    for event in sync:
        click.echo('-> {} :: {} :: {}'.format(event['start_time'],
                                              event['id'],
                                              event['name']))
        gcal.add_event(event)


if __name__ == '__main__':
    fest()  # pylint: disable=no-value-for-parameter
