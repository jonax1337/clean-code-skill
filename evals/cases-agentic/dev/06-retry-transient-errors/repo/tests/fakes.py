import json
from typing import Any

from shipsync.transport import Request, Response

MAX_REQUESTS = 50


class FakeTransport:
    """Answers requests from a script: each outcome is a Response, or an exception to raise.

    The last outcome repeats once the script is used up.
    """

    def __init__(self, *outcomes: Response | Exception) -> None:
        self._outcomes = list(outcomes)
        self.requests: list[Request] = []

    def send(self, request: Request) -> Response:
        self.requests.append(request)
        assert len(self.requests) <= MAX_REQUESTS, "the client keeps sending requests"
        outcome = self._outcomes.pop(0) if len(self._outcomes) > 1 else self._outcomes[0]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def reply(status: int, payload: Any = None) -> Response:
    return Response(status, json.dumps(payload).encode() if payload is not None else b"")


def shipment_payload(shipment_id: str = "sh-1", order_ref: str = "A-1001", status: str = "open") -> dict:
    return {"id": shipment_id, "order_ref": order_ref, "status": status, "tracking_number": None}
