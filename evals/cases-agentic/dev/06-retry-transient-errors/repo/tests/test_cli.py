import json

from shipsync.cli import load_orders


def test_load_orders_reads_references_and_addresses(tmp_path):
    address = {
        "name": "Ada Lovelace",
        "street": "1 Analytical Way",
        "city": "London",
        "postal_code": "N1 9GU",
        "country": "GB",
    }
    path = tmp_path / "orders.json"
    path.write_text(json.dumps([{"reference": "A-1", "address": address}]), encoding="utf-8")

    (order,) = load_orders(path)

    assert order.reference == "A-1"
    assert order.address.city == "London"
