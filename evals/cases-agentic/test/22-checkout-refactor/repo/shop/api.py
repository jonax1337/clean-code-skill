from shop.checkout import process_order
from shop.coupons import CouponBook
from shop.errors import OrderRejected
from shop.inventory import Inventory
from shop.models import Customer, Item, Order
from shop.payments import PaymentGateway, ReceiptNotifier


def handle_checkout(
    payload: dict,
    inventory: Inventory,
    gateway: PaymentGateway,
    notifier: ReceiptNotifier,
    coupons: CouponBook,
) -> dict:
    """Runs a checkout request and describes the outcome as a JSON-serializable dict."""
    customer = Customer(**payload["customer"])
    items = [Item(**raw) for raw in payload["items"]]
    order = Order(id=payload["order_id"], items=items, coupon=payload.get("coupon"))
    try:
        receipt_id = process_order(order, customer, inventory, gateway, notifier, coupons)
    except OrderRejected as error:
        return {"ok": False, "status": order.status, "error": str(error)}
    return {"ok": True, "status": order.status, "total_cents": order.total_cents, "receipt_id": receipt_id}
