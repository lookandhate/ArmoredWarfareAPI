"""
Armored Warfare API Wrapper
~~~~~~~~~~~~~~~~~~~

Parser simulating API for ArmoredWarfare players statistics.

:copyright: (c) 2020 lookandhate
:license: MIT, see LICENSE for more details.

"""

from .api import API, AW
from .api import GameMode
from .player import Player
from .battalion import BattalionMemberEntry, BattalionSearchResult

import aw_api.exceptions
