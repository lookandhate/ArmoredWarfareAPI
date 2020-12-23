# AW_API

### Unofficial Armored Warfare API

[Версия](https://github.com/lookandhate/ArmoredWarfareAPI/wiki/README.md-RU) для русскоязычных пользователей

## Requirements

`requests` Python package for handling API requests

`beautifulsoup4` Python HTML parser

-------------
`python 3.x` - You need to have Python 3 installed in order to use this

## Installing
Open terminal or command prompt and type ``pip install aw-api`` in order to install
the latest stable version of library from PyPI.


## Usage

1) In order to get access to statistics page you need to get authorized cookies from ``armata.my.games``. You can export
   them using EditThisCookie Chrome extension
   
![cookie export][cookie]

[cookie]: https://github.com/lookandhate/ArmoredWarfareAPI/blob/master/github_readmepage/cookie_export.png 

![cookie.json file example][cookie.json]

[cookie.json]: https://github.com/lookandhate/ArmoredWarfareAPI/blob/master/github_readmepage/cookies.json_example.png 

### Quick example
```python
import json
from aw_api import API

aw_api_client = API(raw_cookie=json.loads(open('cookies.json').read()))

my_pvp_statistics = aw_api_client.get_statistic_by_nickname('MyNickname')

print(
    f'My nickname is {my_pvp_statistics.nickname}, I have played {my_pvp_statistics.battles} in PvP and have '
    f'{my_pvp_statistics.winrate} percents of wins. In average I deal {my_pvp_statistics.damage} per battle and kill {my_pvp_statistics.average_kills} enemies.'
    f'My teammates do {my_pvp_statistics.average_spotting} damage on tanks spotted by me. '
)

```
