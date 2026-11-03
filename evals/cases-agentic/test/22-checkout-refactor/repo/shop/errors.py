class OutOfStock(Exception):
    def __init__(self, sku: str) -> None:
        super().__init__(sku)
        self.sku = sku


class PaymentDeclined(Exception):
    pass


class OrderRejected(Exception):
    pass
