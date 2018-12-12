"""
Facebook Events Sync
"""
import pkg_resources

from fest.facebook import FacebookPage
from fest.google import GoogleCalendar

try:
    __version__ = pkg_resources.get_distribution(__package__).version
except pkg_resources.DistributionNotFound:  # pragma: no cover
    __version__ = None                      # pragma: no cover
