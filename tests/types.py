import typing as t
from collections.abc import Callable

from htpy import Node

ToStr: t.TypeAlias = Callable[[Node], str]
ToList: t.TypeAlias = Callable[[Node], list[str]]
