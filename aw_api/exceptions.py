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
