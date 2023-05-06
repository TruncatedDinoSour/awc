#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ari-web comments api wrappers"""

import typing

import requests

from . import Awc, const, exc, util


def post_comment(awc: Awc, content: str) -> typing.List[typing.Union[int, bool]]:
    """post a comment

    awc: awc.Awc -- the awc.Awc instance to work on
    content: str(const.MAX_CONTENT_LEN) -- the comment content

    return typing.List[typing.Union[int, bool]] -- [comment id, is admin]"""

    try:
        return awc.post(
            data={"content": util.truncate(content, const.MAX_CONTENT_LEN)}
        ).json()
    except requests.exceptions.InvalidJSONError as e:
        raise exc.UnexpectedResponseError(
            e.response.text, typing.List[typing.Union[int, bool]]
        ) from e


def get_comments(
    awc: Awc, from_id: int, to_id: int
) -> typing.Dict[str, typing.List[typing.Union[str, bool, None]]]:
    """get comments in range from-to, range is to_id >= cid >= from_id

    awc: awc.Awc -- the awc.Awc instance to work on
    from_id: int -- the comment ID to begin the range from
    to_id: int -- the comment ID to end the range with

    raise
        ValueError -- on from_id > to_id
        ValueError -- on abs(to_id - from_id) > awc.const.MAX_FETCH_COUNT
        awc.exc.UnexpectedResponseError -- on invalid returned JSON

    return typing.Dict[str, typing.List[typing.Union[str, bool, None]]] -- comments"""

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
        ) from e


def get_comment(awc: Awc, cid: int) -> typing.List[typing.Union[str, bool, None]]:
    """get coment by ID

    awc: awc.Awc -- the awc.Awc instance to work on
    cid: int -- same as both from_id and to_id arguments to `get_comments`

    raise
        awc.exc.ResouceNotFoundError from KeyError -- on a comment not found

    return typing.List[typing.Union[str, bool, None]] -- the comment"""

    try:
        return get_comments(awc, cid, cid)[str(cid)]
    except KeyError as e:
        raise exc.ResouceNotFoundError(cid) from e


def total(awc: Awc) -> int:
    """total comments count api

    awc: awc.Awc -- the awc.Awc instance to work on

    raise
        awc.exc.UnexpectedResponseError from ValueError -- when returned response is NaN

    return int -- total comments count"""

    r: requests.Response = awc.get(api="total")

    try:
        return int(r.text)
    except ValueError as e:
        raise exc.UnexpectedResponseError(r.text, int) from e


@Awc.require_key
def sql(
    awc: Awc, queries: typing.Iterable[str], backup: typing.Optional[str] = None
) -> typing.List[typing.List[typing.Any]]:
    """run SQL queries

    awc: awc.Awc -- the awc.Awc instance to work on
    queries: typing.Iterable[str] -- the queries to run
    backup: str | None = None -- optionally set backup database name

    raise
        awc.exc.UnexpectedResponseError from requests.exceptions.InvalidJSONError --
            on invalid JSON
        ValueError -- on invalid queries

    return typing.List[typing.List[typing.Any]] -- query results"""

    data: typing.Dict[str, typing.Union[typing.Iterable[str], str]] = {"sql": queries}

    if backup is not None:
        data["backup"] = backup

    try:
        return awc.post(api="sql", data=data).json()  # type: ignore
    except requests.exceptions.InvalidJSONError as e:
        raise exc.UnexpectedResponseError(
            e.response.text, typing.Dict[int, typing.List[typing.List[typing.Any]]]
        ) from e


def apply(awc: Awc, author: str, content: str) -> requests.Response:
    """apply to the whitelist

    awc: awc.Awc -- the awc.Awc instance to work on
    author: str -- the author / username you want to have
    content: str -- the reason why youre applying

    return requests.Response -- the apply API response"""

    return awc.post(
        api="apply",
        data={
            "author": util.truncate(author, const.MAX_AUTHOR_LEN),
            "content": util.truncate(content, const.MAX_CONTENT_LEN),
        },
    )


def whoami(awc: Awc) -> str:
    """returns your username ( if youre in the whitelist )

    awc: awc.Awc -- the awc.Awc instance to work on"""
    return awc.get(api="whoami").text


def get_comment_lock(awc: Awc) -> bool:
    """gets comments lock status

    awc: awc.Awc -- the awc.Awc instance to work on"""
    return util.resp_to_bool(awc.get(api="lock").text)


@Awc.require_key
def toggle_comment_lock(awc: Awc) -> bool:
    """toggles comments lock status

    awc: awc.Awc -- the awc.Awc instance to work on"""
    return util.resp_to_bool(awc.post(api="lock").text)


def amiadmin(awc: Awc) -> bool:
    """returns your admin status ( `True` if API key is correct ( you are admin ) )

    awc: awc.Awc -- the awc.Awc instance to work on"""
    return util.resp_to_bool(awc.get(api="amiadmin").text)


def applied(awc: Awc) -> bool:
    """returns your application status ( `True` if applied / accepted )

    awc: awc.Awc -- the awc.Awc instance to work on"""
    return util.resp_to_bool(awc.get(api="applied").text)


def anon(awc: Awc, content: str) -> requests.Response:
    """send message to server anonymously

    awc: awc.Awc -- the awc.Awc instance to work on
    content: str -- the reason why youre applying

    return requests.Response -- the id of the message"""

    return awc.post(
        api="anon",
        data={
            "content": util.truncate(content, const.MAX_CONTENT_LEN),
        },
    )
