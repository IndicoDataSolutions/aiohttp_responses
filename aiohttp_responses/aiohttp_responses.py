import json as jsonlib
import re
import sys
import typing as t
from collections import defaultdict
from copy import deepcopy
from functools import partialmethod
from unittest import mock

from aiohttp.client import ClientSession, StrOrURL

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    Literal = t.Literal


class MockResponse:
    _json: t.Dict[str, t.Any] = None
    _text: str = None

    def __init__(
        self,
        status: int = 200,
        url: str = None,
        json: t.Dict[str, t.Any] = None,
        text: str = None,
        attrs: t.Dict[str, t.Any] = None,
    ):
        self.status = status
        self.url = url
        self._json = json
        self._text = text or jsonlib.dumps(json)

        # Set attrs for flexibility
        attrs = attrs or {}
        for field, value in attrs.items():
            if field.startswith("_"):
                raise ValueError("Cannot pass underscore attrs to MockedResponse")
            setattr(self, field, value)

    def set_url(self, url: str):
        self.url = url

    async def text(self):
        return self._text

    async def json(self):
        return self._json

    def release(self):
        pass


class Entry:
    str_or_url: StrOrURL
    req_kwargs: t.Dict[str, t.Any]
    use_regex: bool
    saved_response: MockResponse
    json_serializer: t.Callable[[t.Any], str]
    json_deserializer: t.Callable[[str], t.Any]

    def __init__(
        self,
        str_or_url: StrOrURL,
        req_kwargs: t.Dict[str, t.Any],
        json_serializer: t.Callable[[t.Any], str] = jsonlib.dumps,
        json_deserializer: t.Callable[[str], t.Any] = jsonlib.loads,
        use_regex: bool = False,
    ):
        self.str_or_url = str_or_url
        self.req_kwargs = req_kwargs
        self.use_regex = use_regex
        self.json_serializer = json_serializer
        self.json_deserializer = json_deserializer

    def is_match(self, incoming: "Entry") -> bool:
        return (
            re.match(self.str_or_url, incoming.str_or_url)
            if self.use_regex
            else self.str_or_url == incoming.str_or_url
        ) and self.req_kwargs == incoming.req_kwargs

    def response(
        self,
        json: t.Dict[str, t.Any] = None,
        text: str = None,
        status: int = 200,
        **attrs,
    ) -> MockResponse:
        self.saved_response = resp = MockResponse(
            url=self.str_or_url, status=status, json=json, text=text, attrs=attrs
        )
        return resp

    def get_response(self) -> MockResponse:
        return self.saved_response

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.str_or_url}, "
            f"req_kwargs={self.req_kwargs}, use_regex={self.use_regex})"
        )


HTTP_METHODS = Literal["get", "post", "put", "delete", "patch"]


class aiohttp_responses:
    default_supported_kwargs: t.Iterable[str] = (
        "params",
        "data",
        "json",
        "cookies",
        "headers",
    )

    json_serializer: t.Callable[[t.Any], str]
    json_deserializer: t.Callable[[str], t.Any]

    # Internal Use
    _entry_registry: t.Dict[HTTP_METHODS, t.Any]
    _supported_kwargs: t.Iterable[str]

    _original: t.Dict[HTTP_METHODS, t.Any]

    def __init__(
        self,
        json_serializer: t.Callable[[t.Any], str] = jsonlib.dumps,
        json_deserializer: t.Callable[[str], t.Any] = jsonlib.loads,
        supported_kwargs: t.Iterable[str] = None,
    ):
        self.json_serializer = json_serializer
        self.json_deserializer = json_deserializer
        self._entry_registry = defaultdict(list)
        self._supported_kwargs = self.default_supported_kwargs + (
            supported_kwargs or tuple()
        )

    def create_entry(
        self,
        str_or_url: StrOrURL,
        req_kwargs: t.Dict[str, t.Any],
        use_regex: bool = False,
    ) -> Entry:
        return Entry(
            str_or_url,
            {
                k: v
                for k, v in req_kwargs.items()
                if k in self._supported_kwargs and v is not None
            },
            use_regex=use_regex,
        )

    def match(self, method: str, str_or_url: StrOrURL, req_kwargs: t.Dict[str, t.Any]):
        target = self.create_entry(str_or_url, req_kwargs)
        for entry in self._entry_registry[method.lower()]:
            if entry.is_match(target):
                return entry.get_response()

    def add(
        self,
        method: str,
        str_or_url: StrOrURL,
        use_regex: bool = False,
        **req_kwargs: t.Dict[str, t.Any],
    ) -> Entry:
        entry = self.create_entry(str_or_url, req_kwargs, use_regex=use_regex)
        self._entry_registry[method].append(entry)
        return entry

    def __enter__(self):
        self._saved_registry = deepcopy(self._entry_registry)
        orig = ClientSession._request

        async def _mocked_request(cs, method: str, str_or_url: StrOrURL, **req_kwargs):
            response = self.match(method, str_or_url, req_kwargs)
            if response:
                # For regex.
                response.set_url(str_or_url)
                return response
            return await orig(cs, method, str_or_url, **req_kwargs)

        self._patch = mock.patch.object(ClientSession, "_request", _mocked_request)
        self._patch.start()
        return self

    def __exit__(self, _, __, ___):
        self._entry_registry = self._saved_registry
        del self._saved_registry
        self._patch.stop()

    """ Mocking Interface """
    delete = partialmethod(add, "delete")
    get = partialmethod(add, "get")
    patch = partialmethod(add, "patch")
    post = partialmethod(add, "post")
    put = partialmethod(add, "put")
