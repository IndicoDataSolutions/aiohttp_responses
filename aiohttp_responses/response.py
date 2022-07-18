import json as jsonlib
import typing as t


class MockResponse:
    _json: t.Dict[str, t.Any] = None
    _text: str = None
    _bytes: bytes = None

    def __init__(
        self,
        status: int = 200,
        url: str = None,
        json: t.Dict[str, t.Any] = None,
        text: str = None,
        bytes: bytes = None,
        callback: t.Callable = None,
        attrs: t.Dict[str, t.Any] = None,
    ):
        self.status = status
        self.url = url
        self._json = json
        self.callback = callback
        self._text = text or jsonlib.dumps(json)
        self._bytes = bytes or self._text.encode("utf-8")

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

    async def json(self, *args, **kwargs):
        return self._json

    async def read(self):
        return self._bytes

    def release(self):
        pass

    @property
    def ok(self):
        return self.status < 400
