#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""awc -- ari-web comments"""

import time
import typing
from functools import wraps

import requests
from furl import furl  # type: ignore

from . import const, exc, util

__version__: typing.Final[str] = "2.0.0"


class Awc:
    """ari-web comments interface

    this is where all API requests begin, you must
    pass an instance of this object to every api wrapper
    as a first argument"""

    __slots__: typing.Tuple[str, ...] = (
        "__instance",
        "__api_key",
        "__rate_limit_wait",
        "__session",
    )

    __instance: furl
    __api_key: typing.Optional[str]
    __rate_limit_wait: typing.Union[int, float]
    __session: requests.Session

    @property
    def instance(self) -> furl:
        """return API instance url COPY ( parsed )

        return furl.furl -- the parsed url copy"""
        return self.__instance.copy()

    @property
    def api_key(self) -> typing.Optional[str]:
        """api_key getter -- returns the optionally set API key

        return str | None -- optionally set API key"""
        return self.__api_key

    @api_key.setter
    def api_key(self, value: typing.Optional[str]) -> None:
        """api_key setter -- sets the optionally set API key

        raise
            awc.exc.InvalidAPIKeyError -- on invalid API key"""

        api_key: typing.Optional[str]

        try:
            api_key = self.__api_key
        except AttributeError:
            api_key = None

        self.__api_key = value

        if value is not None and self.get(api="amiadmin").text != "1":
            self.__api_key = api_key

            raise exc.InvalidAPIKeyError(
                f"{value[:5]}{'*' * (len(value) - 5)}"[:50]
                + (" ..." if len(value) > 50 else "")
            )

    @property
    def rate_limit_wait(self) -> typing.Union[int, float]:
        """rate limit wait time getter -- get the rate limit wait in seconds

        return int | float -- sleep time in seconds"""
        return self.__rate_limit_wait

    @rate_limit_wait.setter
    def rate_limit_wait(self, value: float) -> None:
        """rate limit wait time setter -- set the rate limit wait in seconds

        raise
            ValueError -- on incorrect supplied value ( typewise or valuewise )"""

        if type(value) not in (int, float) or value < 0:
            raise ValueError(f"rate limit wait time cannot be {value!r}")

        self.__rate_limit_wait = value

    @property
    def session(self) -> requests.Session:
        """requests.Session instance

        return requests.Session -- the requests session"""
        return self.__session

    def __init__(
        self,
        instance: str,
        api_key: typing.Optional[str] = None,
        rate_limit_wait: typing.Union[int, float] = 5,
    ) -> None:
        """initialise the awc instance

        instance: str -- the instance URL
        api_key: str | None = None -- the API key used for requests ( optional )
        rate_limit_wait: int | float -- the sleep time in seconds for how much to
                                        sleep when we get rate limited

        raise
            awc.exc.InvalidInstanceURLError -- on invalid instance
            awc.exc.InvalidAPIKeyError(api_key.setter) -- on invalid API key"""

        ins: furl = furl(instance)

        if (
            not ins.host  # type: ignore
            or ins.scheme not in const.INSTANCE_PROTOCOLS  # type: ignore
            or not util.is_up(ins.host, ins.port)  # type: ignore
        ):
            raise exc.InvalidInstanceURLError(instance)

        self.__instance = ins
        self.__session = requests.Session()

        self.rate_limit_wait = rate_limit_wait
        self.api_key = api_key

    def __getitem__(self, path: str) -> str:
        """return an API URL of requested `path`

        return str -- the URL"""
        return self.instance.join(path).url  # type: ignore

    def __enter__(self) -> "Awc":
        return self

    def __exit__(self, *_: typing.Any) -> None:
        self.end()

    def request(
        self,
        method: typing.Callable[..., requests.Response],
        *args: typing.Any,
        api: str = ".",
        admin: bool = True,
        **kwargs: typing.Any,
    ) -> requests.Response:
        """general requests API

        method: typing.Callable[..., requests.Response] -- member of Awc.session, used
                                                           to call to the API endpoints
        *args: typing.Any -- arguments passed to `method`
        api: str = "." -- the API endpoint to call to
        admin: bool = True -- should we add the `api-key` header to this request
        **kwargs: typing.Any -- keyword arguments passed to `method`

        return requests.Response -- the API response"""

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
                raise exc.APIRequestFailedError(api, e.response) from e

            if self.rate_limit_wait and r.status_code == 429:
                time.sleep(self.rate_limit_wait)
            else:
                break

        if not r.ok:
            raise exc.APIRequestFailedError(api, r)

        return r

    def get(self, *args: typing.Any, **kwargs: typing.Any) -> requests.Response:
        """similar to `Awc.request` but for GET requests,

        return requests.Response"""
        return self.request(self.session.get, *args, **kwargs)

    def post(self, *args: typing.Any, **kwargs: typing.Any) -> requests.Response:
        """similar to `Awc.request` but for POST requests"""
        return self.request(self.session.post, *args, **kwargs)

    def end(self) -> None:
        """end an instance ( close it )"""

        self.__api_key = None
        self.session.close()

    @staticmethod
    def require_key(
        f: typing.Callable[..., typing.Any]
    ) -> typing.Callable[..., typing.Any]:
        """decorator to require an api key to run a function"""

        @wraps(f)
        def wrap(awc: "Awc", *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            if awc.api_key is None:
                raise exc.NoAPIKeyError(f.__name__)

            return f(awc, *args, **kwargs)

        return wrap
