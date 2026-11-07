"""Bounded, fixed-destination HTTP transport to Closet."""

from dataclasses import dataclass
from urllib.parse import urlsplit

from aiohttp import ClientSession, ClientTimeout
from homeassistant.util.json import JsonObjectType, json_loads_object

from .const import MAX_RESPONSE_BYTES, REQUEST_TIMEOUT_SECONDS


class InvalidBackendURL(ValueError):
    """The backend must be an HTTP origin without credentials or a path."""


class ResponseTooLarge(ValueError):
    """The backend exceeded the adapter response limit."""


def normalize_backend_url(value: str) -> str:
    """Accept an explicit origin, never a caller-selected request destination."""
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as err:
        raise InvalidBackendURL from err
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
        or any(character.isspace() for character in value)
        or "\\" in value
        or port == 0
    ):
        raise InvalidBackendURL
    return value.rstrip("/")


@dataclass(frozen=True, slots=True)
class Actor:
    """Trusted HA user context, constructed only after HA authentication."""

    id: str
    name: str
    admin: bool


@dataclass(frozen=True, slots=True)
class BackendResponse:
    """The bounded response and public protocol headers."""

    status: int
    body: bytes
    headers: dict[str, str]

    def json(self) -> JsonObjectType:
        """Decode the upstream document at the dynamic HTTP boundary."""
        return json_loads_object(self.body)


class ClosetClient:
    """Use HA's shared session; never retry, redirect, or own its lifecycle."""

    def __init__(self, session: ClientSession, backend_url: str, token: str) -> None:
        self._session = session
        self._backend_url = normalize_backend_url(backend_url)
        self._token = token

    async def request(
        self,
        method: str,
        path: str,
        *,
        body: bytes | None = None,
        actor: Actor | None = None,
        headers: dict[str, str] | None = None,
    ) -> BackendResponse:
        """Forward only paths and protocol headers constructed by this adapter."""
        upstream_headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }
        if body is not None:
            upstream_headers["Content-Type"] = "application/json"
        if headers:
            upstream_headers.update(headers)
        if actor is not None:
            upstream_headers.update(
                {
                    "X-Closet-Actor-Id": f"ha:{actor.id}",
                    "X-Closet-Actor-Name": actor.name,
                    "X-Closet-Admin": "true" if actor.admin else "false",
                }
            )
        async with self._session.request(
            method,
            f"{self._backend_url}{path}",
            data=body,
            headers=upstream_headers,
            allow_redirects=False,
            timeout=ClientTimeout(total=REQUEST_TIMEOUT_SECONDS),
        ) as response:
            payload = bytearray()
            async for chunk in response.content.iter_chunked(16 * 1024):
                payload.extend(chunk)
                if len(payload) > MAX_RESPONSE_BYTES:
                    raise ResponseTooLarge
            public_headers = {
                key: response.headers[key]
                for key in ("Content-Type", "ETag", "Retry-After", "Cache-Control")
                if key in response.headers
            }
            return BackendResponse(response.status, bytes(payload), public_headers)
