# Order confirmation emails. Sent by the worker in jobs/send_mail.py.

from shop.money import format_eur
from shop.orders import Order, gross_total

SENDER = "shop@example.com"


def subject(o):
    return "Ihre Bestellung " + o.number + " ist eingegangen"


def confirmation_body(o: Order) -> str:
    s = "Hallo " + o.customer_name + ",\n\n"
    s += "vielen Dank für Ihre Bestellung " + o.number + ".\n\n"
    s += "Sie haben bestellt:\n"
    for it in o.items:
        s += "  " + str(it.quantity) + " x " + it.name + "\n"
    s += "Gesamtbetrag: " + format_eur(gross_total(o)) + "\n"
    s += "\n"
    s += "Wir melden uns, sobald Ihre Bestellung versandt wurde.\n\n"
    s += "Viele Grüße\nIhr Shop-Team\n"
    return s


def is_sendable(o):
    if o.customer_email == None or o.customer_email == "":
        return False
    if not "@" in o.customer_email:
        return False
    return True
