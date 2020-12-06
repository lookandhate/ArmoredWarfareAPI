import json
import os
from aw_api import API
if os.getenv('LARGE_SECRET_PASSPHRASE'):
    cookies = json.loads(open('/home/runner/work/ArmoredWarfareAPI/ArmoredWarfareAPI/test_cookies.json').read())
else:
    cookies = json.loads(open('cookies.json').read())

raise Exception(os.getenv('LARGE_SECRET_PASSPHRASE'))

client = aw_api.API(cookies)

test_data = {
    'battalion_players_0': [{'id': 622893703, 'nickname': 'iLuvSasha'}]
}


def test_general():
    player_data = client.get_statistic_by_nickname('IterasuGr1njo', mode=0)

    assert player_data['winrate'] == 65.6
    assert player_data['battles'] == 326
    assert player_data['damage'] == 6815.85
    assert player_data['clantag'] is None
    assert player_data['nickname'] == 'IterasuGr1njo'


def test_pve():
    player_data = client.get_statistic_by_nickname('IterasuGr1njo', mode=1)

    assert player_data['winrate'] == 48.7
    assert player_data['battles'] == 78
    assert player_data['damage'] == 9465.28
    assert player_data['clantag'] is None
    assert player_data['nickname'] == 'IterasuGr1njo'


def test_low():
    player_data = client.get_statistic_by_nickname('IterasuGr1njo', mode=2)
    other_player = client.get_statistic_by_nickname('Googlemen', mode=2)

    assert other_player['winrate'] == 87.5
    assert other_player['battles'] == 48
    assert other_player['damage'] == 2598.97

    assert player_data['winrate'] == 0
    assert player_data['battles'] == 0
    assert player_data['damage'] == 0
    assert player_data['clantag'] is None
    assert player_data['nickname'] == 'IterasuGr1njo'


def test_glops():
    player_data = client.get_statistic_by_nickname('IterasuGr1njo', mode=3)

    assert player_data['winrate'] == 47.1
    assert player_data['battles'] == 34
    assert player_data['damage'] == 15336.55
    assert player_data['clantag'] is None
    assert player_data['nickname'] == 'IterasuGr1njo'


test_glops()
