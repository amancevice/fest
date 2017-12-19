"""
Facebook Events Sync
"""
import pkg_resources
from fest.graph import GraphAPI
from fest.google import CalendarAPI

try:
    __version__ = pkg_resources.get_distribution(__package__).version
except pkg_resources.DistributionNotFound:  # pragma: no cover
    __version__ = None                      # pragma: no cover
