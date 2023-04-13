#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""awc utils"""

import functools
import socket
import warnings

from .wrn import AWCWarning, ContentTruncatedWarning


@functools.lru_cache
def is_up(host: str, port: int) -> bool:
    """check if host:port is up, this result is cached

    host: str -- the hostname
    port: int -- the port you want to check"""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((host, port))
            return True
        except socket.error:
            return False


def warn(msg: AWCWarning) -> None:
    """throw a warning message

    msg: awc.wrn.AWCWarning -- the warning"""

    warnings.warn(msg, stacklevel=2)


def truncate(content: str, length: int, do_warn: bool = True) -> str:
    """truncate content and warn if appropriate

    content: str -- content you want to truncated
    length: int -- to what length should the content be truncated to
    do_warn: bool = True -- do we warn if content is being truncated

    return str -- the truncated content"""

    if do_warn and len(content) > length:
        warn(ContentTruncatedWarning(content, length))

    return content[:length]


def resp_to_bool(resp: str) -> bool:
    """convets a response like 0 and 1 to boolean

    resp: str -- the response

    return bool -- the converted boolean"""

    return resp == "1"
