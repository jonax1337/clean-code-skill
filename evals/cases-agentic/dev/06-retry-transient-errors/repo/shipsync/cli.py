import argparse
import json
import os
from datetime import date
from pathlib import Path

from shipsync.client import ShippingClient
from shipsync.models import Address, Order
from shipsync.sync import sync_shipments
from shipsync.transport import UrllibTransport


def load_orders(path: Path) -> list[Order]:
    entries = json.loads(path.read_text(encoding="utf-8"))
    return [Order(entry["reference"], Address(**entry["address"])) for entry in entries]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Book carrier shipments for the day's orders.")
    parser.add_argument("orders", type=Path, help="JSON file with the orders to ship")
    args = parser.parse_args(argv)

    client = ShippingClient(UrllibTransport(), os.environ["SHIPSYNC_API_KEY"])
    report = sync_shipments(client, load_orders(args.orders), date.today())

    print(f"created {len(report.created)} shipments, rejected {len(report.rejected)}")
    for reference, status in sorted(report.rejected.items()):
        print(f"  rejected {reference}: HTTP {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
