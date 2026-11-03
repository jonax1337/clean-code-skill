import json
import time
from collections.abc import Callable
from datetime import date
from typing import Any

from shipsync.errors import ApiError, LabelNotReady, TransportError
from shipsync.models import Address, Shipment
from shipsync.transport import Request, Response, Transport

DEFAULT_BASE_URL = "https://api.carrier.example/v2"
LABEL_POLL_ATTEMPTS = 5
LABEL_POLL_INTERVAL_S = 2.0
IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"
MAX_ATTEMPTS = 4
RETRY_BASE_DELAY_S = 0.5
TRANSIENT_STATUSES = frozenset({502, 503, 504})


class ShippingClient:
    def __init__(
        self,
        transport: Transport,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        *,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._transport = transport
        self._api_key = api_key
        self._base_url = base_url
        self._sleep = sleep

    def get_shipment(self, shipment_id: str) -> Shipment:
        response = self._request("GET", f"/shipments/{shipment_id}")
        return Shipment.from_payload(response.json())

    def list_shipments(self, status: str) -> list[Shipment]:
        response = self._request("GET", f"/shipments?status={status}")
        return [Shipment.from_payload(item) for item in response.json()["shipments"]]

    def create_shipment(
        self, order_ref: str, address: Address, idempotency_key: str | None = None
    ) -> Shipment:
        headers = {IDEMPOTENCY_KEY_HEADER: idempotency_key} if idempotency_key else {}
        payload = {"order_ref": order_ref, "address": address.to_payload()}
        response = self._request("POST", "/shipments", payload, headers)
        return Shipment.from_payload(response.json())

    def request_pickup(self, pickup_date: date, shipment_ids: list[str]) -> str:
        payload = {"date": pickup_date.isoformat(), "shipment_ids": shipment_ids}
        response = self._request("POST", "/pickups", payload)
        return response.json()["id"]

    def wait_for_label(self, shipment_id: str) -> str:
        for _ in range(LABEL_POLL_ATTEMPTS):
            response = self._request("GET", f"/shipments/{shipment_id}/label")
            if response.status == 200:
                return response.json()["url"]
            self._sleep(LABEL_POLL_INTERVAL_S)
        raise LabelNotReady(shipment_id)

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        request = Request(
            method,
            self._base_url + path,
            {"Authorization": f"Bearer {self._api_key}", **(headers or {})},
            json.dumps(payload).encode() if payload is not None else None,
        )
        max_attempts = MAX_ATTEMPTS if _is_safe_to_repeat(request) else 1
        for attempt in range(1, max_attempts):
            try:
                return self._send(request)
            except (TransportError, ApiError) as error:
                if not _is_transient(error):
                    raise
                self._sleep(RETRY_BASE_DELAY_S * 2 ** (attempt - 1))
        return self._send(request)

    def _send(self, request: Request) -> Response:
        response = self._transport.send(request)
        if response.status >= 400:
            raise ApiError(response.status, response.body.decode(errors="replace"))
        return response


def _is_safe_to_repeat(request: Request) -> bool:
    """Reads can be repeated freely; a POST only when the carrier deduplicates it by idempotency key."""
    return request.method == "GET" or IDEMPOTENCY_KEY_HEADER in request.headers


def _is_transient(error: TransportError | ApiError) -> bool:
    return isinstance(error, TransportError) or error.status in TRANSIENT_STATUSES
