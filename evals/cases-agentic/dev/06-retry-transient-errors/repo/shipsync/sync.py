from dataclasses import dataclass, field
from datetime import date, timedelta

from shipsync.client import ShippingClient
from shipsync.errors import ApiError
from shipsync.models import Order

PICKUP_LEAD_DAYS = 1


@dataclass
class SyncReport:
    created: list[str] = field(default_factory=list)
    rejected: dict[str, int] = field(default_factory=dict)


def sync_shipments(client: ShippingClient, orders: list[Order], today: date) -> SyncReport:
    """Create a shipment for every order that has none yet, then book one pickup for the new ones."""
    already_shipped = {shipment.order_ref for shipment in client.list_shipments("open")}
    report = SyncReport()
    for order in orders:
        if order.reference in already_shipped:
            continue
        try:
            shipment = client.create_shipment(
                order.reference, order.address, idempotency_key=f"order-{order.reference}"
            )
        except ApiError as error:
            if error.status >= 500:
                raise
            report.rejected[order.reference] = error.status
            continue
        report.created.append(shipment.id)
    if report.created:
        client.request_pickup(today + timedelta(days=PICKUP_LEAD_DAYS), report.created)
    return report
