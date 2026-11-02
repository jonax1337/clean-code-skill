```ts
const BOOK_MEMBER_MULTIPLIER = 0.9;
const DEFAULT_MEMBER_MULTIPLIER = 0.95;
const SAVE10_COUPON = "SAVE10";
const SAVE10_DISCOUNT = 10;

function memberMultiplier(category: string): number {
  return category === "books" ? BOOK_MEMBER_MULTIPLIER : DEFAULT_MEMBER_MULTIPLIER;
}

function roundToCents(amount: number): number {
  return Math.round(amount * 100) / 100;
}

export function getPrice(p: any, isMember: boolean, coupon?: string) {
  let price = p.price;

  if (isMember) {
    price *= memberMultiplier(p.category);
  }

  if (coupon === SAVE10_COUPON) {
    price = Math.max(0, price - SAVE10_DISCOUNT);
  }

  return roundToCents(price);
}
```

**What changed**
- The duplicated `isMember` branches are collapsed into one check, with the category-specific rate pulled into `memberMultiplier`.
- The nested `if (coupon) { if (coupon == "SAVE10") ... }` became a single check. An empty or undefined coupon never equals `"SAVE10"`, so the outer truthiness check was redundant.
- The manual `if (price < 0) price = 0` became `Math.max(0, ...)`. The floor still applies only after the coupon, so a negative `p.price` with no coupon passes through unchanged, as before. `NaN` also behaves the same.
- The magic numbers and strings are now named constants.

**Things I deliberately left alone**
- The signature, including `p: any`, is unchanged so none of the ~40 callers can break. Tightening it later to something like `{ price: number; category?: string }` would be a good follow-up, but it could surface type errors at call sites.
- `==` became `===`. For string categories this is identical. It would differ only if `category` were a non-primitive such as a `String` object, which is very unlikely.