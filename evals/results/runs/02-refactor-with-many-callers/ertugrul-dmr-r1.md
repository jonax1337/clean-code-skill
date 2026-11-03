```ts
export interface PricedProduct {
  price: number;
  category?: string;
}

const BOOKS_CATEGORY = "books";
const BOOKS_MEMBER_MULTIPLIER = 0.9;
const DEFAULT_MEMBER_MULTIPLIER = 0.95;
const SAVE10_COUPON = "SAVE10";
const SAVE10_AMOUNT_OFF = 10;

export function getPrice(product: PricedProduct, isMember: boolean, coupon?: string): number {
  const memberPrice = isMember ? applyMemberDiscount(product) : product.price;
  const discountedPrice = applyCoupon(memberPrice, coupon);
  return roundToCents(discountedPrice);
}

function applyMemberDiscount(product: PricedProduct): number {
  const multiplier =
    product.category === BOOKS_CATEGORY ? BOOKS_MEMBER_MULTIPLIER : DEFAULT_MEMBER_MULTIPLIER;
  return product.price * multiplier;
}

function applyCoupon(price: number, coupon?: string): number {
  if (coupon !== SAVE10_COUPON) {
    return price;
  }
  return Math.max(0, price - SAVE10_AMOUNT_OFF);
}

function roundToCents(price: number): number {
  return Math.round(price * 100) / 100;
}
```

**What was fixed**
- G25: extracted the magic numbers and strings (`0.9`, `0.95`, `"books"`, `"SAVE10"`, `10`) into named constants.
- G5: the duplicated `if (isMember)` branches are now one multiplier choice.
- G30/G34: `getPrice` now reads as three steps (member discount, coupon, rounding), each in its own small function.
- G28/G29: the nested coupon `if`s became a guard clause. `Math.max(0, …)` replaces the manual clamp.
- TS3: `any` is replaced by a `PricedProduct` interface, and the return type is explicit.
- N1: `p` is now `product`.

**Behavior preserved**
- The exported name and the parameter order and arity are unchanged, so the ~40 call sites still work.
- The multiplication and rounding order is identical, so floating-point results match.
- An empty or undefined coupon still has no effect.
- The `NaN` edge case behaves the same: `NaN < 0` is false, and `Math.max(0, NaN)` is `NaN`.

**Things to check**
- **F3 (flag argument):** `isMember` is a boolean flag, and splitting the function would be the textbook fix. I left it because it would change the signature across 40 callers. If you want it, add `getMemberPrice` or similar as a new function and migrate callers gradually.
- **Type tightening:** `PricedProduct` is only a compile-time change. If any caller passes an `any` value, it still compiles. If a caller passes `price` as a string, the compiler will now flag it, and that was probably a latent bug.
- **`==` to `===`:** this differs only if `category` is a non-primitive such as `new String("books")`. That is very unlikely in practice.