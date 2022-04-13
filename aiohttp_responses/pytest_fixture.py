"""AIOHttp Client mocking to provide responses on match
"""
import json

import pytest

from .aiohttp_responses import aiohttp_responses as mock


@pytest.fixture
def aiohttp_response_json():
    yield (json.dumps, json.loads)


@pytest.fixture
def aiohttp_responses(aiohttp_response_json):
    dumps, loads = aiohttp_response_json
    yield mock(json_serializer=dumps, json_deserializer=loads)
