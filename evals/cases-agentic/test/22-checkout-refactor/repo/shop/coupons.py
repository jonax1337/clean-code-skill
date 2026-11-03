class CouponBook:
    """Percentage coupons with a limited number of redemptions."""

    def __init__(self, coupons: dict[str, tuple[int, int]]) -> None:
        self._percent = {code: percent for code, (percent, _) in coupons.items()}
        self._remaining = {code: uses for code, (_, uses) in coupons.items()}

    def discount_percent(self, code: str) -> int | None:
        if self._remaining.get(code, 0) <= 0:
            return None
        return self._percent[code]

    def redeem(self, code: str) -> None:
        self._remaining[code] -= 1
