import json
import os
from aw_api import API

if os.getenv('HOME'):
    cookies = json.loads(open('test_cookies.json').read())
else:
    cookies = json.loads(open('cookies.json').read())

client = API(cookies)

test_data = {
    'battalion_players_348473': [{'id': 622893703, 'nickname': 'iLuvSasha'}]
}


def test_pvp():
    player_data = client.get_statistic_by_nickname('IterasuGr1njo', mode=0)

    assert player_data['winrate'] == 65.6
    assert player_data['battles'] == 326
    assert player_data['damage'] == 6815.85
    assert player_data['clantag'] is None
    assert player_data['nickname'] == 'IterasuGr1njo'
    assert player_data['average_spotting'] == 613.4325153374233
    assert player_data['average_kills'] == 2.25


def test_pve():
    player_data = client.get_statistic_by_nickname('IterasuGr1njo', mode=1)

    assert player_data['winrate'] == 48.7
    assert player_data['battles'] == 78
    assert player_data['damage'] == 9465.28
    assert player_data['clantag'] is None
    assert player_data['nickname'] == 'IterasuGr1njo'
    assert player_data['average_spotting'] == 1923.128205128205
    assert player_data['average_kills'] == 3.4


def test_low():
    player_data = client.get_statistic_by_nickname('IterasuGr1njo', mode=2)
    other_player = client.get_statistic_by_nickname('Googlemen', mode=2)

    assert other_player['winrate'] == 87.5
    assert other_player['battles'] == 48
    assert other_player['damage'] == 2598.97
    assert other_player['average_spotting'] == 900.875
    assert other_player['average_kills'] == 1.19

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
    assert int(player_data['average_spotting']) == 2352
    assert player_data['average_kills'] == 4.79


def disabled_test_battalion(): # This test has been disabled because battalion with id = 348473 does not exist anymore
    data = client.get_battalion_players(348473)
    assert data == test_data['battalion_players_348473']


test_pvp()