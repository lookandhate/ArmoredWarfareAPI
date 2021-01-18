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

from dataclasses import dataclass
from typing import Optional


@dataclass
class BattalionMemberEntry:
    """

    Dataclass for battalion member data. Each instance has 4 fields:

    nickname :class:`str` - Nickname of battalion member.

    id :class:`int` - Unique ID of player.

    role :class:`Optional[str]` - Role of player in the battalion.

    battalion_id :class:`int` - Unique ID of battalion, player belongs to.

    versionadded:: 1.3

    """

    nickname: str
    id: int
    role: Optional[str]
    battalion_id: int

    def __eq__(self, other):
        """
        Comparing :class:`BattalionMemberEntry` to other objects

        versionadded:: 1.3

        :param other: Object we are comparing self with
        :return: :class:`bool` True if other is instance of :class:`BattalionMemberEntry`
        and objects have identical fields. Otherwise returns False

        """
        return isinstance(other, self.__class__) and \
               self.id == other.id and \
               self.role == other.role and \
               self.battalion_id == other.battalion_id

    def __repr__(self):
        return f'<{self.nickname}(ID: {self.id}) is a member of battalion with ID {self.battalion_id}>'


@dataclass
class BattalionSearchResultEntry:
    """

    Dataclass for battalion search method of API. It contains two fields:

    full_name :class:`str` - full name of the battalion

    id :class:`int` - Unique ID of battalion

    versionadded:: 1.3

    """
    full_name: str
    id: int

    def __repr__(self):
        return f'<Battalion "{self.full_name}" with ID {self.id}>'

    def __eq__(self, other):
        """
        Comparing :class:`BattalionSearchResultEntry` to other objects

        versionadded:: 1.3

        :param other: Object we are comparing self with
        :return: :class:`bool` True if other is instance of :class:`BattalionSearchResultEntry`
        and objects have identical fields. Otherwise returns False

        """
        return isinstance(other, self.__class__) and self.id == other.id and self.full_name == other.full_name
