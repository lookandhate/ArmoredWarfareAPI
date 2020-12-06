# AW_API

### An Armored Warfare API wrapper for python

## Requirements

`requests` Python package for handling API requests

`beautifulsoup4` Python HTML parser

-------------
`python 3.x` - You need to have Python 3 installed in order to use this

## Installing
Open terminal or command prompt and type ``pip install git+https://github.com/lookandhate/ArmoredWarfareAPI.git`` in order to install library from github.

Maybe there will be a PyPI package later.


## Usage

1) In order to get access to statistics page you need to get authorized cookies from ``armata.my.games``. You can export
   them using EditThisCookie chrome extension
   
![cookie export][cookie]

[cookie]: https://github.com/lookandhate/ArmoredWarfareAPI/blob/master/github_readmepage/cookie_export.png 

![cookie.json file example][cookie.json]

[cookie.json]: https://github.com/lookandhate/ArmoredWarfareAPI/blob/master/github_readmepage/cookies.json_example.png 

```python
from aw_api.api import AW

__cookies = dict()  # Your cookies
aw_stats = AW(__cookies)

my_stats = aw_stats.get_statistic_by_nickname(nickname='MyNickname')
print(
    'My winrate: {0}\nMy average damage: {1}\nI have played {2} battles'.format(my_stats['winrate'], my_stats['damage'],
                                                                                my_stats['battles']))



```

2) You can specify the game mode from which you want to get statistics by changing ``mode`` keyword.

```python
aw_stats.get_statistic_by_nickname(nickname='MyNickname', mode=mode_id)
``` 

where ``mode_id`` is integer indicates id of gamemode(it's 0 for PvP, 1 for PvE, 2 for LoW(lords of war - old game mode
that was ripped off), 3 for GLoPS and 4 for Ranked Battles)

So if you want to get your PvE stats just pass ``mode=1`` in function like this

```python
my_pve_statistics = aw_stats.get_statistic_by_nickname(nickname='MyNickname', mode=1)
print("I've played {0} battles in PvE, won {1} battles of 100 and deal {2} damage in average".format(
    my_pve_statistics['battles'], my_pve_statistics['winrate'], my_pve_statistics['damage']))
```

3) You can specify tank too: just pass ``tank_id`` key-word parameter.
```python
my_glops_statistics = aw_stats.get_statistic_by_nickname(nickname='MyNickname', mode=3, tank_id=157)
print("I've played {0} battles in PvE on XM1A3, won {1} battles of 100 and deal {2} damage in average".format(
    my_glops_statistics['battles'], my_glops_statistics['winrate'], my_glops_statistics['damage']))
```
Code Above will print your GLoPS statistics on XM1A3

*I can't provide IDs for all tanks in the game for now, but you can dig them in Game.log or from source code of statistic page at armata.my.games*


