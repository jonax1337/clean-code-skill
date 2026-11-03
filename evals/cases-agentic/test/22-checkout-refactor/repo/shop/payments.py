from typing import Protocol


class PaymentGateway(Protocol):
    def charge(self, email: str, amount_cents: int) -> str:
        """Charges the customer and returns a receipt id; raises PaymentDeclined."""
        ...

    def refund(self, email: str, amount_cents: int) -> None: ...


class ReceiptNotifier(Protocol):
    def send_receipt(self, email: str, order_id: int, receipt_id: str) -> None: ...
