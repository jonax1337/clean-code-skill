"""Order checkout: prices an order, reserves stock, charges the customer and sends the receipt."""

import logging
from decimal import ROUND_HALF_UP, Decimal

from shop.coupons import CouponBook
from shop.errors import OrderRejected, OutOfStock, PaymentDeclined
from shop.inventory import Inventory
from shop.models import Customer, Order
from shop.payments import PaymentGateway, ReceiptNotifier
from shop.pricing import tax_rate

logger = logging.getLogger(__name__)

SHIPPING_CENTS = 490
FREE_SHIPPING_FROM_CENTS = 5000
VIP_DISCOUNT_PERCENT = 5


def process_order(
    order: Order,
    customer: Customer,
    inventory: Inventory,
    gateway: PaymentGateway,
    notifier: ReceiptNotifier,
    coupons: CouponBook,
) -> str:
    """Checks out the order and returns the receipt id of the payment."""
    if not order.items:
        raise OrderRejected("order has no items")
    for item in order.items:
        if item.quantity <= 0:
            raise OrderRejected(f"invalid quantity for {item.sku}")

    # Tax is rounded per line, as the accounting export expects, and is charged on the undiscounted line price.
    rate = tax_rate(customer.country)
    subtotal = 0
    tax = 0
    for item in order.items:
        line_cents = item.unit_price_cents * item.quantity
        subtotal += line_cents
        tax += int((Decimal(line_cents) * rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    discount = 0
    if order.coupon is not None:
        percent = coupons.discount_percent(order.coupon)
        if percent is None:
            raise OrderRejected(f"invalid coupon: {order.coupon}")
        discount += subtotal * percent // 100
    if customer.vip:
        discount += (subtotal - discount) * VIP_DISCOUNT_PERCENT // 100
    shipping = 0 if subtotal - discount >= FREE_SHIPPING_FROM_CENTS else SHIPPING_CENTS
    total = subtotal - discount + tax + shipping

    reserved = []
    try:
        for item in order.items:
            inventory.reserve(item.sku, item.quantity)
            reserved.append(item)
    except OutOfStock as error:
        for item in reserved:
            inventory.release(item.sku, item.quantity)
        order.status = "rejected"
        raise OrderRejected(f"out of stock: {error.sku}") from error

    try:
        receipt_id = gateway.charge(customer.email, total)
    except PaymentDeclined as error:
        for item in reserved:
            inventory.release(item.sku, item.quantity)
        order.status = "payment_failed"
        raise OrderRejected(f"payment declined: {error}") from error

    for item in order.items:
        inventory.commit(item.sku, item.quantity)
    if order.coupon is not None:
        coupons.redeem(order.coupon)
    order.status = "paid"
    order.total_cents = total
    logger.info("order %s paid: %s cents", order.id, total)

    try:
        notifier.send_receipt(customer.email, order.id, receipt_id)
    except Exception:
        logger.warning("receipt for order %s could not be sent", order.id, exc_info=True)
    return receipt_id


def refund_order(order: Order, customer: Customer, inventory: Inventory, gateway: PaymentGateway) -> None:
    """Refunds a paid order in full and puts its items back into stock."""
    if order.status != "paid":
        raise OrderRejected(f"order {order.id} is not paid")
    gateway.refund(customer.email, order.total_cents)
    for item in order.items:
        inventory.restock(item.sku, item.quantity)
    order.status = "refunded"
    logger.info("order %s refunded: %s cents", order.id, order.total_cents)
