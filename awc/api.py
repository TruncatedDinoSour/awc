#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ari-web api wrappers"""

import typing

import requests

from . import Awc, const, exc, util


def post_comment(awc: Awc, content: str) -> typing.List[typing.Union[int, bool]]:
    """post a comment"""

    try:
        return awc.post(
            data={"content": util.truncate(content, const.MAX_CONTENT_LEN)}
        ).json()
    except requests.exceptions.InvalidJSONError as e:
        raise exc.UnexpectedResponseError(
            e.response.text, typing.List[typing.Union[int, bool]]
        )


def get_comments(
    awc: Awc, from_id: int, to_id: int
) -> typing.Dict[str, typing.List[typing.Union[str, bool, None]]]:
    """get comments in range from-to"""

    if from_id > to_id:
        raise ValueError(
            f"from_id ( {from_id} ) most not be larger than to_id ( {to_id} )"
        )

    if (diff := abs(to_id - from_id)) > const.MAX_FETCH_COUNT:
        raise ValueError(
            f"difference between to_id ( {to_id} ) and from_id ( {from_id} ) cannot be \
larger than {const.MAX_FETCH_COUNT} ( while currently its {diff} )"
        )

    try:
        return awc.get(api=f"{from_id}/{to_id}").json()
    except requests.exceptions.InvalidJSONError as e:
        raise exc.UnexpectedResponseError(
            e.response.text,
            typing.Dict[int, typing.List[typing.Union[str, bool, None]]],
        )


def get_comment(awc: Awc, cid: int) -> typing.List[typing.Union[str, bool, None]]:
    """get coment by ID"""

    try:
        return get_comments(awc, cid, cid)[str(cid)]
    except KeyError as e:
        raise exc.ResouceNotFoundError(cid) from e


def total(awc: Awc) -> int:
    """total comments count api"""

    r: requests.Response = awc.get(api="total")

    try:
        return int(r.text)
    except ValueError as e:
        raise exc.UnexpectedResponseError(r.text, int) from e


@Awc.require_key
def sql(
    awc: Awc, queries: typing.Iterable[str], backup: typing.Optional[str] = None
) -> typing.List[typing.List[typing.Any]]:
    """run SQL queries"""

    data: typing.Dict[str, typing.Union[typing.Iterable[str], str]] = {"sql": queries}

    if backup is not None:
        data["backup"] = backup

    try:
        return awc.post(api="sql", data=data).json()  # type: ignore
    except requests.exceptions.InvalidJSONError as e:
        raise exc.UnexpectedResponseError(
            e.response.text, typing.Dict[int, typing.List[typing.List[typing.Any]]]
        )


def apply(awc: Awc, author: str, content: str) -> requests.Response:
    """apply to the whitelist"""

    return awc.post(
        api="apply",
        data={
            "author": util.truncate(author, const.MAX_AUTHOR_LEN),
            "content": util.truncate(content, const.MAX_CONTENT_LEN),
        },
    )


def whoami(awc: Awc) -> str:
    """returns your username ( if youre in the whitelist )"""
    return awc.get(api="whoami").text


def get_comment_lock(awc: Awc) -> bool:
    """gets comments lock status"""
    return awc.get(api="lock").text == "1"


@Awc.require_key
def toggle_comment_lock(awc: Awc) -> bool:
    """toggles comments lock status"""
    return awc.post(api="lock").text == "1"


def amiadmin(awc: Awc) -> bool:
    """returns your admin status ( 1 if API key is correct ( you are admin ) )"""
    return awc.get(api="amiadmin").text == "1"
