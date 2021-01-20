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

from .dataobjects.player import PlayerStatistics
from .exceptions import NotAuthException, UserNotFoundException, UserHasClosedStatisticsException, BattalionNotFound

import re
import logging
from bs4 import BeautifulSoup, Tag
from typing import List

__all__ = ['Parser']

logger = logging.getLogger()


class Helper:
    @staticmethod
    def clean_html(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    @classmethod
    def extract_battles_per_level(cls, level_stats: List[Tag]) -> List[int]:
        battles = []
        for item in level_stats:
            children = list(item.children)
            battles.append(int(cls.clean_html(str(children[-2]))))
        return battles

    @staticmethod
    def calculate_level_sum(level_stats: List[int]) -> int:
        total_sum = 0
        for index, item in enumerate(level_stats, 1):
            total_sum += index * item
        return total_sum


class Parser:
    # Paragraph that shows if we are not authenticated on site
    __NOT_AUTH_CHECK = [
        '<p>Для просмотра данной страницы вам необходимо авторизоваться или <a href="/user/register/">зарегистрироваться</a> на сайте.</p>',
        '<p>Для просмотра данной страницы вам необходимо авторизоваться или <a href="" onclick="__GEM.showSignup();return false;" target="_blank">зарегистрироваться</a> на сайте.</p>'
    ]
    __NOT_AUTH_CHECK_BATTALION = '<div class="node_notice warn border">Необходимо авторизоваться.</div>'
    # Div with text shows that user closed his statistics
    __CLOSED_STAT = '<div class="node_notice warn border">Пользователь закрыл доступ!</div>'
    # Div with text shows that player with given nickname does not exist
    __PLAYER_NOT_EXISTS = '<div class="node_notice warn border">Пользователь не найден!</div>'
    __HELPER = Helper()

    def parse_player_statistics(self, page: str, nickname=None) -> PlayerStatistics:
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
        nickname = self.__HELPER.clean_html(str(page_parser.find("div", {"class": "name"}))).split('\n')[1]
        __battalion_info_dirty = page_parser.find('div', {'class': 'clan'})
        __battalion_tag_and_fullname_dirty = str(__battalion_info_dirty.contents[3]).split()
        battalion_tag = __battalion_tag_and_fullname_dirty[0].replace('<span>', '').replace('[', '').replace(']', '')
        battalion_full_name = __battalion_tag_and_fullname_dirty[1].replace('</span>', '').replace('[', '').replace(']',
                                                                                                                    '')

        if len(battalion_tag) == 0:
            battalion_tag = None
            battalion_full_name = None

        __battles_played_dirty = str(page_parser.find("div", {"class": "total"}))
        __battles_played_dirty = self.__HELPER.clean_html(__battles_played_dirty).split()[-1].replace('сыграно', '')
        battles_played: int = int(__battles_played_dirty) if __battles_played_dirty else 0

        __average_damage_data = page_parser.findAll("div", {"class": "list_pad"})
        __clean_html = self.__HELPER.clean_html(str(__average_damage_data[3]))
        __parsed_data = __clean_html.split('\n')

        average_damage = __parsed_data[4]
        average_damage = average_damage.strip()[3::]

        overall_spotting_damage = __parsed_data[6].split()[2].replace('разведданным', '')
        overall_spotting_damage = float(overall_spotting_damage) if overall_spotting_damage else 0.0

        __kills_info_dirty = page_parser.find('div', {'id': 'profile_main_cont'}).find('div', {'class': 'game_stats2'})
        __average_kills_info_dirty = __kills_info_dirty.find('div', {'class': 'list_pad'}).find_all('div')
        __clean_average_kills_info = self.__HELPER.clean_html(str(__average_kills_info_dirty[2]))
        average_kills = __clean_average_kills_info.split()[-1][3::]
        average_kills = float(average_kills) if average_kills else 0.0

        winrate = str(page_parser.find("span", {"class": "yellow"}))
        winrate = self.__HELPER.clean_html(winrate)

        levels_data = page_parser.find('div', {'class': 'game_stats3'})
        if levels_data:
            __level_data_dirty = list(levels_data.find('div', {'class': 'diag_pad'}).children)
            __levels_data_dirty_tags: List[Tag] = [item for item in __level_data_dirty if item != '\n']
            levels = self.__HELPER.extract_battles_per_level(__levels_data_dirty_tags)
            average_level = self.__HELPER.calculate_level_sum(levels) / battles_played if battles_played else None
        else:
            average_level = None

        return PlayerStatistics(**{'winrate': float(winrate[:-1]), 'battles': battles_played,
                                   'damage': float(average_damage), 'clantag': battalion_tag,
                                   'battalion_full': battalion_full_name,
                                   'average_spotting': overall_spotting_damage / battles_played if battles_played else 0.0,
                                   'average_kills': average_kills,
                                   'average_level': average_level,
                                   'nickname': nickname})

    def parse_battalion_players(self, page: str):
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
