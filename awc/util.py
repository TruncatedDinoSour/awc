#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""awc utils"""

import functools
import socket
import warnings

from .wrn import AWCWarning, ContentTruncatedWarning


@functools.lru_cache
def is_up(host: str, port: int) -> bool:
    """check if host:port is up, this result is cached"""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((host, port))
            return True
        except socket.error:
            return False


def warn(msg: AWCWarning) -> None:
    """throw a warning message"""

    warnings.warn(msg, stacklevel=2)


def truncate(content: str, length: int, do_warn: bool = True) -> str:
    """truncate content and warn if appropriate"""

    if do_warn and len(content) > length:
        warn(ContentTruncatedWarning(content, length))

    return content[:length]
