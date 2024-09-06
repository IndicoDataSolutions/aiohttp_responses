import json as jsonlib
import re
import typing as t

from aiohttp.client import StrOrURL

from .response import MockResponse


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
        if "json" in self.req_kwargs:
            try:
                # This try-except is a temp patch for now to unblock intake work
                # Consider making it easier to pass custom serializers so that
                # we can round-trip without causing failures where
                # atmosphere would have accepted it.
                self.req_kwargs["json"] = self.json_deserializer(
                    self.json_serializer(self.req_kwargs["json"])
                )
            except Exception as e:
                pass

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
        bytes: bytes = None,
        status: int = 200,
        callback: t.Callable = None,
        **attrs,
    ) -> MockResponse:
        self.saved_response = resp = MockResponse(
            url=self.str_or_url,
            status=status,
            json=json,
            text=text,
            bytes=bytes,
            callback=callback,
            attrs=attrs,
        )
        return resp

    def get_response(self) -> MockResponse:
        return self.saved_response

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.str_or_url}, "
            f"req_kwargs={self.req_kwargs}, use_regex={self.use_regex})"
        )
