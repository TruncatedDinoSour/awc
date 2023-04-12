#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""awc warnings"""


class AWCWarning(Warning):
    """base awc warning"""

    message: str

    def __str__(self) -> str:
        return self.message


class ContentTruncatedWarning(AWCWarning, Warning):
    """raised when content is being truncated"""

    content: str
    to: int

    def __init__(self, content: str, to: int) -> None:
        self.message: str = f"{content[:10]!r} ... \
( {len(content)} chars ) is being truncated down to {to} chars"

        super().__init__(self.message)  # type: ignore

        self.content = content
        self.to = to
