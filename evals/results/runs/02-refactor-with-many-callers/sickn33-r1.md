Here is the refactor. The exported signature `getPrice(p: any, isMember: boolean, coupon?: string)` is unchanged, so the ~40 call sites don't need to change.

```ts
const BOOK_MEMBER_DISCOUNT_RATE = 0.9;
const DEFAULT_MEMBER_DISCOUNT_RATE = 0.95;
const SAVE10_COUPON_CODE = "SAVE10";
const SAVE10_AMOUNT_OFF = 10;

export function getPrice(p: any, isMember: boolean, coupon?: string) {
  const memberPrice = applyMemberDiscount(p.price, p.category, isMember);
  const finalPrice = applyCoupon(memberPrice, coupon);
  return roundToCents(finalPrice);
}

function applyMemberDiscount(price: number, category: string, isMember: boolean) {
  if (!isMember) return price;
  return price * memberDiscountRateFor(category);
}

function memberDiscountRateFor(category: string) {
  return category == "books"
    ? BOOK_MEMBER_DISCOUNT_RATE
    : DEFAULT_MEMBER_DISCOUNT_RATE;
}

function applyCoupon(price: number, coupon?: string) {
  if (coupon == SAVE10_COUPON_CODE) {
    return Math.max(0, price - SAVE10_AMOUNT_OFF);
  }
  return price;
}

function roundToCents(amount: number) {
  return Math.round(amount * 100) / 100;
}
```

**What changed**
- `getPrice` now reads as three steps: member discount, coupon, rounding. Each step is its own small function.
- The magic numbers and the coupon code are named constants.
- The nested `if`s are replaced with guard clauses and a ternary.
- The `if (price < 0) price = 0` clamp became `Math.max(0, …)`.

**Behavior I deliberately preserved**
- I kept `==` rather than `===`. Since `p` is `any`, `===` could in theory change results for odd inputs (e.g. a non-string category that coerces to `"books"`). If you know categories are always strings, switching to `===` is a safe follow-up.
- Non-members are not multiplied by anything, which matches the original.
- The clamp-at-zero applies only to the coupon step, not the member discount, as before.
- Rounding happens last, exactly as before.
- Unknown coupon codes are ignored. An empty or `undefined` coupon also changes nothing.

**Not done, on purpose**
- I left `p: any` alone. Typing it (e.g. `{ price: number; category: string }`) would be an improvement, but it could cause compile errors at some of the 40 callers, so it should be done as a separate step where you can see the compiler's complaints.
- I couldn't run anything here, so I haven't verified this against your tests. Before merging, I'd add characterization tests that pin the current outputs. Good cases are: books vs. non-books, member vs. non-member, `SAVE10` on a price under 10 (clamps to 0), an unknown coupon, and a price that needs rounding such as `19.99 * 0.95`. Run them against both the old and new versions.