```ts
interface Priceable {
  price: number;
  category?: string;
}

const MEMBER_DISCOUNT_BOOKS = 0.9;
const MEMBER_DISCOUNT_DEFAULT = 0.95;
const SAVE10_AMOUNT = 10;

function memberMultiplier(category: string | undefined): number {
  return category === "books" ? MEMBER_DISCOUNT_BOOKS : MEMBER_DISCOUNT_DEFAULT;
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
  const memberPrice = isMember ? p.price * memberMultiplier(p.category) : p.price;
  return roundToCents(applyCoupon(memberPrice, coupon));
}
```

**What changed**
- The nested `if`s are now small helpers with named constants, and `getPrice` reads as three steps: member discount, coupon, rounding.
- `==` became `===`, and the redundant `if (coupon)` wrapper is gone, since `coupon === "SAVE10"` already implies it's truthy.
- The `if (price < 0) price = 0` clamp became `Math.max(0, ...)`.

**Behavior I deliberately preserved**
- The zero clamp applies only when the coupon is applied, so a negative `p.price` with no coupon still comes back negative, as before.
- Only `"SAVE10"` is recognized, and unknown coupons are ignored.
- Rounding is still `Math.round(x * 100) / 100`, applied last.
- The function name, export, and parameter order are unchanged, so the ~40 call sites don't need edits.

**One thing to check**
I replaced `p: any` with a `Priceable` interface. Callers that pass `any` are unaffected, but typed callers whose objects lack a numeric `price` (for example, a string price) will now fail to compile. That's likely a real bug being surfaced, but if you want zero risk, change the parameter back to `p: any`, or run `tsc` first and see what breaks. With `any`, a string `price` such as `"20"` is coerced by JS arithmetic, and the typed version no longer promises that.