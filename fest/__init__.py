"""
Facebook Events Sync
"""
import pkg_resources

from fest.facebook import FacebookPage  # noqa: F401
from fest.google import GoogleCalendar  # noqa: F401

try:
    __version__ = pkg_resources.get_distribution(__package__).version
except pkg_resources.DistributionNotFound:  # pragma: no cover
    __version__ = None                      # pragma: no cover
