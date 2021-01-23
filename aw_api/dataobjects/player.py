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
class PlayerStatistics:
    winrate: float
    battles: int
    damage: float
    clantag: Optional[str]
    battalion_full: Optional[str]
    average_spotting: float
    average_kills: float
    average_level: Optional[float]
    nickname: str

    def __getitem__(self, item):
        return getattr(self, item)

    def __eq__(self, other):

        if not isinstance(other, PlayerStatistics):
            return False

        if self.clantag is None:
            clantag = self.clantag is other.clantag
        else:
            clantag = self.clantag == other.clantag

        if self.battalion_full is None:
            battalion_full = self.battalion_full is other.battalion_full
        else:
            battalion_full = self.battalion_full == other.battalion_full

        if self.average_level is None:
            average_level = self.average_level is other.average_level
        else:
            average_level = self.average_level == other.average_level

        return isinstance(other,
                          PlayerStatistics) \
               and other.winrate == self.winrate \
               and other.battles == self.battles \
               and other.damage == self.damage \
               and clantag \
               and battalion_full \
               and other.average_spotting == self.average_spotting \
               and other.average_kills == self.average_kills \
               and average_level \
               and other.nickname == self.nickname


Player = PlayerStatistics
