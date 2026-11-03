import json
from collections.abc import Iterator
from urllib.parse import urlparse

from shipsync.client import ShippingClient
from shipsync.models import Address
from shipsync.transport import Request, Response

ADDRESS = Address("Ada Lovelace", "1 Analytical Way", "London", "N1 9GU", "GB")
MAX_REQUESTS = 25
MAX_REASONABLE_ATTEMPTS = 10


class RunawayRetries(BaseException):
    """Raised by the fakes when a client keeps sending requests; a BaseException so no `except Exception` hides it."""


def reply(status: int, payload: object = None) -> Response:
    return Response(status, json.dumps(payload).encode() if payload is not None else b"")


def shipment_json(shipment_id: str = "sh-1", order_ref: str = "A-1001") -> dict:
    return {"id": shipment_id, "order_ref": order_ref, "status": "open", "tracking_number": None}


class ScriptedTransport:
    """Plays outcomes in order (a Response, or an exception to raise); the last one repeats."""

    def __init__(self, *outcomes: Response | Exception) -> None:
        self._outcomes = list(outcomes)
        self.requests: list[Request] = []

    def send(self, request: Request) -> Response:
        self.requests.append(request)
        if len(self.requests) > MAX_REQUESTS:
            raise RunawayRetries(f"more than {MAX_REQUESTS} requests")
        outcome = self._outcomes.pop(0) if len(self._outcomes) > 1 else self._outcomes[0]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class Carrier:
    """A stateful stand-in for the carrier API, as documented in the README.

    `POST /shipments` creates a shipment, but a repeated Idempotency-Key returns the first one. `POST /pickups`
    books a new pickup every time. `glitches` maps (method, path, n) to what goes wrong on the n-th such request:
    "timeout_before" (nothing processed), "unavailable" (503, nothing processed) or "lost_response" (processed,
    but the caller sees a timeout).
    """

    def __init__(self, glitches: dict[tuple[str, str, int], str] | None = None) -> None:
        self._glitches = glitches or {}
        self._seen: dict[tuple[str, str], int] = {}
        self._by_key: dict[str, dict] = {}
        self.requests: list[Request] = []
        self.shipments: list[dict] = []
        self.pickups: list[dict] = []

    def send(self, request: Request) -> Response:
        from shipsync.errors import RequestTimeout

        self.requests.append(request)
        if len(self.requests) > MAX_REQUESTS:
            raise RunawayRetries(f"more than {MAX_REQUESTS} requests")
        path = urlparse(request.url).path
        occurrence = self._seen[(request.method, path)] = self._seen.get((request.method, path), 0) + 1
        glitch = self._glitches.get((request.method, path, occurrence))
        if glitch == "timeout_before":
            raise RequestTimeout("timed out before the carrier saw the request")
        if glitch == "unavailable":
            return reply(503, {"error": "try again later"})
        response = self._handle(request, path)
        if glitch == "lost_response":
            raise RequestTimeout("timed out waiting for the response")
        return response

    def _handle(self, request: Request, path: str) -> Response:
        body = json.loads(request.body) if request.body else {}
        if (request.method, path) == ("GET", "/v2/shipments"):
            return reply(200, {"shipments": self.shipments})
        if (request.method, path) == ("POST", "/v2/shipments"):
            return self._create_shipment(body, request.headers.get("Idempotency-Key"))
        if (request.method, path) == ("POST", "/v2/pickups"):
            self.pickups.append(body)
            return reply(201, {"id": f"pk-{len(self.pickups)}"})
        return reply(404, {"error": "unknown endpoint"})

    def _create_shipment(self, body: dict, key: str | None) -> Response:
        if key is not None and key in self._by_key:
            return reply(200, self._by_key[key])
        shipment = shipment_json(f"sh-{len(self.shipments) + 1}", body["order_ref"])
        self.shipments.append(shipment)
        if key is not None:
            self._by_key[key] = shipment
        return reply(201, shipment)


def make_client(transport: ScriptedTransport | Carrier) -> tuple[ShippingClient, list[float]]:
    """A client wired to the fake with a recording sleep; returns it with the list of requested waits."""
    sleeps: list[float] = []
    return ShippingClient(transport, api_key="test-key", sleep=sleeps.append), sleeps


def causal_chain(error: BaseException) -> Iterator[BaseException]:
    """The error and everything it was explicitly raised `from`."""
    current: BaseException | None = error
    while current is not None:
        yield current
        current = current.__cause__
