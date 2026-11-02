```ts
const MEMBER_DISCOUNT_RATE_BOOKS = 0.10;
const MEMBER_DISCOUNT_RATE_DEFAULT = 0.05;
const SAVE10_COUPON_CODE = "SAVE10";
const SAVE10_AMOUNT_OFF = 10;

export function getPrice(product: any, isMember: boolean, coupon?: string) {
  let price = product.price;

  if (isMember) {
    price = applyMemberDiscount(price, product.category);
  }
  if (coupon === SAVE10_COUPON_CODE) {
    price = applySave10Coupon(price);
  }

  return roundToCents(price);
}

function applyMemberDiscount(price: number, category: string): number {
  const multiplier = category === "books" ? 0.9 : 0.95;
  return price * multiplier;
}

function applySave10Coupon(price: number): number {
  return Math.max(0, price - SAVE10_AMOUNT_OFF);
}

function roundToCents(amount: number): number {
  return Math.round(amount * 100) / 100;
}
```

I left two unused constants in that draft, so here is the tidied version without them:

```ts
const SAVE10_COUPON_CODE = "SAVE10";
const SAVE10_AMOUNT_OFF = 10;
const BOOKS_MEMBER_MULTIPLIER = 0.9;
const DEFAULT_MEMBER_MULTIPLIER = 0.95;

export function getPrice(product: any, isMember: boolean, coupon?: string) {
  let price = product.price;

  if (isMember) {
    price *= memberMultiplierFor(product.category);
  }
  if (coupon === SAVE10_COUPON_CODE) {
    price = Math.max(0, price - SAVE10_AMOUNT_OFF);
  }

  return roundToCents(price);
}

function memberMultiplierFor(category: string): number {
  return category === "books"
    ? BOOKS_MEMBER_MULTIPLIER
    : DEFAULT_MEMBER_MULTIPLIER;
}

function roundToCents(amount: number): number {
  return Math.round(amount * 100) / 100;
}
```

**What changed**
- **Nested ifs removed.** The duplicated `isMember` branches became a single check plus a `memberMultiplierFor` helper.
- **Magic numbers named.** The multipliers, coupon code, and coupon amount are now constants.
- **One level of abstraction.** `getPrice` reads as: member discount, coupon, round. The details live in small helpers.
- **Coupon check simplified.** `if (coupon) { if (coupon == "SAVE10") ...}` is equivalent to `coupon === "SAVE10"`. The `Math.max(0, …)` floor matches the old `if (price < 0) price = 0`, and it is still applied only when the coupon is used.

**Preserved on purpose**
- The export name, parameter order, and return type are unchanged, so the ~40 call sites are unaffected.
- I kept `product: any`. Tightening it to something like `{ price: number; category?: string }` would be a good follow-up, but it could cause compile errors at call sites I can't see, so I left it out of a behavior-preserving change.
- The parameter `p` is now `product`. This is only a rename, since TypeScript callers don't depend on parameter names.

**One subtle difference**
- I changed `==` to `===`. For string values the result is identical. It would differ only if `category` were a non-string that loosely equals `"books"`, such as `["books"]` or a `String` object. That's very unlikely, but if any caller might do it, switch back to `==`.

**Verification**
I couldn't run anything here. Before merging, add characterization tests that pin the current outputs:
- member and non-member prices, for books and for other categories
- `SAVE10` on a price below 10, which floors at 0
- an unknown coupon, which has no effect
- rounding cases such as `19.999`

Run them against the old implementation first, then against the new one.