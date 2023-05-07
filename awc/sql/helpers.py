#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sql helpers"""

import typing

import pypika.queries  # type: ignore

from .. import const, util
from . import AnonMsg, Ban, Comment, IpQueue, IpWhitelist, delete


def whitelist(author: str) -> typing.List[pypika.queries.QueryBuilder]:
    """whitelist a user

    author: str -- the aplicant ( author ) to whitelist from the queue

    return typing.List[pypika.queries.QueryBuilder] -- the queries"""

    author = util.truncate(author, const.MAX_AUTHOR_LEN)

    return [
        IpWhitelist.add(
            IpQueue.select(IpQueue.author == author, "ip"),  # type: ignore
            IpQueue.select(IpQueue.author == author, "author"),  # type: ignore
        ),
        delete(IpQueue.query(IpQueue.author == author).limit(1)),  # type: ignore
    ]


def unwhitelist(author: str) -> typing.List[pypika.queries.QueryBuilder]:
    """unwhitelist a user

    author: str -- the aplicant ( author ) to unwhitelist

    return typing.List[pypika.queries.QueryBuilder] -- the queries"""

    return [
        delete(
            IpWhitelist.query(
                IpWhitelist.author
                == util.truncate(  # type: ignore
                    author,
                    const.MAX_AUTHOR_LEN,
                )
            )
        ),
    ]


def ban_ip(ip: pypika.queries.QueryBuilder) -> typing.List[pypika.queries.QueryBuilder]:
    """ban an ip

    ip: pypika.queries.QueryBuilder -- the query to get the user ip

    return typing.List[pypika.queries.QueryBuilder] -- the queries"""

    return [Ban.add(ip)]  # type: ignore


def ban(author: str) -> typing.List[pypika.queries.QueryBuilder]:
    """ban and unwhitelist a user

    author: str -- the author to ip ban ( needs to be whitelisted )

    return typing.List[pypika.queries.QueryBuilder] -- the queries"""

    author = util.truncate(author, const.MAX_AUTHOR_LEN)

    return [
        *ban_ip(IpWhitelist.select(IpWhitelist.author == author, "ip"))  # type: ignore
    ] + unwhitelist(author)


def unban(ip: str) -> typing.List[pypika.queries.QueryBuilder]:
    """unban an IP

    ip: str -- the SHA256 hash of the IP being unbannned

    return typing.List[pypika.queries.QueryBuilder] -- the queries"""
    return [delete(Ban.query(Ban.ip == ip).limit(1))]  # type: ignore


def censor_comments(
    where: pypika.queries.QueryBuilder,
    censoring: str = "[censored]",
) -> typing.List[pypika.queries.QueryBuilder]:
    """censor comments

    where: pypika.queries.QueryBuilder -- the condition on which to censor
    censoring: str = "[censored]" -- the string to use for censoring

    return typing.List[pypika.queries.QueryBuilder] -- the queries"""
    return [
        Comment.set(
            where,
            {
                Comment.author: censoring,
                Comment.content: censoring,
            },
        )
    ]


def get_anon_msg(ip: str) -> typing.List[pypika.queries.QueryBuilder]:
    """get an anonymous message by id

    ip: str -- content id ( ip )

    return typing.List[pypika.queries.QueryBuilder] -- the queries"""
    return [AnonMsg.select(AnonMsg.cid == ip, AnonMsg.content)]  # type: ignore


def del_anon_msg(ip: str) -> typing.List[pypika.queries.QueryBuilder]:
    """delete an anonymous message by id

    ip: str -- content id ( ip )

    return typing.List[pypika.queries.QueryBuilder] -- the queries"""
    return [delete(AnonMsg.query(AnonMsg.cid == ip))]  # type: ignore
