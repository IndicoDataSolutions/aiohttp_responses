from unittest import mock

import aiohttp
import pytest


async def test_get_request(aiohttp_responses):
    with aiohttp_responses as r:
        r.get("https://host/endpoint").response(json={"success": True})
        async with aiohttp.ClientSession() as client:
            async with client.get("https://host/endpoint") as resp:
                assert await resp.json() == {"success": True}


async def test_get_request_with_params(aiohttp_responses):
    with aiohttp_responses as r:
        r.get("https://host/endpoint", params={"param": [1, 2]}).response(
            json={"success": True}
        )
        async with aiohttp.ClientSession() as client:
            async with client.get(
                "https://host/endpoint", params={"param": [1, 2]}
            ) as resp:
                assert await resp.json() == {"success": True}

            with pytest.raises(aiohttp.ClientConnectionError):
                async with client.get(
                    "https://host/endpoint", params={"param": [1, 3]}
                ) as resp:
                    await resp.json()


async def test_post_request_with_json(aiohttp_responses):
    with aiohttp_responses as r:
        r.post("https://host/endpoint", json={"param": [1, 2]}).response(
            json={"success": True}
        )
        async with aiohttp.ClientSession() as client:
            async with client.post(
                "https://host/endpoint", json={"param": [1, 2]}
            ) as resp:
                assert await resp.json() == {"success": True}

            with pytest.raises(aiohttp.ClientConnectionError):
                async with client.post(
                    "https://host/endpoint", json={"param": [1, 3]}
                ) as resp:
                    await resp.json()


async def test_put_request_with_data(aiohttp_responses):
    with aiohttp_responses as r:
        r.post("https://host/endpoint", data="mocked data").response(
            json={"success": True}
        )
        async with aiohttp.ClientSession() as client:
            async with client.post("https://host/endpoint", data="mocked data") as resp:
                assert await resp.json() == {"success": True}

            with pytest.raises(aiohttp.ClientConnectionError):
                async with client.post(
                    "https://host/endpoint", data="not the same data"
                ) as resp:
                    await resp.json()


async def test_request_with_callback(aiohttp_responses):
    magic_mock = mock.MagicMock()

    def callback(response, request_entry, response_entry):
        assert response.ok
        magic_mock()

    with aiohttp_responses as r:
        r.post("https://host/endpoint", data="mocked data").response(
            json={"success": True}, callback=callback
        )
        async with aiohttp.ClientSession() as client:
            async with client.post("https://host/endpoint", data="mocked data") as resp:
                assert await resp.json() == {"success": True}

            with pytest.raises(aiohttp.ClientConnectionError):
                async with client.post(
                    "https://host/endpoint", data="not the same data"
                ) as resp:
                    await resp.json()

    magic_mock.assert_called_once()


@pytest.mark.skip
async def test_regex_match(aiohttp_response):
    # Need to determine behavior for regex match
    # In indico case, we would need fuzzy matching in general for regex url and kwargs
    # fuzzy matching would need to be supported with response lambda
    ...


@pytest.mark.skip
async def test_json_serialization(aiohttp_response):
    # Need to determine if we even want to care about json serialization
    # Probably not, in which case, we should remove all serialization logic from the code base
    ...
