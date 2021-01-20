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

from .exceptions import UserHasClosedStatisticsException, UserNotFoundException, BadHTTPStatusCode, NotAuthException, \
    BattalionNotFound, BattalionSearchTooShortQuery, BattalionSearchBattalionNotFound

from .structs import PlayerStatistics, BattalionMemberEntry, BattalionSearchResultEntry
from .parser import Parser
from .enums import GameMode

from typing import Union, Dict, List, Optional
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


class API:
    def __init__(self, raw_cookie: Optional[List[Dict]] = None):
        """
        :param raw_cookie :class:`Optional[Dict, List]`
         containing exported with "EditThisCookie" Chrome extension cookie from aw.mail.ru
        """

        self.__parser: Parser = Parser()

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
                _, player_id, nickname, battalion_role = \
                    item.replace('<div><a href="/user/stats?', '').replace('">', ' ').replace('</a><br/', ' ') \
                        .replace('data=', ' ').split(' ')

                # Clean tags in battalion_role
                battalion_role = battalion_role.replace('><span>', '').replace('</span></div>', '')

                # Create a dictionary with player ID and player nickname and add this to List of all players
                player = {'id': int(player_id), 'nickname': nickname, 'role': battalion_role}
                battalion_players.append(player)

        # Eventually, return all battalion players
        return battalion_players

    def get_battalion_players(self, battalion_id: int) -> List[BattalionMemberEntry]:
        """
        Retrieves battalion players by given battalion ID

        :param battalion_id: ID of battalion
        :return: list of players in this battalion
        """

        # TODO: Optimize that algorithm, so we would need to iterate over list two times here and in page parser method

        page = self.__get_page(f'{self.__battalion_stats_url}&data={battalion_id}')
        __temp_battalion_players = self.__parse_battalion_page_for_nicknames(page)

        battalion_players: List[BattalionMemberEntry] = []
        for internal_dict_entry in __temp_battalion_players:
            battalion_players.append(
                BattalionMemberEntry(nickname=internal_dict_entry['nickname'],
                                     id=internal_dict_entry['id'],
                                     role=internal_dict_entry['role'],
                                     battalion_id=battalion_id)
            )

        return battalion_players

    def get_statistic_by_nickname(self, nickname, mode: Union[int, GameMode] = 0, player_id: int = 0, tank_id: int = 0,
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
        page = self.__get_player_statistic_page(nickname, mode, player_id, tank_id, day)
        # Parse the page
        parsed_data = self.__parser.get_player_statistics(page, nickname)
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
