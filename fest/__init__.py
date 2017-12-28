"""
Facebook Events Sync
"""
import pkg_resources
from fest.graph import GraphAPI
try:
    from fest.google import GoogleCloud
except ImportError:
    pass
try:
    from fest.tribe import TribeCalendar
except ImportError:
    pass

try:
    __version__ = pkg_resources.get_distribution(__package__).version
except pkg_resources.DistributionNotFound:  # pragma: no cover
    __version__ = None                      # pragma: no cover
