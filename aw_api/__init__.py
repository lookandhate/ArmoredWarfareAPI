"""
Armored Warfare API Wrapper
~~~~~~~~~~~~~~~~~~~

Parser simulating API for ArmoredWarfare players statistics.

:copyright: (c) 2020-2021 Dmitriy Trofimov
:license: MIT, see LICENSE for more details.

"""
try:
    from .client import API, AW
except Exception:
    pass
from .async_client import AIOClient
from .enums import GameMode
from .dataobjects import *

import aw_api.exceptions

__version__ = '2.0.3'
