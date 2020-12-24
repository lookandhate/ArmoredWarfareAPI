import json
import os
from aw_api import API

# TODO: Coverage 95%+ of main API module
if os.getenv('HOME'):
    cookies = json.loads(open('test_cookies.json').read())
else:
    cookies = json.loads(open('cookies.json').read())

client = API(cookies)


class TestGameMode:
    def test_pvp_ru_account(self):
        player_data = client.get_statistic_by_nickname('IterasuGr1njo', mode=0)

        assert player_data['winrate'] == player_data.winrate == 65.6
        assert player_data['battles'] == player_data.battles == 326
        assert player_data['damage'] == player_data.damage == 6815.85
        assert player_data['clantag'] is player_data.clantag is None
        assert player_data['nickname'] == player_data.nickname == 'IterasuGr1njo'
        assert player_data['average_spotting'] == player_data.average_spotting == 613.4325153374233
        assert player_data['average_kills'] == player_data.average_kills == 2.25

    def test_pve_ru_account(self):
        player_data = client.get_statistic_by_nickname('IterasuGr1njo', mode=1)

        assert player_data['winrate'] == player_data.winrate == 48.7
        assert player_data['battles'] == player_data.battles == 78
        assert player_data['damage'] == player_data.damage == 9465.28
        assert player_data['clantag'] is player_data.clantag is None
        assert player_data['nickname'] == player_data.nickname == 'IterasuGr1njo'
        assert player_data['average_spotting'] == player_data.average_spotting == 1923.128205128205
        assert player_data['average_kills'] == player_data.average_kills == 3.4

    def test_low_ru_account(self):
        player_data = client.get_statistic_by_nickname('IterasuGr1njo', mode=2)
        other_player = client.get_statistic_by_nickname('Googlemen', mode=2)

        assert other_player['winrate'] == other_player.winrate == 87.5
        assert other_player['battles'] == other_player.battles == 48
        assert other_player['damage'] == other_player.damage == 2598.97
        assert other_player['average_spotting'] == other_player.average_spotting == 900.875
        assert other_player['average_kills'] == other_player.average_kills == 1.19

        assert player_data['winrate'] == player_data.winrate == 0
        assert player_data['battles'] == player_data.battles == 0
        assert player_data['damage'] == player_data.damage == 0
        assert player_data['clantag'] is player_data.clantag is None
        assert player_data['nickname'] == player_data.nickname == 'IterasuGr1njo'

    def test_glops_ru_account(self):
        player_data = client.get_statistic_by_nickname('IterasuGr1njo', mode=3)

        assert player_data['winrate'] == player_data.winrate == 47.1
        assert player_data['battles'] == player_data.battles == 34
        assert player_data['damage'] == player_data.damage == 15336.55
        assert player_data['clantag'] is player_data.clantag is None
        assert player_data['nickname'] == player_data.nickname == 'IterasuGr1njo'
        assert int(player_data['average_spotting']) == 2352
        assert player_data['average_kills'] == 4.79


class TestTankAndGameModes:
    def test_pvp_xm1a3(self):
        player_data = client.get_statistic_by_nickname('IterasuGr1njo', mode=0, tank_id=157)
        assert player_data.winrate == player_data['winrate'] == 65.6
        assert player_data.battles == player_data['battles'] == 32
        assert player_data.damage == player_data['damage'] == 8611.4
        assert player_data.clantag is player_data['clantag'] is None
        assert player_data.average_spotting == player_data['average_spotting'] == 422.28125
        assert player_data.average_kills == player_data['average_kills'] == 2.81
        assert player_data.average_level is player_data['average_level'] is None
        assert player_data.nickname == player_data['nickname'] == 'IterasuGr1njo'

        # Player with non-null clantag
        player_for_clantag_test = client.get_statistic_by_nickname('Haswell', mode=1, tank_id=3)
        assert player_for_clantag_test.clantag == player_for_clantag_test['clantag'] == 'LABS'

    def test_pve_leo2a4evo(self):
        player_data = client.get_statistic_by_nickname('IterasuGr1njo', mode=1, tank_id=236)
        assert player_data.winrate == player_data['winrate'] == 66.7
        assert player_data.battles == player_data['battles'] == 9
        assert player_data.damage == player_data['damage'] == 18207.55
        assert player_data.clantag is player_data['clantag'] is None
        assert player_data.average_spotting == player_data['average_spotting'] == 3472.4444444444443
        assert player_data.average_kills == player_data['average_kills'] == 6.11
        assert player_data.average_level is player_data['average_level'] is None
        assert player_data.nickname == player_data['nickname'] == 'IterasuGr1njo'

        # Player with non-null clantag
        player_for_clantag_test = client.get_statistic_by_nickname('Haswell', mode=1, tank_id=3)
        assert player_for_clantag_test.clantag == player_for_clantag_test['clantag'] == 'LABS'

    # TODO Complete tests for glops and ranked battles


class TestLookForBattalion:
    multiple_battalion_search_test_data = {167635: 'RAGE TEAM', 275033: 'RAGE AGAINST THE MACHINE#1', 287761: '161 rus',
                                           292883: 'Rage Against The Mashine', 293774: 'RageWolves',
                                           302260: 'RAGE_Team'}  # Search by RAGE word

    def test_battalion_search(self):
        search_results = client.search_battalion('LABS')
        assert search_results[335779] == 'ArmoredLabs'

        multiple_battalions_search_results = client.search_battalion('RAGE')
        assert multiple_battalions_search_results == TestLookForBattalion.multiple_battalion_search_test_data

