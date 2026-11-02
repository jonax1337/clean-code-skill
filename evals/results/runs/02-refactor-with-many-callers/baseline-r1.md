```ts
type Product = { price: number; category?: string };

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

export function getPrice(p: Product, isMember: boolean, coupon?: string): number {
  let price = p.price;
  if (isMember) price = applyMemberDiscount(price, p.category);
  price = applyCoupon(price, coupon);
  return roundToCents(price);
}
```

**What changed**
- The duplicated `isMember` branches are collapsed into one multiplier choice.
- The nested coupon `if`s are flattened, and the clamp to 0 uses `Math.max`.
- The magic numbers are named constants, and the rounding is its own helper.
- The function name, parameter order, and exported signature are unchanged.

**Behavior preserved on purpose**
- The coupon floor of 0 applies only when `SAVE10` is used. A negative `p.price` with no coupon is still returned as is.
- Member discount is applied before the coupon, and rounding happens last.
- Any other coupon string is ignored.
- NaN passes through the same way as before.

**Two things to check with ~40 callers**
1. I replaced `p: any` with a `Product` type. At runtime nothing changes, but if any caller passes an object whose type doesn't fit (for example, `price` typed as `string`), the compiler will now flag it. If you want zero type risk, keep `p: any` for now and tighten it later.
2. `==` became `===` for the category and coupon comparisons. That only differs if someone passes a non-string value, such as a `String` object. That's very unlikely, but a quick grep for non-literal callers would confirm it.