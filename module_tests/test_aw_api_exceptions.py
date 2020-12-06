import os

import pytest
import json

from aw_api import API
from aw_api import NotAuthException, UserNotFoundException, UserHasClosedStatisticsException, BattalionNotFound

if os.getenv('HOME'):
    cookies = json.loads(open('test_cookies.json').read())
else:
    cookies = json.loads(open('cookies.json').read())

bad_cookies = json.loads(open('bad_credentials_client.json').read())

authenticated_client = API(cookies)
not_authenticated_client = API()
bad_credentials_client = API(bad_cookies)


def test_player_not_found_exception():
    with pytest.raises(UserNotFoundException):
        authenticated_client.get_statistic_by_nickname('1')


def test_battalion_does_not_exist():
    with pytest.raises(BattalionNotFound):
        authenticated_client.get_battalion_players(1)


def test_statistics_is_closed():
    with pytest.raises(UserHasClosedStatisticsException):
        authenticated_client.get_statistic_by_nickname('Tuka_Chinchilla')


def test_not_auth_player_statistics():
    with pytest.raises(NotAuthException):
        not_authenticated_client.get_statistic_by_nickname('Tuka_Chinchilla')


def test_not_auth_battalion_players():
    with pytest.raises(NotAuthException):
        not_authenticated_client.get_battalion_players(273749)


def test_bad_cred_player_statistics():
    with pytest.raises(NotAuthException):
        bad_credentials_client.get_statistic_by_nickname('Tuka_Chinchilla')


def testbad_cred_battalion_players():
    with pytest.raises(NotAuthException):
        bad_credentials_client.get_battalion_players(273749)
