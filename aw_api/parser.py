from .structs.player import PlayerStatistics
from .exceptions import NotAuthException
from .exceptions import UserHasClosedStatisticsException
from .exceptions import UserNotFoundException

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

    def get_player_statistics(self, page: str, nickname=None) -> PlayerStatistics:
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
