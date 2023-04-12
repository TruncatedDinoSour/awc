# awc

> ari-web comments ( awc ) API wrapper

## what

this libarary is a wrapper for <https://server.ari-web.xyz/> API
to help you manage, query and edit content using it

awc wraps pypika for sql queries and in `sql.helpers` you can access
some pre-made SQL queries, i suggest you use pypika for all ( or at least
most ) sql queries, reason being that manually writing them is
fairly insecure, especially with concat and f-strings

## examples

see the [examples](/examples) folder

## installation

```sh
python3 -m pip install --user awc
```

or ( in the cloned repo dir )

```sh
python3 -m pip install -e .
```

`-e` is for editable, you can also leave it out if you
wont be editing the library
