#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""awc example"""

import typing
from warnings import filterwarnings as filter_warnings

import awc
import awc.api
import awc.const
import awc.exc
import awc.sql  # tip : use pypika as this library is very compatible with it :)
import awc.sql.helpers

BACKUP: typing.Final[str] = "backup"  # we dont need .db as it gets added automatically
EX_SQL: typing.Tuple[str, ...] = (
    f'INSERT INTO {awc.sql.IpQueue.tname} VALUES ("some-ip-hash", "author",'
    '"let me in !!")',  # this way of doing SQL is **INSECURE**, use an SQL bulder
    awc.sql.sql(awc.sql.IpQueue.all()),
    awc.sql.sql(
        awc.sql.delete(
            awc.sql.IpQueue.query(awc.sql.IpQueue.author == "author")  # type: ignore
        )
    ),
    awc.sql.sql(awc.sql.IpQueue.all()),
)


def infinput(prompt: str) -> str:
    """infinite input"""

    value: typing.Optional[str] = None

    while not value:
        value = input(f"{prompt} :: ").strip()

    return value


def print_iter(itr: typing.Iterable[typing.Any]) -> None:
    for item in itr:
        print(f" - {item}")


def main() -> int:
    """entry / main function"""

    with open("api_key.key", "r") as api_key:
        # keep in mind, `api_key` is optional, although it will only
        # limit you to user-only actions, also you have to
        # host an instance of https://server.ari-web.xyz/git locally
        api: awc.Awc = awc.Awc("http://127.0.0.1:5000", api_key.read())

    print(
        "\n>>> just an FYI : if the request takes long that means "
        "you just got rate limited, wait the timeout out\n"
    )

    for attr in dir(awc.const):
        if attr.isupper():
            print(f"{attr} = {getattr(awc.const, attr)}")

    print()

    author: str

    try:
        author = awc.api.whoami(api)
    except awc.exc.APIRequestFailedError:
        print("you need to apply")

        author = infinput("author")

        print(
            "apply api response :",
            awc.api.apply(api, author, infinput("why do you want to join")).text,
        )

        print("accepting your application ...")

        queries: typing.Tuple[str, ...] = awc.sql.multisql(
            awc.sql.helpers.whitelist(author)
        )

        print(
            "calling the SQL api with these SQL queries and backing up "
            f"to {BACKUP}.db :"
        )

        print_iter(queries)

        # note : OPTIONAL argument `backup` ( restoration is manual )
        print("sql API response : ", awc.api.sql(api, queries))

    print(f"hello, {author!r}")

    cid, is_admin = awc.api.post_comment(api, infinput("say something to the world"))

    print(f"posted comment #{cid} with attribute {is_admin = }")

    print(
        "your comment in the database looks like this :", awc.api.get_comment(api, cid)
    )

    print(f"actually, in total, we have {awc.api.total(api)} comments !")

    print("running example queries :")
    print_iter(EX_SQL)

    print("results :")
    print_iter(awc.api.sql(api, EX_SQL))

    for _ in range(2):
        print("comments are", "locked" if awc.api.get_comment_lock(api) else "unlocked")
        print("toggled lock status :", awc.api.toggle_comment_lock(api))

    print("you are", "an" if awc.api.amiadmin(api) else "not an", "admin")

    print(f"ill call you {__name__!r} now")
    print(
        awc.api.sql(
            api,
            awc.sql.sql(
                awc.sql.IpWhitelist.set(
                    awc.sql.IpWhitelist.author == author,  # type: ignore
                    {awc.sql.IpWhitelist.author: __name__},
                )
            ),
        )
    )

    print("whoami api returned", (author := awc.api.whoami(api)))

    print(
        "anon message with id",
        (anon_id := int(awc.api.anon(api, infinput("anonymous message")).text)),
    )

    print(
        "anon msg :",
        awc.api.sql(api, awc.sql.multisql(awc.sql.helpers.get_anon_msg(anon_id))),
    )

    print("deleting the anon msg")
    print(awc.api.sql(api, awc.sql.multisql(awc.sql.helpers.del_anon_msg(anon_id))))

    print("imma ban you wait")
    print(awc.api.sql(api, awc.sql.multisql(awc.sql.helpers.ban(author))))

    print("time to unwhitelist you :)")
    print(awc.api.sql(api, awc.sql.multisql(awc.sql.helpers.unwhitelist(author))))

    # dw you can whitelist too
    print("lol okok wait, ill unban you :) ( i wont whitelist you bc i said so !! )")
    # nvm u need to unban by ip lol
    # print(awc.api.sql(api, awc.sql.multisql(awc.sql.helpers.unban(author))))
    print(awc.api.sql(api, "DELETE FROM bans"))

    # close the connection and stuff
    api.end()  # note : you can also use a `with` context manager

    return 0


if __name__ == "__main__":
    assert main.__annotations__.get("return") is int, "main() should return an integer"

    filter_warnings("error", category=Warning)
    raise SystemExit(main())
