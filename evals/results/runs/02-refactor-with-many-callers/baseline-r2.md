```ts
interface Priceable {
  price: number;
  category?: string;
}

const MEMBER_DISCOUNT_BOOKS = 0.9;
const MEMBER_DISCOUNT_DEFAULT = 0.95;
const SAVE10_AMOUNT = 10;

function applyMemberDiscount(price: number, category?: string): number {
  const multiplier = category === "books" ? MEMBER_DISCOUNT_BOOKS : MEMBER_DISCOUNT_DEFAULT;
  return price * multiplier;
}

function applyCoupon(price: number, coupon?: string): number {
  if (coupon === "SAVE10") {
    return Math.max(0, price - SAVE10_AMOUNT);
  }
  return price;
}

function roundToCents(value: number): number {
  return Math.round(value * 100) / 100;
}

export function getPrice(p: Priceable, isMember: boolean, coupon?: string): number {
  let price = p.price;
  if (isMember) price = applyMemberDiscount(price, p.category);
  price = applyCoupon(price, coupon);
  return roundToCents(price);
}
```

**What changed**
- The duplicated `isMember` branches are collapsed into one multiplier choice, and the magic numbers are named constants.
- The nested coupon `if`s and the manual clamp become `applyCoupon` with `Math.max(0, ...)`.
- Each step is a small helper, so adding coupons or categories later is easy.

**Behavior preserved**
- The 0 clamp still applies only when `SAVE10` is used. Without a coupon, a negative price stays negative, as before.
- Rounding is identical, and the order of operations is the same: member discount, then coupon, then round.

**Things to check given the 40 callers**
- I replaced `p: any` with a minimal `Priceable` type. It's compile-time only, but any caller passing an object without a numeric `price` will now get a type error. If that's a problem, change it back to `any` for now and tighten it later.
- `==` became `===`. This differs only if `category` or `coupon` is a non-string that loosely equals the string (e.g. `["books"]`). That is unlikely, but it's the one theoretical runtime difference.