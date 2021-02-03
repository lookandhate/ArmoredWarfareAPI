import json
import os
import pytest

from aw_api import API, AIOClient
from aw_api.dataobjects import BattalionSearchResultEntry, PlayerStatistics

# TODO: Coverage 95%+ of main API module
if os.getenv('HOME'):
    cookies = json.loads(open('test_cookies.json').read())
else:
    cookies = json.loads(open('cookies.json').read())

client = API(cookies)
aio_client = AIOClient(cookies)


class TestGameMode:
    def test_pvp_ru_account(self):
        player_data = client.get_statistic_by_nickname('IterasuGr1njo', mode=0)
        test_data = PlayerStatistics(winrate=65.6, battles=326, damage=6815.85, clantag=None, nickname='IterasuGr1njo',
                                     average_spotting=613.4325153374233, average_kills=2.25, battalion_full=None,
                                     average_level=8.223926380368098)

        assert test_data == player_data

    def test_pve_ru_account(self):
        player_data = client.get_statistic_by_nickname('IterasuGr1njo', mode=1)
        print(player_data.average_level)
        test_data = PlayerStatistics(winrate=48.7, battles=78, damage=9465.28, clantag=None, nickname='IterasuGr1njo',
                                     average_spotting=1923.128205128205, average_kills=3.4, battalion_full=None,
                                     average_level=7.051282051282051
                                     )

        assert test_data == player_data

    def test_low_ru_account(self):
        player_data = client.get_statistic_by_nickname('IterasuGr1njo', mode=2)
        other_player = client.get_statistic_by_nickname('Googlemen', mode=2)

        test_data_grinjo = PlayerStatistics(winrate=0.0, battles=0, damage=0.0, clantag=None, battalion_full=None,
                                            average_spotting=0.0, average_kills=0.0, average_level=None,
                                            nickname='IterasuGr1njo')

        test_data_google = PlayerStatistics(winrate=87.5, battles=48, damage=2598.97, clantag='R7GEx',
                                            battalion_full='RAGE_Team', average_spotting=900.875, average_kills=1.19,
                                            average_level=7.333333333333333, nickname='Googlemen')
        assert other_player == test_data_google
        assert player_data == test_data_grinjo

    def test_glops_ru_account(self):
        player_data = client.get_statistic_by_nickname('IterasuGr1njo', mode=3)
        test_data = PlayerStatistics(winrate=47.1, battles=34, damage=15336.55, clantag=None, battalion_full=None,
                                     average_spotting=2352.5882352941176, average_kills=4.79,
                                     average_level=8.588235294117647, nickname='IterasuGr1njo')

        assert player_data == test_data


class TestTankAndGameModes:
    def test_pvp_xm1a3(self):
        player_data = client.get_statistic_by_nickname('IterasuGr1njo', mode=0, tank_id=157)
        test_data = PlayerStatistics(winrate=65.6, battles=32, damage=8611.4, clantag=None, battalion_full=None,
                                     average_spotting=422.28125, average_kills=2.81, average_level=None,
                                     nickname='IterasuGr1njo')

        assert player_data == test_data

        # Player with non-null clantag
        player_for_clantag_test = client.get_statistic_by_nickname('Haswell', mode=1, tank_id=3)
        assert player_for_clantag_test.clantag == player_for_clantag_test['clantag'] == 'LABS'

    def test_pve_leo2a4evo(self):
        player_data = client.get_statistic_by_nickname('IterasuGr1njo', mode=1, tank_id=236)
        test_data = PlayerStatistics(winrate=66.7, battles=9, damage=18207.55, clantag=None, battalion_full=None,
                                     average_spotting=3472.4444444444443, average_kills=6.11, average_level=None,
                                     nickname='IterasuGr1njo')

        assert player_data == test_data

        # Player with non-null clantag
        player_for_clantag_test = client.get_statistic_by_nickname('Haswell', mode=1, tank_id=3)
        assert player_for_clantag_test.clantag == player_for_clantag_test['clantag'] == 'LABS'

    # TODO Complete tests for glops and ranked battles


class TestLookForBattalion:
    predefined_data = [
        BattalionSearchResultEntry('RAGE TEAM', 167635),
        BattalionSearchResultEntry('RAGE AGAINST THE MACHINE#1', 275033),
        BattalionSearchResultEntry('161 rus', 287761),
        BattalionSearchResultEntry('Rage Against The Mashine', 292883),
        BattalionSearchResultEntry('RageWolves', 293774),
        BattalionSearchResultEntry('RAGE_Team', 302260),
    ]

    def test_battalion_search(self):
        search_results = client.search_battalion('LABS')
        assert search_results[0].full_name == 'ArmoredLabs'

        multiple_battalions_search_results = client.search_battalion('RAGE')
        assert multiple_battalions_search_results == TestLookForBattalion.predefined_data
