"""Order checkout: prices an order, reserves stock, charges the customer and sends the receipt."""

import logging
from decimal import ROUND_HALF_UP, Decimal

from shop.coupons import CouponBook
from shop.errors import OrderRejected, OutOfStock, PaymentDeclined
from shop.inventory import Inventory
from shop.models import Customer, Item, Order
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
    _validate_items(order)
    total = _total_cents(order, customer, coupons)
    _reserve_all(order, inventory)
    receipt_id = _charge(order, customer, gateway, inventory, total)
    _record_payment(order, inventory, coupons, total)
    _send_receipt(order, customer, notifier, receipt_id)
    return receipt_id


def _validate_items(order: Order) -> None:
    if not order.items:
        raise OrderRejected("order has no items")
    for item in order.items:
        if item.quantity <= 0:
            raise OrderRejected(f"invalid quantity for {item.sku}")


def _total_cents(order: Order, customer: Customer, coupons: CouponBook) -> int:
    subtotal = sum(item.unit_price_cents * item.quantity for item in order.items)
    discount = _discount_cents(order, customer, coupons, subtotal)
    shipping = 0 if subtotal - discount >= FREE_SHIPPING_FROM_CENTS else SHIPPING_CENTS
    return subtotal - discount + _tax_cents(order, customer) + shipping


def _tax_cents(order: Order, customer: Customer) -> int:
    """Tax is rounded per line, as the accounting export expects, and is charged on the undiscounted line price."""
    rate = tax_rate(customer.country)
    return sum(_line_tax_cents(item, rate) for item in order.items)


def _line_tax_cents(item: Item, rate: Decimal) -> int:
    line_cents = item.unit_price_cents * item.quantity
    return int((Decimal(line_cents) * rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _discount_cents(order: Order, customer: Customer, coupons: CouponBook, subtotal: int) -> int:
    discount = 0
    if order.coupon is not None:
        percent = coupons.discount_percent(order.coupon)
        if percent is None:
            raise OrderRejected(f"invalid coupon: {order.coupon}")
        discount += subtotal * percent // 100
    if customer.vip:
        discount += (subtotal - discount) * VIP_DISCOUNT_PERCENT // 100
    return discount


def _reserve_all(order: Order, inventory: Inventory) -> None:
    reserved: list[Item] = []
    try:
        for item in order.items:
            inventory.reserve(item.sku, item.quantity)
            reserved.append(item)
    except OutOfStock as error:
        _release(inventory, reserved)
        order.status = "rejected"
        raise OrderRejected(f"out of stock: {error.sku}") from error


def _release(inventory: Inventory, items: list[Item]) -> None:
    for item in items:
        inventory.release(item.sku, item.quantity)


def _charge(order: Order, customer: Customer, gateway: PaymentGateway, inventory: Inventory, total: int) -> str:
    try:
        return gateway.charge(customer.email, total)
    except PaymentDeclined as error:
        _release(inventory, order.items)
        order.status = "payment_failed"
        raise OrderRejected(f"payment declined: {error}") from error


def _record_payment(order: Order, inventory: Inventory, coupons: CouponBook, total: int) -> None:
    for item in order.items:
        inventory.commit(item.sku, item.quantity)
    if order.coupon is not None:
        coupons.redeem(order.coupon)
    order.status = "paid"
    order.total_cents = total
    logger.info("order %s paid: %s cents", order.id, total)


def _send_receipt(order: Order, customer: Customer, notifier: ReceiptNotifier, receipt_id: str) -> None:
    try:
        notifier.send_receipt(customer.email, order.id, receipt_id)
    except Exception:
        logger.warning("receipt for order %s could not be sent", order.id, exc_info=True)


def refund_order(order: Order, customer: Customer, inventory: Inventory, gateway: PaymentGateway) -> None:
    """Refunds a paid order in full and puts its items back into stock."""
    if order.status != "paid":
        raise OrderRejected(f"order {order.id} is not paid")
    gateway.refund(customer.email, order.total_cents)
    for item in order.items:
        inventory.restock(item.sku, item.quantity)
    order.status = "refunded"
    logger.info("order %s refunded: %s cents", order.id, order.total_cents)
