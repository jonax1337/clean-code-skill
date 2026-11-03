import json
from datetime import date

import pytest

from shipsync.errors import ApiError
from shipsync.models import Address, Order
from shipsync.sync import sync_shipments
from tests.fakes import FakeTransport, reply, shipment_payload

TODAY = date(2026, 3, 2)
ADDRESS = Address("Ada Lovelace", "1 Analytical Way", "London", "N1 9GU", "GB")


def orders(*references: str) -> list[Order]:
    return [Order(reference, ADDRESS) for reference in references]


def test_creates_a_shipment_per_order_and_books_one_pickup(make_client):
    transport = FakeTransport(
        reply(200, {"shipments": []}),
        reply(201, shipment_payload("sh-1", "A-1")),
        reply(201, shipment_payload("sh-2", "A-2")),
        reply(201, {"id": "pk-1"}),
    )

    report = sync_shipments(make_client(transport), orders("A-1", "A-2"), TODAY)

    assert report.created == ["sh-1", "sh-2"]
    pickup = transport.requests[-1]
    assert pickup.url.endswith("/pickups")
    assert json.loads(pickup.body) == {"date": "2026-03-03", "shipment_ids": ["sh-1", "sh-2"]}


def test_creates_use_a_key_derived_from_the_order(make_client):
    transport = FakeTransport(
        reply(200, {"shipments": []}), reply(201, shipment_payload("sh-1", "A-1")), reply(201, {"id": "pk-1"})
    )

    sync_shipments(make_client(transport), orders("A-1"), TODAY)

    assert transport.requests[1].headers["Idempotency-Key"] == "order-A-1"


def test_orders_that_already_have_a_shipment_are_skipped(make_client):
    transport = FakeTransport(reply(200, {"shipments": [shipment_payload("sh-1", "A-1")]}))

    report = sync_shipments(make_client(transport), orders("A-1"), TODAY)

    assert report.created == []
    assert len(transport.requests) == 1


def test_rejected_orders_are_reported_and_the_rest_continue(make_client):
    transport = FakeTransport(
        reply(200, {"shipments": []}),
        reply(422, {"error": "bad postal code"}),
        reply(201, shipment_payload("sh-2", "A-2")),
        reply(201, {"id": "pk-1"}),
    )

    report = sync_shipments(make_client(transport), orders("A-1", "A-2"), TODAY)

    assert report.rejected == {"A-1": 422}
    assert report.created == ["sh-2"]


def test_server_errors_stop_the_job(make_client):
    transport = FakeTransport(reply(200, {"shipments": []}), reply(500, {"error": "boom"}))

    with pytest.raises(ApiError) as raised:
        sync_shipments(make_client(transport), orders("A-1"), TODAY)

    assert raised.value.status == 500
