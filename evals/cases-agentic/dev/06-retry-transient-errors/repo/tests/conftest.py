from collections.abc import Callable

import pytest

from shipsync.client import ShippingClient
from tests.fakes import FakeTransport


@pytest.fixture
def sleeps() -> list[float]:
    return []


@pytest.fixture
def make_client(sleeps: list[float]) -> Callable[[FakeTransport], ShippingClient]:
    def build(transport: FakeTransport) -> ShippingClient:
        return ShippingClient(transport, api_key="test-key", sleep=sleeps.append)

    return build
