from __future__ import annotations

import typing as t

from htpy import comment, div

if t.TYPE_CHECKING:
    from .types import ToStr


def test_simple(to_str: ToStr) -> None:
    assert to_str(div[comment("hi")]) == "<div><!-- hi --></div>"


def test_escape_two_dashes(to_str: ToStr) -> None:
    assert to_str(div[comment("foo--bar")]) == "<div><!-- foobar --></div>"


def test_escape_three_dashes(to_str: ToStr) -> None:
    assert to_str(div[comment("foo---bar")]) == "<div><!-- foo-bar --></div>"


def test_escape_four_dashes(to_str: ToStr) -> None:
    assert to_str(div[comment("foo----bar")]) == "<div><!-- foobar --></div>"
