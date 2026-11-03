from shop.errors import OutOfStock


class Inventory:
    def __init__(self, stock: dict[str, int]) -> None:
        self._stock = dict(stock)
        self._reserved: dict[str, int] = {}
        self.log: list[tuple[str, str, int]] = []

    def available(self, sku: str) -> int:
        return self._stock.get(sku, 0) - self._reserved.get(sku, 0)

    def reserve(self, sku: str, quantity: int) -> None:
        if self.available(sku) < quantity:
            raise OutOfStock(sku)
        self._reserved[sku] = self._reserved.get(sku, 0) + quantity
        self.log.append(("reserve", sku, quantity))

    def release(self, sku: str, quantity: int) -> None:
        self._reserved[sku] = self._reserved.get(sku, 0) - quantity
        self.log.append(("release", sku, quantity))

    def commit(self, sku: str, quantity: int) -> None:
        self._reserved[sku] = self._reserved.get(sku, 0) - quantity
        self._stock[sku] = self._stock.get(sku, 0) - quantity
        self.log.append(("commit", sku, quantity))

    def restock(self, sku: str, quantity: int) -> None:
        self._stock[sku] = self._stock.get(sku, 0) + quantity
        self.log.append(("restock", sku, quantity))
