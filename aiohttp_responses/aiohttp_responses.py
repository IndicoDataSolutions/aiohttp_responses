import json as jsonlib
import sys
import typing as t
from collections import defaultdict
from copy import deepcopy
from functools import partialmethod
from unittest import mock

from aiohttp.client import ClientSession, StrOrURL

from .entry import Entry
from .response import MockResponse

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    Literal = t.Literal

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
    _response_cls: t.Type[MockResponse]
    _original: t.Dict[HTTP_METHODS, t.Any]

    def __init__(
        self,
        json_serializer: t.Callable[[t.Any], str] = jsonlib.dumps,
        json_deserializer: t.Callable[[str], t.Any] = jsonlib.loads,
        response_cls: t.Type[MockResponse] = MockResponse,
        supported_kwargs: t.Iterable[str] = None,
    ):
        self.json_serializer = json_serializer
        self.json_deserializer = json_deserializer
        self._response_cls = response_cls
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
                response = entry.get_response()
                if response.callback:
                    response.callback(response, target, entry)
                return response

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
