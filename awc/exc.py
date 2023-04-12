#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""awc exceptions"""

import typing

import requests


class AWCException(Exception):
    """base awc exception"""


class InvalidInstanceURLError(AWCException, requests.exceptions.InvalidURL):
    """raised when an API instance URL isnt valid"""

    instance: str

    def __init__(self, instance: str) -> None:
        super().__init__(instance)  # type: ignore
        self.instance: str = instance


class APIRequestFailedError(AWCException, requests.exceptions.HTTPError):
    """raised when a request to an API fails"""

    api: str

    def __init__(self, api: str, response: requests.Response) -> None:
        super().__init__(api)  # type: ignore
        self.api: str = api
        self.response: requests.Response = response


class NoAPIKeyError(AWCException, PermissionError):
    """raised when no API key is provided"""


class InvalidAPIKeyError(AWCException, PermissionError):
    """raised when the API key is invalid"""


class UnexpectedResponseError(AWCException, ValueError):
    """raised when the API returns an unexpected response"""

    def __init__(self, value: str, expected: type) -> None:
        super().__init__(
            f"got {value!r}, but we expected something of type {expected!r}"
        )
        self.value: str = value
        self.expected: type = expected


class ResouceNotFoundError(AWCException, ValueError):
    """raised when the API doesnt return the requested resource"""

    def __init__(self, value: typing.Any) -> None:
        super().__init__(value)
        self.value: typing.Any = value
