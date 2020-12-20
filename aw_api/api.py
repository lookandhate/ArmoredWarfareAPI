"""
MIT License

Copyright (c) 2020 lookandhate

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import re
import requests
import logging

from typing import Union, Dict, List, NamedTuple, Optional
from collections import namedtuple
from bs4 import BeautifulSoup, Tag

from .exceptions import UserHasClosedStatisticsException, UserNotFoundException, BadHTTPStatusCode, NotAuthException, \
    BattalionNotFound

logger = logging.getLogger(__name__)

__PlayerStatistics__ = namedtuple('PlayerStatistics',
                                  ['winrate', 'battles', 'damage', 'clantag', 'average_spotting', 'average_kills',
                                   'average_level', 'nickname'])


class PlayerStatistics(NamedTuple):
    import sys
    winrate: float
    battles: int
    damage: float
    clantag: Optional[str]
    average_spotting: float
    average_kills: float
    average_level: Optional[float]
    nickname: str
    if sys.version_info >= (3, 8, 0):
        def __getitem__(self, item):
            if isinstance(item, str):
                return getattr(self, item)
            return NamedTuple.__getitem__(self, item)
    else:
        def __getitem__(self, item):
            if isinstance(item, str):
                return getattr(self, item)
            return self._asdict()[item]

    def get(self, item, default=None):
        try:
            return self[item]
        except (KeyError, AttributeError):
            return default


class API:
    def __init__(self, raw_cookie: Union[Dict, List] = None):
        """
        :param raw_cookie :class:`Union[Dict, List]`
         containing exported with "EditThisCookie" Chrome extension cookie from aw.mail.ru
        """

        # Paragraph that shows if we are not authenticated on site
        self.__NOT_AUTH_CHECK = [
            '<p>Для просмотра данной страницы вам необходимо авторизоваться или <a href="/user/register/">зарегистрироваться</a> на сайте.</p>',
            '<p>Для просмотра данной страницы вам необходимо авторизоваться или <a href="" onclick="__GEM.showSignup();return false;" target="_blank">зарегистрироваться</a> на сайте.</p>'
        ]
        self.__NOT_AUTH_CHECK_BATTALION = '<div class="node_notice warn border">Необходимо авторизоваться.</div>'
        # Div with text shows that user closed his statistics
        self.__CLOSED_STAT = '<div class="node_notice warn border">Пользователь закрыл доступ!</div>'
        # Div with text shows that player with given nickname does not exist
        self.__PLAYER_NOT_EXISTS = '<div class="node_notice warn border">Пользователь не найден!</div>'

        # Base URL for player statistics
        self.__user_stats_url = 'https://armata.my.games/dynamic/user/?a=stats'
        # Base URL for battalion page
        self.__battalion_stats_url = 'https://armata.my.games/dynamic/aliance/index.php?a=index'

        # Session that will contain cookies
        self.__session: requests.Session = requests.Session()
        # Dict with cookies
        self.__cookie: Union[Dict, List, None] = None

        if raw_cookie:
            self.__cookie = self.__prepare_cookie(raw_cookie)

    # Clean HTML from tags to extract only data
    @staticmethod
    def __clean_html(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    @classmethod
    def __extract_battles_per_level(cls, level_stats: List[Tag]) -> List[int]:
        battles = []
        for item in level_stats:
            children = list(item.children)
            battles.append(int(cls.__clean_html(str(children[-2]))))
        return battles

    @staticmethod
    def _calculate_average_level(level_stats: List[int]) -> int:
        total_sum = 0
        for index, item in enumerate(level_stats, 1):
            total_sum += index * item
        return total_sum

    @staticmethod
    def __prepare_cookie(raw_cookie: Union[Dict, List]) -> Dict:
        """
        :param raw_cookie :class:`Union[Dict, List]`: Raw cookie from EditThisCookie

        :return: :class:`dict` with "cleaned" cookies
        """

        new_cookie_dict = dict()
        for item in raw_cookie:
            new_cookie_dict[item['name']] = item['value']
        return new_cookie_dict

    def __get_page(self, url: str) -> str:
        """
        :param url :class:`str` URL to retrieve.

        :return: :class:`str` That contains decoded HTML page
        """
        logger.info('Performing request to {0}'.format(url))

        request = self.__session.get(url, cookies=self.__cookie)
        if request.status_code == 200:
            page = request.content.decode('utf-8')
            return page
        logger.error('Got non 200 status code on request to {0}. Status code: {1}'.format(url, request.status_code))
        raise BadHTTPStatusCode(f'Got non 200 status code: {request.status_code}', status_code=request.status_code)

    def __get_player_statistic_page(self, nickname: str, mode: int, data: int, tank_id: id, day: int = 0,
                                    ajax: int = 0, maintype: int = 0) -> str:
        """
        :param nickname: Nickname of user to find.
        :param mode: Game mode Number from 0 to 4 {pvp, pve, low, glops, ranked}.
        :param data: CSA ID of player to find(overwrites user nickname) if not 0.
        :param tank_id: staticID of tank to find for(0 means overall stat for mode).
        :param day: Filter stats by some date/battle count.
        :param ajax: Is data should be returned like in ajax request (DONT CHANGE IT OR WILL BROKE).
        :param maintype: In-game type of vehicle(0 all types, 1 - MBT, 2 - LT, 3 - TD, 4 - AFV)

        :return: string with decoded HTML page

        """

        url = f'{self.__user_stats_url}&name={nickname}&mode={mode}&data={data}&type={tank_id}&maintype={maintype}&day={day}&ajax={ajax}'
        page = self.__get_page(url)
        return page

    def __get_player_statistics(self, page: str, nickname=None) -> PlayerStatistics:
        """
        :param page: string with HTML document

        :return: dict with user data, where
        winrate: float - Player win rate in percents
        battles: int - Total player battles
        damage: float - Player average damage
        clantag: Optional[str] - player battalion tag (can be None)
        nickname: str - Correct player nickname
        """

        # Let's parse the page
        page_parser = BeautifulSoup(page, "html.parser")
        notifications = list(page_parser.find_all('p'))

        if not notifications:
            notifications = page_parser.find_all('div')
        notifications = list(notifications)

        # Check if we authenticated (if not, then notifications[0] will be equal to one of items in NOT_AUTH_CHECK )
        if str(notifications[0]) in self.__NOT_AUTH_CHECK:
            logger.error('Error on parsing page: Client is not authenticated')
            raise NotAuthException('I am not authenticated on aw.mail.ru')

        # Check if user exists( if user does not exist, then notifications[0] will be equal to PLAYER_NOT_EXISTS )
        if self.__PLAYER_NOT_EXISTS == str(notifications[0]):
            logger.warning('Player {} was not found'.format(nickname))
            raise UserNotFoundException(f'User {nickname} nickname was not found', nickname=nickname)

        # Check did user closed stats
        if '<div class="node_notice warn border">Пользователь закрыл доступ!</div>' == str(notifications[0]):
            logger.warning('Player {} has closed his statistics'.format(nickname))
            raise UserHasClosedStatisticsException(f'{nickname} closed his stats', nickname=nickname)

        nickname = self.__clean_html(str(page_parser.find("div", {"class": "name"}))).split('\n')[1]
        battalion = page_parser.find('div', {'class': 'clan'})
        battalion = str(battalion.contents[3]).split()
        battalion = battalion[0].replace('<span>', '').replace('[', '').replace(']', '')
        if len(battalion) == 0:
            battalion = None

        battles_played = str(page_parser.find("div", {"class": "total"}))
        battles_played = self.__clean_html(battles_played).split()[-1].replace('сыграно', '')
        battles_played = int(battles_played) if battles_played else 0

        __average_damage_data = page_parser.findAll("div", {"class": "list_pad"})
        __clean_html = self.__clean_html(str(__average_damage_data[3]))
        __parsed_data = __clean_html.split('\n')

        average_damage = __parsed_data[4]
        average_damage = average_damage.strip()[3::]

        overall_spotting_damage = __parsed_data[6].split()[2].replace('разведданным', '')
        overall_spotting_damage = float(overall_spotting_damage) if overall_spotting_damage else 0.0

        __kills_info = page_parser.find('div', {'id': 'profile_main_cont'}).find('div', {'class': 'game_stats2'})
        __average_kills_info = __kills_info.find('div', {'class': 'list_pad'}).find_all('div')
        __clean_average_kills_info = self.__clean_html(str(__average_kills_info[2]))
        average_kills = __clean_average_kills_info.split()[-1][3::]
        average_kills = float(average_kills) if average_kills else 0.0

        winrate = str(page_parser.find("span", {"class": "yellow"}))
        winrate = self.__clean_html(winrate)

        levels_data = page_parser.find('div', {'class': 'game_stats3'})
        if levels_data:
            data = list(levels_data.find('div', {'class': 'diag_pad'}).children)
            data: List[Tag] = [item for item in data if item != '\n']
            levels = self.__extract_battles_per_level(data)
            average_level = self._calculate_average_level(levels) / battles_played if battles_played else None
        else:
            average_level = None

        return PlayerStatistics(**{'winrate': float(winrate[:-1]), 'battles': battles_played,
                                   'damage': float(average_damage), 'clantag': battalion,
                                   'average_spotting': overall_spotting_damage / battles_played if battles_played else 0.0,
                                   'average_kills': average_kills,
                                   'average_level': average_level,
                                   'nickname': nickname})

    def __parse_battalion_page_for_nicknames(self, page: str) -> List:
        soup = BeautifulSoup(page, 'html.parser')
        if page == r'{"redirect":"\/alliance\/top"}':
            logger.warning('Battalion with given ID was not found')
            raise BattalionNotFound("Battalion with given ID was not found")

        notifications = list(soup.find_all('p'))
        if not notifications:
            notifications = soup.find_all('div')
        notifications = list(notifications)

        # Check if we authenticated (if not, then notifications[1] will be equal to __NOT_AUTH_CHECK_BATTALION )
        if self.__NOT_AUTH_CHECK_BATTALION == str(notifications[1]):
            logger.error('Error on parsing page: Client is not authenticated')
            raise NotAuthException('I am not authenticated on aw.mail.ru')

        # Get all divs with cont class( Cont class is class for player information)
        data = soup.find_all('div', {'class': 'cont'})
        # This is the list where we gonna keep track of players
        battalion_players = []

        # YE I KNOW THIS IS HORRIBLE AS FUCK
        for item in str(data[0]).split('\n'):
            if item.startswith('<div><a href="/user/stats'):
                _, player_id, nickname, __ = \
                    item.replace('<div><a href="/user/stats?', '').replace('">', ' ').replace('</a><br/', ' ') \
                        .replace('data=', ' ').split(' ')

                player = {'id': int(player_id), 'nickname': nickname}
                battalion_players.append(player)

        return battalion_players

    def get_battalion_players(self, battalion_id: int) -> List:
        """
        Retrieves battalion players by given battalion ID

        :param battalion_id: ID of battalion
        :return: list of players in this battalion
        """

        page = self.__get_page(f'{self.__battalion_stats_url}&data={battalion_id}')
        battalion_players = self.__parse_battalion_page_for_nicknames(page)
        return battalion_players

    def get_statistic_by_nickname(self, nickname, mode=0, data=0, tank_id=0, day=0) -> PlayerStatistics:
        """
        Retrieves player statistics in mode on specified tank by given nickname or playerID

        :param nickname: Nickname of user to find
        :param mode: Game mode Number from 0 to 4 {pvp, pve, low, glops, ranked}
        :param data: CSA ID of player to find(overwrites user nickname) if not 0
        :param tank_id: staticID of tank to find for(0 means overall stat for mode)
        :param day: Filter stats by some date/battle count

        :return: :dict: Dictionary contains player statistics contains following fields
            winrate: float - Player win rate in percents
            battles: int - Total player battles
            damage: float - Player average damage
            clantag: Optional[str] - player battalion tag (can be None)
            nickname: str - Correct player nickname
        """

        # Get page
        page = self.__get_player_statistic_page(nickname, mode, data, tank_id, day)
        # Parse the page
        parsed_data = self.__get_player_statistics(page, nickname)
        return parsed_data

    def search_battalion(self, battalion_name):
        import json

        r = self.__session.post(f'https://armata.my.games/dynamic/gamecenter/?a=clan_search',
                                data={'name': battalion_name})

        if r.status_code == 200:
            content = json.loads(r.content.decode('utf-8'))
            if content['error'] == 0:
                response_data = content['data']
                return response_data
            raise Exception(f'Bad battalion search code')
        raise BadHTTPStatusCode(f'Received not 200 status code', r.status_code)


AW = API
