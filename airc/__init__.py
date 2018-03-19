"""
    Asynchronous IRC module. Provides ways to handle individual servers, multiple servers,
    and a built in client and bot framework. Handles twitch and general IRC protocol
    'out of the box'.

    :copyright: (c) 2018 CraftSpider
    :license: MIT, see LICENSE for details.
"""

import logging

from .master import ServerMaster
from .events import Event, numeric
from .enums import UserType
from .errors import *
from .server import TwitchServer
from .client import TwitchClient
from .bot import *

__title__ = "airc"
__author__ = "CraftSpider"
__license__ = "MIT"
__copyright__ = "Copyright 2018 CraftSpider"
__version__ = "0.1.0"

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
