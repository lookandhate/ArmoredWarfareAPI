from .exceptions import *
from .player import *
from .api import GameMode

import logging
import aiohttp
import asyncio
import re

from typing import Optional, Union, Dict, List
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger()


class AIOClient:
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

        # Dict with cookies
        self.__cookie: Union[Dict, List, None] = None

        if raw_cookie:
            self.__cookie = self.__prepare_cookie(raw_cookie)

        # Session that will contain cookies
        self.__session: aiohttp.ClientSession = aiohttp.ClientSession(cookies=self.__cookie)

    def __del__(self):
        event_loop = asyncio.get_event_loop()

        event_loop.run_until_complete(self.__session.close())

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

    async def __get_page(self, page_url: str):
        request = await self.__session.get(url=page_url)
        if request.status == 200:
            return await request.text()
        else:
            return None

    async def __get_player_statistic_page(self, nickname: str, mode: int, data: int, tank_id: int, day: int = 0,
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
        page = await self.__get_page(url)
        return page

    async def __get_player_statistics(self, page: str, nickname=None) -> PlayerStatistics:
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

    async def get_statistic_by_nickname(self, nickname, mode: Union[int, GameMode] = 0, player_id: int = 0,
                                        tank_id: int = 0,
                                        day: int = 0) -> PlayerStatistics:
        """
        Retrieves player statistics in mode on specified tank by given nickname or playerID

        :raises :exc:`UserHasClosedStatisticsException`, :exc:`NotAuthException`,:exc:`UserNotFoundException`

        :param nickname: Nickname of user to find
        :param mode: Game mode Number from 0 to 4 {pvp, pve, low, glops, ranked}
        :param player_id: CSA ID of player to find(overwrites user nickname if not 0)
        :param tank_id: staticID of tank to find for(0 means overall stat for mode)
        :param day: Filter stats by some date/battle count

        :return: :class:`PlayerStatistics`
        """

        # If GameMode instance was passed as a mode, than assign number from GameMode.value to mode variable
        if isinstance(mode, GameMode):
            mode = mode.value

        # Get page
        page = await self.__get_player_statistic_page(nickname, mode, player_id, tank_id, day)
        # Parse the page
        parsed_data = await self.__get_player_statistics(page, nickname)
        return parsed_data

