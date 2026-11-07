"""Fault injection at real HTTP boundaries, without replacing transport code."""

from dataclasses import dataclass, field

import pytest
from aiohttp import ClientSession, web
from pytest_aiohttp.plugin import AiohttpServer

from custom_components.closet.client import Actor, ClosetClient, ResponseTooLarge
from custom_components.closet.const import MAX_RESPONSE_BYTES


@dataclass
class ProtocolServer:
    """Record actual wire requests and serve controlled HTTP fault responses."""

    requests: list[web.Request] = field(default_factory=list)
    body: bytes = b"{}"
    status: int = 200
    redirects: int = 0

    async def handle(self, request: web.Request) -> web.Response:
        self.requests.append(request)
        return web.Response(
            body=self.body,
            status=self.status,
            headers={
                "Content-Type": "application/json",
                "ETag": '"4"',
                "Set-Cookie": "excluded-example-cookie=value",
                "Location": "/redirect-target",
            },
        )

    async def redirect_target(self, request: web.Request) -> web.Response:
        self.redirects += 1
        return web.json_response({"unexpected": True})


async def test_redirect_is_not_followed_and_headers_are_narrow(
    aiohttp_server: AiohttpServer,
    socket_enabled: None,
) -> None:
    protocol = ProtocolServer(status=302)
    app = web.Application()
    app.router.add_get("/v1/system", protocol.handle)
    app.router.add_get("/redirect-target", protocol.redirect_target)
    server = await aiohttp_server(app)
    async with ClientSession() as session:
        client = ClosetClient(
            session,
            str(server.make_url("/")).rstrip("/"),
            "fake-integration-credential",
        )
        result = await client.request("GET", "/v1/system")
    assert result.status == 302
    assert len(protocol.requests) == 1
    assert protocol.redirects == 0
    assert result.headers["ETag"] == '"4"'
    assert "Set-Cookie" not in result.headers
    assert "Location" not in result.headers


async def test_actor_and_preconditions_are_explicit_wire_context(
    aiohttp_server: AiohttpServer,
    socket_enabled: None,
) -> None:
    protocol = ProtocolServer()
    app = web.Application()
    app.router.add_post("/v1/inventory/sync", protocol.handle)
    server = await aiohttp_server(app)
    async with ClientSession() as session:
        client = ClosetClient(
            session,
            str(server.make_url("/")).rstrip("/"),
            "fake-integration-credential",
        )
        result = await client.request(
            "POST",
            "/v1/inventory/sync",
            body=b"{}",
            actor=Actor("example-user", "Example user", True),
            headers={"If-Match": '"4"', "Idempotency-Key": "example-sync"},
        )
    assert result.status == 200
    received = protocol.requests[0]
    assert received.headers["Authorization"] == "Bearer fake-integration-credential"
    assert received.headers["X-Closet-Actor-Id"] == "ha:example-user"
    assert received.headers["X-Closet-Admin"] == "true"
    assert received.headers["If-Match"] == '"4"'
    assert received.headers["Idempotency-Key"] == "example-sync"


async def test_response_size_is_bounded(
    aiohttp_server: AiohttpServer,
    socket_enabled: None,
) -> None:
    protocol = ProtocolServer(body=b" " * (MAX_RESPONSE_BYTES + 1))
    app = web.Application()
    app.router.add_get("/v1/items", protocol.handle)
    server = await aiohttp_server(app)
    async with ClientSession() as session:
        client = ClosetClient(
            session,
            str(server.make_url("/")).rstrip("/"),
            "fake-integration-credential",
        )
        with pytest.raises(ResponseTooLarge):
            await client.request("GET", "/v1/items")
    assert len(protocol.requests) == 1
