class BaseStatsServiceException(Exception):
    """base exception for statistics parser"""


class UserNotFoundException(BaseStatsServiceException):
    """Raises whenever user with given nickname was not found"""

    def __init__(self, nickname, *args, **kwargs):
        self.nickname = nickname
        super().__init__(*args, **kwargs)


class BattalionNotFound(BaseStatsServiceException):
    """Raises whenever battalion with given id was not found"""
    pass


class UserHasClosedStatisticsException(BaseStatsServiceException):
    """Raises when requested user has closed stats"""
    pass


class NotAuthException(BaseStatsServiceException):
    """Raises if bot did not pass auth"""
    pass


class BadHTTPStatusCode(BaseStatsServiceException):
    def __init__(self, status_code, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = status_code
