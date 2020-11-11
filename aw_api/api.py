import re
from typing import Union

import requests
from bs4 import BeautifulSoup

from .exceptions import UserHasClosedStatisticsException, UserNotFoundException, BadHTTPStatusCode, NotAuthException, \
    BattalionNotFound


class API:
    def __init__(self, raw_cookie: Union[dict, list] = None):
        """
        :param raw_cookie: dict containing exported with "EditThisCookie" Chrome extension cookie from aw.mail.ru
        """

        # Paragraph that shows if we are not authenticated on site
        self.__NOT_AUTH_CHECK = '<p>Для просмотра данной страницы вам необходимо авторизоваться или <a href="/user/register/">зарегистрироваться</a> на сайте.</p>'
        self.__NOT_AUTH_CHECK_BATTALION = '<div class="node_notice warn border">Необходимо авторизоваться.</div>'
        # Div with text shows that user closed his statistics
        self.__CLOSED_STAT = '<div class="node_notice warn border">Пользователь закрыл доступ!</div>'
        # Div with text shows that player with given nickname does not exist
        self.__PLAYER_NOT_EXISTS = '<div class="node_notice warn border">Пользователь не найден!</div>'
        # base url for player statistics
        self.__user_stats_url = 'https://armata.my.games/dynamic/user/?a=stats'
        # Session that will contain cookies
        self.__battalion_stats_url = 'https://armata.my.games/dynamic/aliance/index.php?a=index'
        self.__session: requests.Session = requests.Session()
        # Dict with cookies
        self.__cookie: Union[dict, list, None] = None
        if raw_cookie:
            self.__cookie = self.__prepare_cookie(raw_cookie)

    # Clean HTML from tags to extract only data
    @staticmethod
    def __clean_html(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    @staticmethod
    def __prepare_cookie(raw_cookie: Union[dict, list]) -> dict:
        """
        :param raw_cookie: Raw cookie from EditThisCookie
        :return: Dict with "cleaned" cookies
        """

        new_cookie_dict = dict()
        for item in raw_cookie:
            new_cookie_dict[item['name']] = item['value']
        return new_cookie_dict

    def __get_page(self, url):
        """
        :param url: URL to retrieve
        :return: string with decoded HTML page
        """

        request = self.__session.get(url, cookies=self.__cookie)
        if request.status_code == 200:
            page = request.content.decode('utf-8')
            return page
        raise BadHTTPStatusCode(f'Got non 200 status code: {request.status_code}', request.status_code)

    def __get_player_statistic_page(self, nickname: str, mode: int, data: int, tank_id: id, day: int = 0,
                                    ajax: int = 0) -> str:
        """
        :param nickname: Nickname of user to find
        :param mode: Game mode Number from 0 to 4 {pvp, pve, low, glops, ranked}
        :param data: CSA ID of player to find(overwrites user nickname) if not 0
        :param tank_id: staticID of tank to find for(0 means overall stat for mode)
        :param day: Filter stats by some date/battle count
        :param ajax: Is data should be returned like in ajax request (DONT CHANGE IT OR WILL BROKE)
        :return: string with decoded HTML page

        """

        url = f'{self.__user_stats_url}&name={nickname}&mode={mode}&data={data}&type={tank_id}&day={day}&ajax={ajax}'
        return self.__get_page(url)

    def __get_player_statistics(self, page: str, nickname=None) -> dict:
        """
        :param page: string with HTML document
        :param nickname: Nickname of player to rise exception with

        :return: dict with user data, where
        winrate: float - Player win rate in percents
        battles: int - Total player battles
        damage: float - Player average damage
        clantag: Optional[str] - player battalion tag (can be None)
        nickname: str - Correct player nickname
        """

        # Парсинг страницы
        soup = BeautifulSoup(page, "html.parser")
        notifications = list(soup.find_all('p'))
        if not notifications:
            notifications = soup.find_all('div')
        notifications = list(notifications)

        # Check if we authenticated (if not, then notifications[0] will be equal to NOT_AUTH_CHECK )
        if self.__NOT_AUTH_CHECK == str(notifications[0]):
            raise NotAuthException('I am not authenticated on aw.mail.ru')

        # Check if user exists( if user does not exist, then notifications[0] will be equal to PLAYER_NOT_EXISTS )
        if self.__PLAYER_NOT_EXISTS == str(notifications[0]):
            raise UserNotFoundException('User with given nickname was not found')

        # Check did user closed stats
        if '<div class="node_notice warn border">Пользователь закрыл доступ!</div>' == str(notifications[0]):
            raise UserHasClosedStatisticsException('User with given nickname closed his stats')

        nickname = self.__clean_html(str(soup.find("div", {"class": "name"}))).split('\n')[1]
        battalion = soup.find('div', {'class': 'clan'})
        battalion = str(battalion.contents[3]).split()
        battalion = battalion[0].replace('<span>', '').replace('[', '').replace(']', '')
        if len(battalion) == 0:
            battalion = None

        battle_stats = str(soup.find("div", {"class": "total"}))
        battle_stats = self.__clean_html(battle_stats).split()[-1].replace('сыграно', '')
        battle_stats = int(battle_stats) if battle_stats else 0

        avg_dmg = soup.findAll("div", {"class": "list_pad"})
        clear = self.__clean_html(str(avg_dmg[3]))
        avg_dmg = clear.split('\n')
        avg_dmg = avg_dmg[4]
        avg_dmg = avg_dmg.strip()[3::]

        winrate_stat = str(soup.find("span", {"class": "yellow"}))
        winrate_stat = self.__clean_html(winrate_stat)

        return {'winrate': float(winrate_stat[:-1]), 'battles': battle_stats,
                'damage': float(avg_dmg), 'clantag': battalion, 'nickname': nickname}

    def __parse_battalion_page_for_nicknames(self, page: str) -> list:
        soup = BeautifulSoup(page, 'html.parser')
        if page == '{"redirect":"\/alliance\/top"}':
            raise BattalionNotFound("Battalion with given ID was not found")
        notifications = list(soup.find_all('p'))
        if not notifications:
            notifications = soup.find_all('div')
        notifications = list(notifications)

        # Check if we authenticated (if not, then notifications[1] will be equal to __NOT_AUTH_CHECK_BATTALION )
        if self.__NOT_AUTH_CHECK_BATTALION == str(notifications[1]):
            raise NotAuthException('I am not authenticated on aw.mail.ru')
        # Get all divs with cont class( Cont class is class for player information)
        data = soup.find_all('div', {'class': 'cont'})
        # This is the list where we gonna keep track of players
        battalion_players = []

        # YE I KNOW THIS IS HORRIBLE AS FUCK
        #
        for item in str(data[0]).split('\n'):
            if item.startswith('<div><a href="/user/stats'):
                _, player_id, nickname, __ = item.replace('<div><a href="/user/stats?', '').replace('">', ' ').replace(
                    '</a><br/', ' ') \
                    .replace('data=', ' ').split(' ')
                player = {'id': int(player_id), 'nickname': nickname}
                battalion_players.append(player)

        return battalion_players

    def get_battalion_players(self, battalion_id: int) -> list:
        page = self.__get_page(f'{self.__battalion_stats_url}&data={battalion_id}')
        battalion_players = self.__parse_battalion_page_for_nicknames(page)
        return battalion_players

    def get_statistic_by_nickname(self, nickname, mode=0, data=0, tank_id=0, day=0):
        """

        :param nickname: Nickname of user to find
        :param mode: Game mode Number from 0 to 4 {pvp, pve, low, glops, ranked}
        :param data: CSA ID of player to find(overwrites user nickname) if not 0
        :param tank_id: staticID of tank to find for(0 means overall stat for mode)
        :param day: Filter stats by some date/battle count
        :return: dict with Player statistics
        """

        # Get page
        page = self.__get_player_statistic_page(nickname, mode, data, tank_id, day)
        # Parse the page
        parsed_data = self.__get_player_statistics(page, nickname)
        return parsed_data