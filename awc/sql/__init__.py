#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sql models and wrappers for awc"""

import typing
from abc import ABC

import pypika  # type: ignore
import pypika.queries  # type: ignore
import pypika.terms  # type: ignore


class SQLTable(ABC):
    """base class for awc sql tables"""

    t: pypika.Table
    tnane: str

    @classmethod
    def select(
        cls,
        where: pypika.queries.QueryBuilder,
        *select: str,
    ) -> pypika.queries.QueryBuilder:
        """select statement

        where: pypika.queries.QueryBuilder -- the condition on which to select
        *select: str -- what fields to select

        return pypika.queries.QueryBuilder -- the query"""
        return (
            pypika.Query.from_(cls.t)  # type: ignore
            .select(
                *(select or ("*",)),
            )
            .where(where)
        )

    @classmethod
    def query(
        cls,
        where: pypika.queries.QueryBuilder,
    ) -> pypika.queries.QueryBuilder:
        """select table row

        where: pypika.queries.QueryBuilder -- the condition on which to select

        return pypika.queries.QueryBuilder -- the query"""
        return pypika.Query.from_(cls.t).where(where)  # type: ignore

    @classmethod
    def add(
        cls,
        *what: typing.Any,
    ) -> pypika.queries.QueryBuilder:
        """insert statement

        *what: typing.Any -- VALUES() to insert

        return pypika.queries.QueryBuilder -- the query"""
        return pypika.Query.into(cls.t).insert(what)  # type: ignore

    @classmethod
    def all(cls) -> pypika.queries.QueryBuilder:
        """select the whole table

        return pypika.queries.QueryBuilder -- `SELECT * FROM self.t` query"""
        return pypika.Query.from_(cls.t).select("*")  # type: ignore

    @classmethod
    def set(
        cls,
        where: pypika.queries.QueryBuilder,
        what: typing.Dict[pypika.Column, typing.Any],
    ) -> pypika.queries.QueryBuilder:
        """SET statement

        where: pypika.queries.QueryBuilder -- the condition on which to set
        what: dict[pypika.Column, typing.Any] -- the columns and values to set

        return pypika.queries.QueryBuilder -- the query"""
        q: pypika.queries.QueryBuilder = cls.t.update()

        for k, v in what.items():
            q = q.set(k, v)  # type: ignore

        return q.where(where)  # type: ignore

    @classmethod
    def purge(cls) -> pypika.queries.QueryBuilder:
        """purge the table ( delete everything ) **BE CAREFUL**

        return pypika.queries.QueryBuilder -- the query"""

        return pypika.Query.from_(cls.t).delete()  # type: ignore


class Comment(SQLTable):
    """comment / post table"""

    tname: str = "comments"
    t: pypika.Table = pypika.Table(tname)

    cid: pypika.Column = t.cid  # type: ignore
    content: pypika.Column = t.content  # type: ignore
    author: pypika.Column = t.author  # type: ignore
    admin: pypika.Column = t.admin  # type: ignore


class Ban(SQLTable):
    """ip bans table"""

    tname: str = "bans"
    t: pypika.Table = pypika.Table(tname)

    ip: pypika.Column = t.ip  # type: ignore


class IpWhitelist(SQLTable):
    """ip whitelist table"""

    tname: str = "whitelist"
    t: pypika.Table = pypika.Table(tname)

    ip: pypika.Column = t.ip  # type: ignore
    author: pypika.Column = t.author  # type: ignore


class IpQueue(SQLTable):
    """ip whitelist queue table"""

    tname: str = "queue"
    t: pypika.Table = pypika.Table(tname)

    ip: pypika.Column = t.ip  # type: ignore
    author: pypika.Column = t.author  # type: ignore
    content: pypika.Column = t.content  # type: ignore


class AnonMsg(SQLTable):
    """anonymous message table"""

    tname: str = "anon"
    t: pypika.Table = pypika.Table(tname)

    cid: pypika.Column = t.cid  # type: ignore
    content: pypika.Column = t.content  # type: ignore
    headers: pypika.Column = t.headers  # type: ignore


def sql(query: pypika.queries.QueryBuilder) -> str:
    """return an sql query"""
    return query.get_sql()


def multisql(
    queries: typing.List[pypika.queries.QueryBuilder],
) -> typing.Tuple[str, ...]:
    """convert a list of queries into a list of SQL string queries

    queries: typing.List[pypika.queries.QueryBuilder]
        -- the queries you want to be converted

    return typing.Tuple[str, ...] -- the converted queries"""
    return tuple(map(sql, queries))


def delete(what: pypika.queries.QueryBuilder) -> pypika.queries.QueryBuilder:
    """delete result from your query

    what: what: pypika.queries.QueryBuilder -- what to delete

    return pypika.queries.QueryBuilder -- the query"""
    return what.delete()  # type: ignore
