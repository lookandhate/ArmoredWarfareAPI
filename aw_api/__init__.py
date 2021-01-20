"""
Armored Warfare API Wrapper
~~~~~~~~~~~~~~~~~~~

Parser simulating API for ArmoredWarfare players statistics.

:copyright: (c) 2020-2021 Dmitriy Trofimov
:license: MIT, see LICENSE for more details.

"""

from .client import API, AW
from .async_client import AIOClient
from .enums import GameMode
from .structs import *

import aw_api.exceptions


__version__ = '2.0.0'
