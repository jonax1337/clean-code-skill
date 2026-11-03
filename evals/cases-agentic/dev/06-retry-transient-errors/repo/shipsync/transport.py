import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Protocol

from shipsync.errors import ConnectionFailed, RequestTimeout


@dataclass(frozen=True)
class Request:
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes | None = None


@dataclass(frozen=True)
class Response:
    status: int
    body: bytes = b""

    def json(self) -> Any:
        return json.loads(self.body)


class Transport(Protocol):
    def send(self, request: Request) -> Response: ...


class UrllibTransport:
    def __init__(self, timeout_s: float = 10.0) -> None:
        self._timeout_s = timeout_s

    def send(self, request: Request) -> Response:
        http_request = urllib.request.Request(
            request.url, data=request.body, headers=request.headers, method=request.method
        )
        try:
            with urllib.request.urlopen(http_request, timeout=self._timeout_s) as reply:
                return Response(reply.status, reply.read())
        except urllib.error.HTTPError as error:
            return Response(error.code, error.read())
        except TimeoutError as error:
            raise RequestTimeout(str(error)) from error
        except urllib.error.URLError as error:
            if isinstance(error.reason, TimeoutError):
                raise RequestTimeout(str(error.reason)) from error
            raise ConnectionFailed(str(error.reason)) from error
        except ConnectionError as error:
            raise ConnectionFailed(str(error)) from error
