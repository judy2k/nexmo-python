"""
nexmo - Client library for the nexmo service.
"""

import os
from . import lo, sms


__version__ = '1.4.0'


class Client(object):
    def __init__(
        self,
        key=None,
        secret=None,
    ):
        self.api_key = key or os.environ['NEXMO_API_KEY']
        self.api_secret = secret or os.environ['NEXMO_API_SECRET']

        self._client = lo.Client(
            key=self.api_key,
            secret=self.api_secret,
        )

        self.sms = sms.SMSClient(self)

    def post(self, path, params):
        return self._client.post(self._client.host, path, params)
