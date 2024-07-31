import asyncio
import typing as t

import pytest

from htpy import Node, aiter_node, iter_node


@pytest.fixture(scope="session")
def django_env() -> None:
    import django
    from django.conf import settings

    settings.configure(
        TEMPLATES=[
            {"BACKEND": "django.template.backends.django.DjangoTemplates"},
            {"BACKEND": "htpy.django.HtpyTemplateBackend", "NAME": "htpy"},
        ]
    )
    django.setup()


@pytest.fixture(params=["sync", "async"])
def to_list(request: pytest.FixtureRequest) -> t.Any:
    def func(node: Node) -> t.Any:
        if request.param == "sync":
            return list(iter_node(node))
        else:

            async def get_list() -> t.Any:
                return [chunk async for chunk in aiter_node(node)]

            return asyncio.run(get_list(), debug=True)

    return func


@pytest.fixture
def to_str(to_list: t.Any) -> t.Any:
    return lambda node: "".join(to_list(node))
