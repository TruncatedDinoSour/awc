#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sql helpers"""

import typing

import pypika.queries  # type: ignore

from .. import const, util
from . import Ban, Comment, IpQueue, IpWhitelist, delete


def whitelist(author: str) -> typing.List[pypika.queries.QueryBuilder]:
    """whitelist a user"""

    author = util.truncate(author, const.MAX_AUTHOR_LEN)

    return [
        IpWhitelist.add(
            IpQueue.select(IpQueue.author == author, "ip"),  # type: ignore
            IpQueue.select(IpQueue.author == author, "author"),  # type: ignore
        ),
        delete(IpQueue.query(IpQueue.author == author).limit(1)),  # type: ignore
    ]


def unwhitelist(author: str) -> typing.List[pypika.queries.QueryBuilder]:
    """unwhitelist a user"""

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


def ban(author: str) -> typing.List[pypika.queries.QueryBuilder]:
    """ban a user"""

    author = util.truncate(author, const.MAX_AUTHOR_LEN)

    return [
        Ban.add(IpWhitelist.select(IpWhitelist.author == author, "ip"))  # type: ignore
    ] + unwhitelist(author)


def unban(ip: str) -> typing.List[pypika.queries.QueryBuilder]:
    """unban a user"""
    return [delete(Ban.query(Ban.ip == ip).limit(1))]  # type: ignore


def censor_comments(
    where: pypika.queries.QueryBuilder,
    censoring: str = "[censored]",
) -> typing.List[pypika.queries.QueryBuilder]:
    """censor comments"""
    return [
        Comment.t.update()  # type: ignore
        .set(Comment.author, censoring)
        .set(Comment.content, censoring)
        .where(where)
    ]


def set_comments_admin(
    where: pypika.queries.QueryBuilder,
    value: bool = True,
) -> typing.List[pypika.queries.QueryBuilder]:
    """set admin status on comments"""
    return [Comment.t.update().set(Comment.admin, value).where(where)]  # type: ignore
