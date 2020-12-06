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


class BaseAWStatsException(Exception):
    """Base exception for statistics parser"""


class UserNotFoundException(BaseAWStatsException):
    """Raises whenever user with given nickname was not found"""

    def __init__(self, nickname, *args, **kwargs):
        self.nickname = nickname
        super().__init__(*args, **kwargs)


class BattalionNotFound(BaseAWStatsException):
    """Raises whenever battalion with given id was not found"""
    pass


class UserHasClosedStatisticsException(BaseAWStatsException):
    """Raises when requested user has closed stats"""
    pass


class NotAuthException(BaseAWStatsException):
    """Raises if bot did not pass auth"""
    pass


class BadHTTPStatusCode(BaseAWStatsException):
    def __init__(self, status_code, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = status_code
