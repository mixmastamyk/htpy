from __future__ import annotations

import dataclasses
import datetime
import decimal
import pathlib
import re
import typing as t

import pytest
from markupsafe import Markup
from typing_extensions import assert_type

from htpy import Element, VoidElement, dd, div, dl, dt, html, img, input, li, my_custom_element, ul

if t.TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from htpy import Node

    from .types import ToList, ToStr


def test_void_element(to_str: ToStr) -> None:
    result = input(name="foo")
    assert_type(result, VoidElement)
    assert isinstance(result, VoidElement)

    assert to_str(result) == '<input name="foo">'


def test_integer_child(to_str: ToStr) -> None:
    assert to_str(div[123]) == "<div>123</div>"


def test_children(to_str: ToStr) -> None:
    assert to_str(div[img]) == "<div><img></div>"


def test_multiple_children(to_str: ToStr) -> None:
    result = ul[li, li]

    assert to_str(result) == "<ul><li></li><li></li></ul>"


def test_list_children(to_str: ToStr) -> None:
    children: list[Element] = [li["a"], li["b"]]
    result = ul[children]
    assert to_str(result) == "<ul><li>a</li><li>b</li></ul>"


def test_tuple_children(to_str: ToStr) -> None:
    result = ul[(li["a"], li["b"])]
    assert to_str(result) == "<ul><li>a</li><li>b</li></ul>"


def test_flatten_nested_children(to_str: ToStr) -> None:
    result = dl[
        [
            (dt["a"], dd["b"]),
            (dt["c"], dd["d"]),
        ]
    ]
    assert to_str(result) == """<dl><dt>a</dt><dd>b</dd><dt>c</dt><dd>d</dd></dl>"""


def test_flatten_very_nested_children(to_str: ToStr) -> None:
    # maybe not super useful but the nesting may be arbitrarily deep
    result = div[[([["a"]],)], [([["b"]],)]]
    assert to_str(result) == """<div>ab</div>"""


def test_flatten_nested_generators(to_str: ToStr) -> None:
    def cols() -> Generator[str, None, None]:
        yield "a"
        yield "b"
        yield "c"

    def rows() -> Generator[Generator[str, None, None], None, None]:
        yield cols()
        yield cols()
        yield cols()

    result = div[rows()]

    assert to_str(result) == """<div>abcabcabc</div>"""


def test_generator_children(to_str: ToStr) -> None:
    gen: Generator[Element, None, None] = (li[x] for x in ["a", "b"])
    result = ul[gen]
    assert to_str(result) == "<ul><li>a</li><li>b</li></ul>"


def test_html_tag_with_doctype(to_str: ToStr) -> None:
    result = html(foo="bar")["hello"]
    assert to_str(result) == '<!doctype html><html foo="bar">hello</html>'


def test_void_element_children(to_str: ToStr) -> None:
    with pytest.raises(TypeError):
        img["hey"]  # type: ignore[index]


def test_call_without_args(to_str: ToStr) -> None:
    result = img()
    assert to_str(result) == "<img>"


def test_custom_element(to_str: ToStr) -> None:
    result = my_custom_element()
    assert_type(result, Element)
    assert isinstance(result, Element)
    assert to_str(result) == "<my-custom-element></my-custom-element>"


@pytest.mark.parametrize("ignored_value", [None, True, False])
def test_ignored(to_str: ToStr, ignored_value: t.Any) -> None:
    assert to_str(div[ignored_value]) == "<div></div>"


def test_sync_iter() -> None:
    trace = "not started"

    def generate_list() -> Generator[Element, None, None]:
        nonlocal trace

        trace = "before yield"
        yield li("#a")

        trace = "done"

    iterator = iter(ul[generate_list()])

    assert next(iterator) == "<ul>"
    assert trace == "not started"

    assert next(iterator) == '<li id="a">'
    assert trace == "before yield"
    assert next(iterator) == "</li>"
    assert trace == "before yield"

    assert next(iterator) == "</ul>"
    assert trace == "done"


def test_iter_str(to_list: ToList) -> None:
    _, child, _ = to_list(div["a"])

    assert child == "a"
    # Make sure we dont get Markup (subclass of str)
    assert type(child) is str


def test_iter_markup() -> None:
    _, child, _ = div["a"]

    assert child == "a"
    # Make sure we dont get Markup (subclass of str)
    assert type(child) is str


def test_callable() -> None:
    called = False

    def generate_img() -> VoidElement:
        nonlocal called
        called = True
        return img

    iterator = iter(div[generate_img])

    assert next(iterator) == "<div>"
    assert called is False
    assert next(iterator) == "<img>"
    assert called is True
    assert next(iterator) == "</div>"


def test_escape_children() -> None:
    result = str(div['>"'])
    assert result == "<div>&gt;&#34;</div>"


def test_safe_children() -> None:
    result = str(div[Markup("<hello></hello>")])
    assert result == "<div><hello></hello></div>"


def test_nested_callable_generator() -> None:
    def func() -> Generator[str, None, None]:
        return (x for x in "abc")

    assert str(div[func]) == "<div>abc</div>"


def test_nested_callables() -> None:
    def first() -> Callable[[], Node]:
        return second

    def second() -> Node:
        return "hi"

    assert str(div[first]) == "<div>hi</div>"


def test_callable_in_generator() -> None:
    assert str(div[((lambda: "hi") for _ in range(1))]) == "<div>hi</div>"


@dataclasses.dataclass
class MyDataClass:
    name: str


class SomeClass:
    pass


# Various types that are not valid children.
_invalid_children = [
    12.34,
    decimal.Decimal("12.34"),
    complex("+1.23"),
    object(),
    datetime.date(1, 2, 3),
    datetime.datetime(1, 2, 3),
    datetime.time(1, 2),
    b"foo",
    bytearray(b"foo"),
    memoryview(b"foo"),
    Exception("foo"),
    Ellipsis,
    re.compile("foo"),
    pathlib.Path("FOO"),
    re,  # module type
    MyDataClass(name="Andreas"),
    SomeClass(),
]


@pytest.mark.parametrize("not_a_child", _invalid_children)
def test_invalid_child_direct(not_a_child: t.Any) -> None:
    with pytest.raises(ValueError, match="is not a valid child element"):
        div[not_a_child]


@pytest.mark.parametrize("not_a_child", _invalid_children)
def test_invalid_child_nested_iterable(not_a_child: t.Any) -> None:
    with pytest.raises(ValueError, match="is not a valid child element"):
        div[[not_a_child]]


@pytest.mark.parametrize("not_a_child", _invalid_children)
def test_invalid_child_lazy_callable(not_a_child: t.Any) -> None:
    """
    Ensure proper exception is raised for lazily evaluated invalid children.
    """
    element = div[lambda: not_a_child]
    with pytest.raises(ValueError, match="is not a valid child element"):
        str(element)


@pytest.mark.parametrize("not_a_child", _invalid_children)
def test_invalid_child_lazy_generator(not_a_child: t.Any) -> None:
    """
    Ensure proper exception is raised for lazily evaluated invalid children.
    """

    def gen() -> t.Any:
        yield not_a_child

    element = div[gen()]
    with pytest.raises(ValueError, match="is not a valid child element"):
        str(element)
