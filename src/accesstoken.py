import datetime

import logging
_LOGGER = logging.getLogger(__name__)

class AccessToken():

    def __init__(self, accessToken, refreshToken, validity) -> None:
        self.accessToken = accessToken
        self.refreshToken = refreshToken
        self.validity = validity

    def is_valid(self):
        return datetime.now() < self.validity

    def getToken(self):
        return self.token
    

