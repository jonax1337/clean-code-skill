import json
from datetime import date

import pytest

from shipsync.client import LABEL_POLL_ATTEMPTS, LABEL_POLL_INTERVAL_S, MAX_ATTEMPTS
from shipsync.errors import ApiError, ConnectionFailed, LabelNotReady, RequestTimeout
from shipsync.models import Address
from tests.fakes import FakeTransport, reply, shipment_payload

ADDRESS = Address("Ada Lovelace", "1 Analytical Way", "London", "N1 9GU", "GB")


def test_get_shipment_parses_the_payload(make_client):
    transport = FakeTransport(reply(200, shipment_payload("sh-7", "A-7", "in_transit")))

    shipment = make_client(transport).get_shipment("sh-7")

    assert (shipment.id, shipment.order_ref, shipment.status) == ("sh-7", "A-7", "in_transit")
    assert transport.requests[0].url.endswith("/shipments/sh-7")


def test_every_request_carries_the_api_key(make_client):
    transport = FakeTransport(reply(200, shipment_payload()))

    make_client(transport).get_shipment("sh-1")

    assert transport.requests[0].headers["Authorization"] == "Bearer test-key"


def test_list_shipments_filters_by_status(make_client):
    transport = FakeTransport(reply(200, {"shipments": [shipment_payload("sh-1"), shipment_payload("sh-2")]}))

    shipments = make_client(transport).list_shipments("open")

    assert [shipment.id for shipment in shipments] == ["sh-1", "sh-2"]
    assert transport.requests[0].url.endswith("/shipments?status=open")


def test_create_shipment_sends_the_idempotency_key(make_client):
    transport = FakeTransport(reply(201, shipment_payload()))

    make_client(transport).create_shipment("A-1001", ADDRESS, idempotency_key="order-A-1001")

    request = transport.requests[0]
    assert request.headers["Idempotency-Key"] == "order-A-1001"
    assert json.loads(request.body)["order_ref"] == "A-1001"


def test_create_shipment_without_a_key_sends_no_key_header(make_client):
    transport = FakeTransport(reply(201, shipment_payload()))

    make_client(transport).create_shipment("A-1001", ADDRESS)

    assert "Idempotency-Key" not in transport.requests[0].headers


def test_request_pickup_returns_the_pickup_id(make_client):
    transport = FakeTransport(reply(201, {"id": "pk-3"}))

    pickup_id = make_client(transport).request_pickup(date(2026, 3, 2), ["sh-1", "sh-2"])

    assert pickup_id == "pk-3"
    assert json.loads(transport.requests[0].body) == {"date": "2026-03-02", "shipment_ids": ["sh-1", "sh-2"]}


def test_wait_for_label_polls_until_the_label_is_ready(make_client, sleeps):
    transport = FakeTransport(reply(202), reply(202), reply(200, {"url": "https://labels.example/sh-1.pdf"}))

    url = make_client(transport).wait_for_label("sh-1")

    assert url == "https://labels.example/sh-1.pdf"
    assert sleeps == [LABEL_POLL_INTERVAL_S, LABEL_POLL_INTERVAL_S]


def test_wait_for_label_gives_up_when_the_label_never_arrives(make_client):
    transport = FakeTransport(reply(202))

    with pytest.raises(LabelNotReady):
        make_client(transport).wait_for_label("sh-1")

    assert len(transport.requests) == LABEL_POLL_ATTEMPTS


def test_error_status_raises_api_error_with_the_status(make_client):
    transport = FakeTransport(reply(404, {"error": "no such shipment"}))

    with pytest.raises(ApiError) as raised:
        make_client(transport).get_shipment("sh-404")

    assert raised.value.status == 404


@pytest.mark.parametrize(
    "failure", [RequestTimeout("slow"), ConnectionFailed("reset"), reply(502), reply(503)]
)
def test_reads_are_retried_after_a_transient_failure(make_client, sleeps, failure):
    transport = FakeTransport(failure, reply(200, shipment_payload()))

    shipment = make_client(transport).get_shipment("sh-1")

    assert shipment.id == "sh-1"
    assert len(transport.requests) == 2
    assert len(sleeps) == 1


def test_reads_give_up_after_the_attempt_limit_and_raise_the_last_error(make_client):
    timeout = RequestTimeout("slow")
    transport = FakeTransport(timeout)

    with pytest.raises(RequestTimeout) as raised:
        make_client(transport).get_shipment("sh-1")

    assert raised.value is timeout
    assert len(transport.requests) == MAX_ATTEMPTS


def test_gateway_errors_that_keep_coming_end_in_an_api_error(make_client):
    transport = FakeTransport(reply(503))

    with pytest.raises(ApiError) as raised:
        make_client(transport).get_shipment("sh-1")

    assert raised.value.status == 503
    assert len(transport.requests) == MAX_ATTEMPTS


@pytest.mark.parametrize("status", [400, 401, 404, 422])
def test_client_errors_are_not_retried(make_client, sleeps, status):
    transport = FakeTransport(reply(status))

    with pytest.raises(ApiError):
        make_client(transport).get_shipment("sh-1")

    assert len(transport.requests) == 1
    assert sleeps == []


def test_a_keyed_create_is_retried_with_the_same_key(make_client):
    transport = FakeTransport(RequestTimeout("slow"), reply(201, shipment_payload()))

    make_client(transport).create_shipment("A-1001", ADDRESS, idempotency_key="order-A-1001")

    first, second = transport.requests
    assert first.headers["Idempotency-Key"] == second.headers["Idempotency-Key"] == "order-A-1001"


def test_a_create_without_a_key_is_not_retried(make_client):
    transport = FakeTransport(RequestTimeout("slow"), reply(201, shipment_payload()))

    with pytest.raises(RequestTimeout):
        make_client(transport).create_shipment("A-1001", ADDRESS)

    assert len(transport.requests) == 1


def test_a_pickup_is_not_retried(make_client):
    transport = FakeTransport(RequestTimeout("slow"), reply(201, {"id": "pk-1"}))

    with pytest.raises(RequestTimeout):
        make_client(transport).request_pickup(date(2026, 3, 2), ["sh-1"])

    assert len(transport.requests) == 1
