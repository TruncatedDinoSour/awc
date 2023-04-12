#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AWC -- ari-web comments"""

import time
import typing
from functools import wraps

import requests
from furl import furl  # type: ignore

from . import const, exc, util

__version__: typing.Final[str] = "1.0.1"


class Awc:
    """ari-web comments interface"""

    __slots__: typing.Tuple[str, ...] = (
        "__instance",
        "api_key",
        "__rate_limit_wait",
        "__session",
    )

    __instance: furl
    api_key: typing.Optional[str]
    __rate_limit_wait: typing.Union[int, float]
    __session: requests.Session

    @property
    def instance(self) -> furl:
        """return API instance url COPY ( parsed )"""
        return self.__instance.copy()

    @property
    def rate_limit_wait(self) -> typing.Union[int, float]:
        """rate limit getter -- get the rate limit wait in seconds"""
        return self.__rate_limit_wait

    @rate_limit_wait.setter
    def rate_limit_wait(self, value: float) -> None:
        """rate limit setter -- set the rate limit wait in seconds"""

        if type(value) not in (int, float) or value < 0:
            raise ValueError(f"rate limit wait time cannot be {value!r}")

        self.__rate_limit_wait = value

    @property
    def session(self) -> requests.Session:
        """requests.Session instance"""
        return self.__session

    def __init__(
        self,
        instance: str,
        api_key: typing.Optional[str] = None,
        rate_limit_wait: typing.Union[int, float] = 5,
    ) -> None:
        ins: furl = furl(instance)

        if (
            not ins.host  # type: ignore
            or ins.scheme not in const.INSTANCE_PROTOCOLS  # type: ignore
            or not util.is_up(ins.host, ins.port)  # type: ignore
        ):
            raise exc.InvalidInstanceURLError(instance)

        self.__instance = ins
        self.api_key = api_key
        self.rate_limit_wait = rate_limit_wait
        self.__session = requests.Session()

        if self.api_key is not None and self.get(api="amiadmin").text != "1":
            raise exc.InvalidAPIKeyError(
                f"{self.api_key[:5]}{'*' * (len(self.api_key) - 5)}"[:50]
                + (" ..." if len(self.api_key) > 50 else "")
            )

    def __getitem__(self, path: str) -> str:
        """return API URL"""
        return self.instance.join(path).url  # type: ignore

    def request(
        self,
        method: typing.Callable[..., requests.Response],
        *args: typing.Any,
        api: str = ".",
        admin: bool = True,
        **kwargs: typing.Any,
    ) -> requests.Response:
        """general requests API, `method` is a member of `self.session` object"""

        if not (
            hasattr(self.session, method.__name__)
            and callable(getattr(self.session, method.__name__))
        ):
            raise ValueError(f"invalid request method : {method}")

        headers: typing.Dict[str, str] = kwargs.setdefault("headers", {})

        if admin and self.api_key is not None:
            headers["api-key"] = self.api_key

        r: typing.Optional[requests.Response] = None

        while True:
            try:
                r = method(self[api], *args, **kwargs)
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError,
            ) as e:
                raise exc.APIRequestFailedError(api, e.response)

            if self.rate_limit_wait and r.status_code == 429:
                time.sleep(self.rate_limit_wait)
            else:
                break

        if not r.ok:
            raise exc.APIRequestFailedError(api, r)

        return r

    def get(self, *args: typing.Any, **kwargs: typing.Any) -> requests.Response:
        """similar to Awc.request() but for GET requests"""
        return self.request(self.session.get, *args, **kwargs)

    def post(self, *args: typing.Any, **kwargs: typing.Any) -> requests.Response:
        """similar to Awc.request() but for POST requests"""
        return self.request(self.session.post, *args, **kwargs)

    @staticmethod
    def require_key(
        f: typing.Callable[..., typing.Any]
    ) -> typing.Callable[..., typing.Any]:
        """decorator to require an api key"""

        @wraps(f)
        def wrap(awc: "Awc", *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            if awc.api_key is None:
                raise exc.NoAPIKeyError(f.__name__)

            return f(awc, *args, **kwargs)

        return wrap
