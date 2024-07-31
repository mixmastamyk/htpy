from __future__ import annotations

import typing as t

import pytest
from markupsafe import Markup

from htpy import button, div, th

if t.TYPE_CHECKING:
    from .types import ToStr


def test_attribute() -> None:
    assert str(div(id="hello")["hi"]) == '<div id="hello">hi</div>'


class Test_class_names:
    def test_str(self, to_str: ToStr) -> None:
        result = div(class_='">foo bar')
        assert to_str(result) == '<div class="&#34;&gt;foo bar"></div>'

    def test_safestring(self, to_str: ToStr) -> None:
        result = div(class_=Markup('">foo bar'))
        assert to_str(result) == '<div class="&#34;&gt;foo bar"></div>'

    def test_list(self, to_str: ToStr) -> None:
        result = div(class_=['">foo', Markup('">bar'), False, None, "", "baz"])
        assert to_str(result) == '<div class="&#34;&gt;foo &#34;&gt;bar baz"></div>'

    def test_tuple(self, to_str: ToStr) -> None:
        result = div(class_=('">foo', Markup('">bar'), False, None, "", "baz"))
        assert to_str(result) == '<div class="&#34;&gt;foo &#34;&gt;bar baz"></div>'

    def test_dict(self, to_str: ToStr) -> None:
        result = div(class_={'">foo': True, Markup('">bar'): True, "x": False, "baz": True})
        assert to_str(result) == '<div class="&#34;&gt;foo &#34;&gt;bar baz"></div>'

    def test_nested_dict(self, to_str: ToStr) -> None:
        result = div(
            class_=[
                '">list-foo',
                Markup('">list-bar'),
                {'">dict-foo': True, Markup('">list-bar'): True, "x": False},
            ]
        )
        assert to_str(result) == (
            '<div class="&#34;&gt;list-foo &#34;&gt;list-bar '
            '&#34;&gt;dict-foo &#34;&gt;list-bar"></div>'
        )

    def test_false(self, to_str: ToStr) -> None:
        result = to_str(div(class_=False))
        assert result == "<div></div>"

    def test_none(self, to_str: ToStr) -> None:
        result = to_str(div(class_=None))
        assert result == "<div></div>"

    def test_no_classes(self, to_str: ToStr) -> None:
        result = to_str(div(class_={"foo": False}))
        assert result == "<div></div>"


def test_dict_attributes(to_str: ToStr) -> None:
    result = div({"@click": 'hi = "hello"'})

    assert to_str(result) == """<div @click="hi = &#34;hello&#34;"></div>"""


def test_underscore(to_str: ToStr) -> None:
    # Hyperscript (https://hyperscript.org/) uses _, make sure it works good.
    result = div(_="foo")
    assert to_str(result) == """<div _="foo"></div>"""


def test_dict_attributes_avoid_replace(to_str: ToStr) -> None:
    result = div({"class_": "foo", "hello_hi": "abc"})
    assert to_str(result) == """<div class_="foo" hello_hi="abc"></div>"""


def test_dict_attribute_false(to_str: ToStr) -> None:
    result = div({"bool-false": False})
    assert to_str(result) == "<div></div>"


def test_dict_attribute_true(to_str: ToStr) -> None:
    result = div({"bool-true": True})
    assert to_str(result) == "<div bool-true></div>"


def test_underscore_replacement(to_str: ToStr) -> None:
    result = button(hx_post="/foo")["click me!"]
    assert to_str(result) == """<button hx-post="/foo">click me!</button>"""


class Test_attribute_escape:
    pytestmark = pytest.mark.parametrize(
        "x",
        [
            '<"foo',
            Markup('<"foo'),
        ],
    )

    def test_dict(self, x: str, to_str: ToStr) -> None:
        result = div({x: x})
        assert to_str(result) == """<div &lt;&#34;foo="&lt;&#34;foo"></div>"""

    def test_kwarg(self, x: str, to_str: ToStr) -> None:
        result = div(**{x: x})
        assert to_str(result) == """<div &lt;&#34;foo="&lt;&#34;foo"></div>"""


def test_boolean_attribute_true(to_str: ToStr) -> None:
    result = button(disabled=True)
    assert to_str(result) == "<button disabled></button>"


def test_kwarg_attribute_none(to_str: ToStr) -> None:
    result = div(foo=None)
    assert to_str(result) == "<div></div>"


def test_dict_attribute_none(to_str: ToStr) -> None:
    result = div({"foo": None})
    assert to_str(result) == "<div></div>"


def test_boolean_attribute_false(to_str: ToStr) -> None:
    result = button(disabled=False)
    assert to_str(result) == "<button></button>"


def test_integer_attribute(to_str: ToStr) -> None:
    result = th(colspan=123)
    assert to_str(result) == '<th colspan="123"></th>'


def test_id_class(to_str: ToStr) -> None:
    result = div("#myid.cls1.cls2")
    assert to_str(result) == """<div id="myid" class="cls1 cls2"></div>"""


def test_id_class_only_id(to_str: ToStr) -> None:
    result = div("#myid")
    assert to_str(result) == """<div id="myid"></div>"""


def test_id_class_only_classes(to_str: ToStr) -> None:
    result = div(".foo.bar")
    assert to_str(result) == """<div class="foo bar"></div>"""


def test_id_class_wrong_order() -> None:
    with pytest.raises(ValueError, match="id \\(#\\) must be specified before classes \\(\\.\\)"):
        div(".myclass#myid")


def test_id_class_bad_format() -> None:
    with pytest.raises(ValueError, match="id/class strings must start with # or ."):
        div("foo")


def test_id_class_bad_type() -> None:
    with pytest.raises(ValueError, match="id/class strings must be str. got {'oops': 'yes'}"):
        div({"oops": "yes"}, {})  # type: ignore


def test_id_class_and_kwargs(to_str: ToStr) -> None:
    result = div("#theid", for_="hello", data_foo="<bar")
    assert to_str(result) == """<div id="theid" for="hello" data-foo="&lt;bar"></div>"""


def test_attrs_and_kwargs(to_str: ToStr) -> None:
    result = div({"a": "1", "for": "a"}, for_="b", b="2")
    assert to_str(result) == """<div a="1" for="b" b="2"></div>"""


def test_class_priority(to_str: ToStr) -> None:
    result = div(".a", {"class": "b"}, class_="c")
    assert to_str(result) == """<div class="c"></div>"""

    result = div(".a", {"class": "b"})
    assert to_str(result) == """<div class="b"></div>"""


def test_attribute_priority(to_str: ToStr) -> None:
    result = div({"foo": "a"}, foo="b")
    assert to_str(result) == """<div foo="b"></div>"""


@pytest.mark.parametrize("not_an_attr", [1234, b"foo", object(), object, 1, 0, None])
def test_invalid_attribute_key(not_an_attr: t.Any, to_str: ToStr) -> None:
    with pytest.raises(ValueError, match="Attribute key must be a string"):
        to_str(div({not_an_attr: "foo"}))


@pytest.mark.parametrize(
    "not_an_attr",
    [12.34, b"foo", object(), object],
)
def test_invalid_attribute_value(not_an_attr: t.Any, to_str: ToStr) -> None:
    with pytest.raises(ValueError, match="Attribute value must be a string"):
        div(foo=not_an_attr)
