from shop.money import format_eur
from shop.orders import Order, gross_total, net_total, vat_total


def receipt_lines(order: Order) -> list[str]:
    lines = [f"Bestellung {order.number}"]
    for item in order.items:
        lines.append(f"{item.quantity} x {item.name}  {format_eur(item.net())}")
    lines.append(f"Netto: {format_eur(net_total(order))}")
    lines.append(f"MwSt: {format_eur(vat_total(order))}")
    if order.shipping:
        lines.append(f"Versand: {format_eur(order.shipping)}")
    lines.append(f"Summe: {format_eur(gross_total(order))}")
    return lines
