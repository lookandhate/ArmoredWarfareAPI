"""
MIT License

Copyright (c) 2020-2021 Dmitriy Trofimov

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

from typing import Union, Dict, List, Optional
from enum import Enum
from bs4 import BeautifulSoup, Tag

from .exceptions import UserHasClosedStatisticsException, UserNotFoundException, BadHTTPStatusCode, NotAuthException, \
    BattalionNotFound, BattalionSearchTooShortQuery, BattalionSearchBattalionNotFound

from .player import PlayerStatistics

from .battalion import BattalionMemberEntry, BattalionSearchResultEntry


logger = logging.getLogger(__name__)


class GameMode(Enum):
    PVP = 0
    PVE = 1
    LOW = 2
    GLOPS = 3
    RANKED = 4
    RB = RANKED


class API:
    def __init__(self, raw_cookie: Optional[List[Dict]] = None):
        """
        :param raw_cookie :class:`Optional[Dict, List]`
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
    def __calculate_level_sum(level_stats: List[int]) -> int:
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

    def __get_player_statistic_page(self, nickname: str, mode: int, data: int, tank_id: int, day: int = 0,
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

        :return: `PlayerStatistics` instance
        """

        # Let's parse the page
        page_parser = BeautifulSoup(page, "html.parser")

        # Get page "notifications" and look for error messages
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

        # There is no errors, so go ahead and parse page for information
        nickname = self.__clean_html(str(page_parser.find("div", {"class": "name"}))).split('\n')[1]
        __battalion_info_dirty = page_parser.find('div', {'class': 'clan'})
        __battalion_tag_and_fullname_dirty = str(__battalion_info_dirty.contents[3]).split()
        battalion_tag = __battalion_tag_and_fullname_dirty[0].replace('<span>', '').replace('[', '').replace(']', '')
        battalion_full_name = __battalion_tag_and_fullname_dirty[1].replace('</span>', '').replace('[', '').replace(']',
                                                                                                                    '')

        if len(battalion_tag) == 0:
            battalion_tag = None
            battalion_full_name = None

        __battles_played_dirty = str(page_parser.find("div", {"class": "total"}))
        __battles_played_dirty = self.__clean_html(__battles_played_dirty).split()[-1].replace('сыграно', '')
        battles_played: int = int(__battles_played_dirty) if __battles_played_dirty else 0

        __average_damage_data = page_parser.findAll("div", {"class": "list_pad"})
        __clean_html = self.__clean_html(str(__average_damage_data[3]))
        __parsed_data = __clean_html.split('\n')

        average_damage = __parsed_data[4]
        average_damage = average_damage.strip()[3::]

        overall_spotting_damage = __parsed_data[6].split()[2].replace('разведданным', '')
        overall_spotting_damage = float(overall_spotting_damage) if overall_spotting_damage else 0.0

        __kills_info_dirty = page_parser.find('div', {'id': 'profile_main_cont'}).find('div', {'class': 'game_stats2'})
        __average_kills_info_dirty = __kills_info_dirty.find('div', {'class': 'list_pad'}).find_all('div')
        __clean_average_kills_info = self.__clean_html(str(__average_kills_info_dirty[2]))
        average_kills = __clean_average_kills_info.split()[-1][3::]
        average_kills = float(average_kills) if average_kills else 0.0

        winrate = str(page_parser.find("span", {"class": "yellow"}))
        winrate = self.__clean_html(winrate)

        levels_data = page_parser.find('div', {'class': 'game_stats3'})
        if levels_data:
            __level_data_dirty = list(levels_data.find('div', {'class': 'diag_pad'}).children)
            __levels_data_dirty_tags: List[Tag] = [item for item in __level_data_dirty if item != '\n']
            levels = self.__extract_battles_per_level(__levels_data_dirty_tags)
            average_level = self.__calculate_level_sum(levels) / battles_played if battles_played else None
        else:
            average_level = None

        return PlayerStatistics(**{'winrate': float(winrate[:-1]), 'battles': battles_played,
                                   'damage': float(average_damage), 'clantag': battalion_tag,
                                   'battalion_full': battalion_full_name,
                                   'average_spotting': overall_spotting_damage / battles_played if battles_played else 0.0,
                                   'average_kills': average_kills,
                                   'average_level': average_level,
                                   'nickname': nickname})

    def __parse_battalion_page_for_nicknames(self, page: str) -> List[Dict]:
        # TODO Complete doc-string
        """
        This is fucking hell, get outta here if you dont want to burn your eyes
        I warned you
        :param page:
        :return:
        """
        soup = BeautifulSoup(page, 'html.parser')

        # So, if battalion with given id does not exist
        # then instead of HTML page we will receive JSON, telling browser to redirect on battalion rating page
        if page == r'{"redirect":"\/alliance\/top"}':
            logger.warning('Battalion with given ID was not found')
            raise BattalionNotFound("Battalion with given ID was not found")

        # Get page "notifications" and look for error messages
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
        # SO, in here we are iterating over sub-tags in <div class='cont'>
        for item in str(data[0]).split('\n'):
            # Item will be something like this:
            # <div><a href="/user/stats?data=458829630">T57Heavy-Tank</a><br/><span>Рядовой</span></div>
            # if item is a player line
            if item.startswith('<div><a href="/user/stats'):
                # Here we are getting rid of all HTML stuff like tags, hrefs, etc by replacing them with space-symbols
                # We will get something like this:
                # 485633946 RUBIN ><span>Командир</span></div>

                # Imagine making  a list from that
                # Then we will have something like this: ['', '485633946', 'RUBIN', '><span>Командир</span></div>']
                # Only thing we need from that is ID and nickname, so lets extract them below
                _, player_id, nickname, __ = \
                    item.replace('<div><a href="/user/stats?', '').replace('">', ' ').replace('</a><br/', ' ') \
                        .replace('data=', ' ').split(' ')

                # Create a dictionary with player ID and player nickname and add this to List of all players
                player = {'id': int(player_id), 'nickname': nickname}
                battalion_players.append(player)

        # Eventually, return all battalion players
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

    def get_statistic_by_nickname(self, nickname, mode: Union[int, GameMode] = 0, data: int = 0, tank_id: int = 0,
                                  day: int = 0) -> PlayerStatistics:
        """
        Retrieves player statistics in mode on specified tank by given nickname or playerID

        :raises :exc:`UserHasClosedStatisticsException`, :exc:`NotAuthException`,:exc:`UserNotFoundException`

        :param nickname: Nickname of user to find
        :param mode: Game mode Number from 0 to 4 {pvp, pve, low, glops, ranked}
        :param data: CSA ID of player to find(overwrites user nickname if not 0)
        :param tank_id: staticID of tank to find for(0 means overall stat for mode)
        :param day: Filter stats by some date/battle count

        :return: :class:`PlayerStatistics`
        """

        # If GameMode instance was passed as a mode, than assign number from GameMode.value to mode variable
        if isinstance(mode, GameMode):
            mode = mode.value

        # Get page
        page = self.__get_player_statistic_page(nickname, mode, data, tank_id, day)
        # Parse the page
        parsed_data = self.__get_player_statistics(page, nickname)
        return parsed_data

    def search_battalion(self, battalion_name: str) -> List[BattalionSearchResultEntry]:
        """
        Searches for battalion by given name

        :raises :exc:`BattalionSearchTooShortQuery` if you gave less than 4 symbols for search

        :raises :exc:`BattalionSearchBattalionNotFound` if battalion with given name was not found

        versionadded:: 1.1

        :param battalion_name:
        :return: :class:`List[BattalionSearchResultEntry]`
        List of BattalionSearchResultEntry dataclass instances

        """
        import json

        r = self.__session.post(f'https://armata.my.games/dynamic/gamecenter/?a=clan_search',
                                data={'name': battalion_name})

        if r.status_code == 200:
            __dirty_content = json.loads(r.content.decode('utf-8'))
            if __dirty_content['error'] == 0:
                __battalions_search_result_data = __dirty_content['data']

                search_result = []
                for key in __battalions_search_result_data.keys():
                    search_result.append(BattalionSearchResultEntry(__battalions_search_result_data[key], int(key)))
                return search_result

            if __dirty_content['error'] == 1:
                raise BattalionSearchTooShortQuery(
                    f'Given battalion name is too short for process.'
                    f' 4 symbols required, {len(battalion_name)} were given',
                    len(battalion_name))
            if __dirty_content['error'] == 2:
                raise BattalionSearchBattalionNotFound(f'Battalion with name "{battalion_name}"'
                                                       f' was not found.', battalion_name)

        raise BadHTTPStatusCode(f'Received not 200 status code', r.status_code)


AW = API
