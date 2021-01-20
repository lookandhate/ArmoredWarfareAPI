"""
Armored Warfare API Wrapper
~~~~~~~~~~~~~~~~~~~

Parser simulating API for ArmoredWarfare players statistics.

:copyright: (c) 2020-2021 Dmitriy Trofimov
:license: MIT, see LICENSE for more details.

"""

from .api import API, AW
from .api import GameMode
from .player import Player
from .battalion import BattalionMemberEntry, BattalionSearchResultEntry

from .async_client import AIOClient

import aw_api.exceptions


__version__ = '1.4.0'
