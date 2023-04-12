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

## intro

`awc` is a synchronous library wrapping <https://server.ari-web.xyz/> API, that includes
wrappers for all known endpoints ( see <https://server.ari-web.xyz/git> ) and an interface
to use custom endpoints using `Awc.{request, get, post}` APIs

provided packages :

-   `awc` -- base interface for the API ( required for `awc.Awc` interface so other helpers could use it )
-   `awc.api` -- wrappers for general APIs ( signatures are `(awc: awc.Awc, ...) -> typing.Any` )
-   `awc.const` -- includes required constants for the library and you to use
    -   \* note : `ip` refers to a SHA256 hash of an IP, not an actual IP
-   `awc.exc` -- custom exceptions
-   `awc.sql` -- SQL database definitions, wrappers around pypika
    -   `awc.sql.helpers` -- SQL API helpers, pre-made SQL queries
-   `awc.util` -- utilities
-   `awc.wrn` -- custom warnings

it all starts from creating an instance of `awc.Awc` object, which is basically
a wrapper around `furl.furl` ( a parsed instance url ) and `requests.Session`
( to make requests to API endpoints ), you instantiate it like this :

```py
api: awc.Awc = awc.Awc("https://some-instance.org/", "optional api key", rate_limit_wait)
```

`rate_limit_wait` is how many seconds should the requester wait if its rate limited ( default value is `5` )

example :

```py
# will sleep 2 seconds if it gets rate limited
api: awc.Awc = awc.Awc("https://google.com/", "HIHIUHIyhu9f839uf9hiuh(U()I*)989hIOUjhfew", 2)
```

after that you are free to use the interface, make requests using the provided requester functions,
get API urls ( `api["some-api-endpoint"]` => `https://google.com/some-api-endpoint` ) and use the
provided library functions, wrappers and abstractions

also, a note : not all library functions will work if you dont have an API key, `awc.Awc.require_key`
decorator is used on all functions that require an API key to work, on no api key it will raise
`awc.exc.NoAPIKeyError` with called function name being the error message
