```ts
const BOOK_CATEGORY = "books";
const BOOK_MEMBER_RATE = 0.9;
const DEFAULT_MEMBER_RATE = 0.95;
const SAVE10_COUPON = "SAVE10";
const SAVE10_AMOUNT = 10;

interface Priceable {
  price: number;
  category?: string;
}

export function getPrice(product: Priceable, isMember: boolean, coupon?: string): number {
  const memberPrice = isMember ? applyMemberDiscount(product) : product.price;
  const finalPrice = coupon === SAVE10_COUPON ? applySave10Coupon(memberPrice) : memberPrice;
  return roundToCents(finalPrice);
}

function applyMemberDiscount(product: Priceable): number {
  const rate = product.category === BOOK_CATEGORY ? BOOK_MEMBER_RATE : DEFAULT_MEMBER_RATE;
  return product.price * rate;
}

function applySave10Coupon(price: number): number {
  return Math.max(0, price - SAVE10_AMOUNT);
}

function roundToCents(amount: number): number {
  return Math.round(amount * 100) / 100;
}
```

**What changed**
- `getPrice` now reads as a top-down narrative: member discount, then coupon, then rounding. The details sit in small helpers below it (stepdown rule).
- The nested `if`s are replaced by named helpers, and the magic numbers and strings by named constants.
- `p` is now `product`, and the parameter has a type instead of `any`.
- The export name, parameter order and return type are unchanged, so the 40 call sites don't need edits.

**Behavior I deliberately preserved**
- The same multiplication happens in the same order (`price * rate`), so floating-point results are identical.
- The clamp to 0 applies only when `SAVE10` is used. Without a coupon, a negative input price is still returned as-is.
- Unknown coupons are still silently ignored. Changing that to an error would be a behavior change, so I left it out of scope.
- An empty-string coupon still does nothing.

**Things to check**
- **The `Priceable` type is the one real risk.** It is stricter than `any`, so a call site that passes something without a numeric `price` will now fail to compile. That is arguably a good catch, but if it creates noise across the 40 callers, temporarily loosen the parameter back to `any` and tighten it in a separate change.
- **`==` became `===`.** This is identical for string primitives. It would differ only if a caller passed a `String` object as `category`, which is very unlikely.
- **I haven't run anything.** Before merging, add characterization tests that pin the current outputs. For example, cover books vs. non-books, member vs. non-member, `SAVE10` driving the price below zero, an unknown coupon, and a rounding case like `19.995`.