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

from .dataobjects import *
from .enums import GameMode
from .parser import Parser
from .exceptions import BadHTTPStatusCode

import logging
import aiohttp
import asyncio
from typing import Optional, Union, Dict, List

logger = logging.getLogger()

__all__ = ['AIOClient']


class AIOClient:
    """
    Asynchronous implementation of client.
    Use this one for your discord bots or async web-apps in order to achieve more compatibility
    with asynchronous frameworks.

    versionadded:: 2.0
    """
    def __init__(self, raw_cookie: Optional[List[Dict]] = None):
        """

        :param raw_cookie :class:`Optional[Dict, List]`
        containing exported with "EditThisCookie" Chrome extension cookie from aw.mail.ru

        """

        # Base URL for player statistics
        self.__user_stats_url = 'https://arwar.ru/dynamic/user/?a=stats'
        # Base URL for battalion page
        self.__battalion_stats_url = 'https://arwar.ru/dynamic/aliance/index.php?a=index'

        # Dict with cookies
        self.__cookie: Union[Dict, List, None] = None

        if raw_cookie:
            self.__cookie = self.__prepare_cookie(raw_cookie)

        # Session that will contain cookies
        self.__session: aiohttp.ClientSession = aiohttp.ClientSession(cookies=self.__cookie)
        self.__parser: Parser = Parser()
        logger.info(f'Initialized AIOClient. Is with cookies: {raw_cookie is not None}')

    async def close(self):
        """
        Closes session if it's not closed yet
        Please, call this when you done using class
        :return: None
        """
        if self.__session.closed:
            return
        await self.__session.close()

    def __del__(self):
        asyncio.ensure_future(self.close())

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
        logger.info('Performing request to {0}'.format(page_url))
        if request.status == 200:
            return await request.text()
        logger.error('Got non 200 status code on request to {0}. Status code: {1}'.format(page_url, request.status))
        raise BadHTTPStatusCode(f'Got non 200 status code: {request.status}', status_code=request.status)

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
        parsed_data = self.__parser.parse_player_statistics(page, nickname)
        return parsed_data

    async def get_battalion_players(self, battalion_id: int) -> List[BattalionMemberEntry]:
        """
        Retrieves battalion players by given battalion ID

        :param battalion_id: ID of battalion
        :return: :class:`List[BattalionMemberEntry]`
        """

        # TODO: Optimize that algorithm, so we would need to iterate over list two times here and in page parser method

        page = await self.__get_page(f'{self.__battalion_stats_url}&data={battalion_id}')
        __temp_battalion_players = self.__parser.parse_battalion_players(page)

        battalion_players: List[BattalionMemberEntry] = []
        for internal_dict_entry in __temp_battalion_players:
            battalion_players.append(
                BattalionMemberEntry(nickname=internal_dict_entry['nickname'],
                                     id=internal_dict_entry['id'],
                                     role=internal_dict_entry['role'],
                                     battalion_id=battalion_id)
            )

        return battalion_players
