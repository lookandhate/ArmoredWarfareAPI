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

    def __init__(self, message, nickname=None):
        super().__init__(message)
        self.nickname = nickname


class BattalionNotFound(BaseAWStatsException):
    """Raises whenever battalion with given id was not found"""


class UserHasClosedStatisticsException(BaseAWStatsException):
    """Raises when requested user has closed stats"""

    def __init__(self, message, nickname=None):
        super().__init__(message)
        self.nickname = nickname


class NotAuthException(BaseAWStatsException):
    """Raises if credentials did not pass auth"""


class BadHTTPStatusCode(BaseAWStatsException):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code
