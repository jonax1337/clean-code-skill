import pytest
from hidden_support import ScriptedTransport, make_client, reply, shipment_json

from shipsync.errors import ConnectionFailed, RequestTimeout

TRANSIENT_FAILURES = {
    "timeout": RequestTimeout("timed out"),
    "connection reset": ConnectionFailed("connection reset"),
    "502": reply(502, {"error": "bad gateway"}),
    "503": reply(503, {"error": "unavailable"}),
}
READS = {
    "get_shipment": (lambda client: client.get_shipment("sh-1").id, reply(200, shipment_json()), "sh-1"),
    "list_shipments": (
        lambda client: [s.id for s in client.list_shipments("open")],
        reply(200, {"shipments": [shipment_json()]}),
        ["sh-1"],
    ),
    "wait_for_label": (
        lambda client: client.wait_for_label("sh-1"),
        reply(200, {"url": "https://labels.example/sh-1.pdf"}),
        "https://labels.example/sh-1.pdf",
    ),
}


@pytest.mark.parametrize("failure", TRANSIENT_FAILURES.values(), ids=TRANSIENT_FAILURES.keys())
@pytest.mark.parametrize("read", READS.values(), ids=READS.keys())
def test_a_read_that_hits_a_transient_failure_is_repeated(read, failure):
    call, success, expected = read
    transport = ScriptedTransport(failure, success)
    client, _ = make_client(transport)

    assert call(client) == expected
    assert len(transport.requests) == 2
