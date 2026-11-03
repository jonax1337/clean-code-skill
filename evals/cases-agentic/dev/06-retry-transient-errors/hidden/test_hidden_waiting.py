import time

import pytest
from hidden_support import ScriptedTransport, make_client, reply

from shipsync.errors import RequestTimeout

MAX_TEST_SECONDS = 0.5
MAX_SINGLE_WAIT_S = 120


@pytest.fixture(autouse=True)
def no_real_waiting(monkeypatch):
    def refuse(seconds):
        raise AssertionError(f"slept {seconds}s for real instead of using the client's sleep")

    monkeypatch.setattr(time, "sleep", refuse)
    started = time.perf_counter()
    yield
    assert time.perf_counter() - started < MAX_TEST_SECONDS, "the test spent real time waiting"


@pytest.mark.parametrize("failure", [RequestTimeout("timed out"), reply(503)], ids=["timeout", "503"])
def test_waits_between_attempts_go_through_the_clients_sleep(failure):
    transport = ScriptedTransport(failure)
    client, sleeps = make_client(transport)

    with pytest.raises(Exception):
        client.get_shipment("sh-1")

    assert len(transport.requests) >= 2
    assert sleeps, "the client retried without ever waiting"
    assert all(0 <= seconds <= MAX_SINGLE_WAIT_S for seconds in sleeps)
