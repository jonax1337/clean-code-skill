from datetime import date

import pytest
from hidden_support import (
    ADDRESS,
    MAX_REASONABLE_ATTEMPTS,
    ScriptedTransport,
    causal_chain,
    make_client,
    reply,
)

from shipsync.errors import ApiError, ConnectionFailed, RequestTimeout
from shipsync.models import Order
from shipsync.sync import sync_shipments


class FreshFailures(ScriptedTransport):
    """Raises a new exception of the given type on every request and remembers them."""

    def __init__(self, error_type: type[Exception]) -> None:
        super().__init__(reply(200))
        self._error_type = error_type
        self.raised: list[Exception] = []

    def send(self, request):
        self.requests.append(request)
        self.raised.append(self._error_type(f"failure {len(self.requests)}"))
        raise self.raised[-1]


@pytest.mark.parametrize("error_type", [RequestTimeout, ConnectionFailed])
def test_a_network_failure_that_never_clears_is_raised_after_a_bounded_number_of_attempts(error_type):
    transport = FreshFailures(error_type)
    client, _ = make_client(transport)

    with pytest.raises(Exception) as raised:
        client.get_shipment("sh-1")

    assert 2 <= len(transport.requests) <= MAX_REASONABLE_ATTEMPTS
    assert any(error in transport.raised for error in causal_chain(raised.value)), (
        f"{raised.value!r} is not one of the transport errors and was not raised from one"
    )


def test_a_gateway_error_that_never_clears_is_raised_after_a_bounded_number_of_attempts():
    transport = ScriptedTransport(reply(503, {"error": "unavailable"}))
    client, _ = make_client(transport)

    with pytest.raises(Exception) as raised:
        client.get_shipment("sh-1")

    assert 2 <= len(transport.requests) <= MAX_REASONABLE_ATTEMPTS
    assert any(isinstance(error, ApiError) and error.status == 503 for error in causal_chain(raised.value)), (
        f"{raised.value!r} lost the 503"
    )


def test_the_sync_job_fails_loudly_when_the_carrier_stays_down():
    transport = ScriptedTransport(reply(503, {"error": "unavailable"}))
    client, _ = make_client(transport)

    with pytest.raises(Exception) as raised:
        sync_shipments(client, [Order("A-1", ADDRESS)], date(2026, 3, 2))

    assert any(isinstance(error, ApiError) and error.status == 503 for error in causal_chain(raised.value))
