import pytest
from hidden_support import ADDRESS, ScriptedTransport, make_client, reply, shipment_json

from shipsync.errors import ApiError


@pytest.mark.parametrize("status", [400, 401, 403, 404, 422])
def test_a_client_error_on_a_read_is_raised_after_one_request(status):
    transport = ScriptedTransport(reply(status, {"error": "no"}), reply(200, shipment_json()))
    client, _ = make_client(transport)

    with pytest.raises(ApiError) as raised:
        client.get_shipment("sh-1")

    assert raised.value.status == status
    assert len(transport.requests) == 1


@pytest.mark.parametrize("status", [400, 422])
def test_a_client_error_on_a_keyed_create_is_raised_after_one_request(status):
    transport = ScriptedTransport(reply(status, {"error": "bad address"}), reply(201, shipment_json()))
    client, _ = make_client(transport)

    with pytest.raises(ApiError) as raised:
        client.create_shipment("A-1001", ADDRESS, idempotency_key="order-A-1001")

    assert raised.value.status == status
    assert len(transport.requests) == 1


def test_an_unexpected_exception_from_the_transport_is_not_retried():
    transport = ScriptedTransport(ValueError("not a network problem"), reply(200, shipment_json()))
    client, _ = make_client(transport)

    with pytest.raises(ValueError, match="not a network problem"):
        client.get_shipment("sh-1")

    assert len(transport.requests) == 1
