from __future__ import annotations

import typing as t

import pytest
from django.core import management
from django.forms.utils import ErrorList
from django.template import Context, Template, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.html import escape
from django.utils.safestring import SafeString

from htpy import Element, Node, div, li, ul

if t.TYPE_CHECKING:
    from django.http import HttpRequest

    from .types import ToStr


pytestmark = pytest.mark.usefixtures("django_env")


def test_template_injection() -> None:
    t = Template("<ul>{{ stuff }}</ul>")
    result = t.render(Context({"stuff": li(id="hi")["I am safe!"]}))

    assert result == '<ul><li id="hi">I am safe!</li></ul>'


def test_SafeString(to_str: ToStr) -> None:
    result = ul[SafeString("<li>hello</li>")]
    assert to_str(result) == "<ul><li>hello</li></ul>"


def test_explicit_escape(to_str: ToStr) -> None:
    result = ul[escape("<hello>")]
    assert to_str(result) == "<ul>&lt;hello&gt;</ul>"


def test_errorlist(to_str: ToStr) -> None:
    result = div[ErrorList(["my error"])]
    assert to_str(result) == """<div><ul class="errorlist"><li>my error</li></ul></div>"""


def my_template(context: dict[str, t.Any], request: HttpRequest | None) -> Element:
    return div[f"hey {context['name']}"]


def my_template_fragment(context: dict[str, t.Any], request: HttpRequest | None) -> Node:
    return [div[f"hey {context['name']}"]]


class Test_template_loader:
    def test_render_element(self) -> None:
        result = render_to_string(__name__ + ".my_template", {"name": "andreas"})
        assert result == "<div>hey andreas</div>"

    def test_render_fragment(self) -> None:
        result = render_to_string(__name__ + ".my_template_fragment", {"name": "andreas"})
        assert result == "<div>hey andreas</div>"

    def test_template_does_not_exist(self) -> None:
        with pytest.raises(TemplateDoesNotExist):
            render_to_string(__name__ + ".does_not_exist", {})

    def test_system_checks_works(self) -> None:
        # Django 5.1 requires template backends to implement a check() method.
        # This test ensures that it does not crash.
        management.call_command("check")
