from datetime import date

import pytest
from hidden_support import ADDRESS, Carrier, ScriptedTransport, causal_chain, make_client, reply, shipment_json

from shipsync.errors import RequestTimeout
from shipsync.models import Order
from shipsync.sync import sync_shipments


def test_a_create_without_a_key_is_not_repeated_after_a_timeout():
    timeout = RequestTimeout("timed out")
    transport = ScriptedTransport(timeout, reply(201, shipment_json()))
    client, _ = make_client(transport)

    with pytest.raises(Exception) as raised:
        client.create_shipment("A-1001", ADDRESS)

    assert len(transport.requests) == 1
    assert timeout in causal_chain(raised.value)


def test_a_pickup_is_not_repeated_after_a_timeout():
    timeout = RequestTimeout("timed out")
    transport = ScriptedTransport(timeout, reply(201, {"id": "pk-1"}))
    client, _ = make_client(transport)

    with pytest.raises(Exception) as raised:
        client.request_pickup(date(2026, 3, 2), ["sh-1"])

    assert len(transport.requests) == 1
    assert timeout in causal_chain(raised.value)


def test_a_pickup_whose_response_was_lost_is_booked_exactly_once():
    carrier = Carrier({("POST", "/v2/pickups", 1): "lost_response"})
    client, _ = make_client(carrier)

    with pytest.raises(Exception):
        sync_shipments(client, [Order("A-1", ADDRESS)], date(2026, 3, 2))

    assert len(carrier.pickups) == 1
