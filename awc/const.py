#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ari-web comments API constants"""

from typing import Tuple

MAX_CONTENT_LEN: int = 1024
MAX_AUTHOR_LEN: int = 64
MAX_APPS_ACOUNT: int = 25
MAX_FETCH_COUNT: int = 25
MAX_IP_LEN: int = 64

INSTANCE_PROTOCOLS: Tuple[str, ...] = (
    "http",
    "https",
)
