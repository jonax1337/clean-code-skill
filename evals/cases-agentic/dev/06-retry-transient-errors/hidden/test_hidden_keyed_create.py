from datetime import date

from hidden_support import ADDRESS, Carrier, ScriptedTransport, make_client, reply, shipment_json

from shipsync.errors import RequestTimeout
from shipsync.models import Order
from shipsync.sync import sync_shipments

TODAY = date(2026, 3, 2)
ORDERS = [Order("A-1", ADDRESS), Order("A-2", ADDRESS)]


def test_a_keyed_create_is_repeated_with_the_same_key_after_a_timeout():
    transport = ScriptedTransport(RequestTimeout("timed out"), reply(201, shipment_json()))
    client, _ = make_client(transport)

    shipment = client.create_shipment("A-1001", ADDRESS, idempotency_key="order-A-1001")

    assert shipment.id == "sh-1"
    first, second = transport.requests
    assert first.headers["Idempotency-Key"] == second.headers["Idempotency-Key"] == "order-A-1001"
    assert first.body == second.body


def test_a_lost_create_response_does_not_double_ship_the_order():
    carrier = Carrier({("POST", "/v2/shipments", 1): "lost_response"})
    client, _ = make_client(carrier)

    report = sync_shipments(client, ORDERS, TODAY)

    assert [shipment["order_ref"] for shipment in carrier.shipments] == ["A-1", "A-2"]
    assert report.created == ["sh-1", "sh-2"]
    assert [pickup["shipment_ids"] for pickup in carrier.pickups] == [["sh-1", "sh-2"]]


def test_a_gateway_error_on_a_create_is_survived():
    carrier = Carrier({("POST", "/v2/shipments", 2): "unavailable"})
    client, _ = make_client(carrier)

    report = sync_shipments(client, ORDERS, TODAY)

    assert report.created == ["sh-1", "sh-2"]
    assert len(carrier.shipments) == 2


def test_a_timeout_while_listing_open_shipments_is_survived():
    carrier = Carrier({("GET", "/v2/shipments", 1): "timeout_before"})
    client, _ = make_client(carrier)

    report = sync_shipments(client, ORDERS, TODAY)

    assert report.created == ["sh-1", "sh-2"]
