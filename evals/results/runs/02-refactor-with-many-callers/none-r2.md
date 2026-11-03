```ts
interface Priceable {
  price: number;
  category?: string;
}

const MEMBER_DISCOUNT_MULTIPLIER = {
  books: 0.9,
  default: 0.95,
} as const;

const SAVE10_COUPON = "SAVE10";
const SAVE10_AMOUNT = 10;

export function getPrice(p: Priceable, isMember: boolean, coupon?: string) {
  let price = p.price;

  if (isMember) {
    price *= p.category === "books"
      ? MEMBER_DISCOUNT_MULTIPLIER.books
      : MEMBER_DISCOUNT_MULTIPLIER.default;
  }

  if (coupon === SAVE10_COUPON) {
    price = Math.max(0, price - SAVE10_AMOUNT);
  }

  return Math.round(price * 100) / 100;
}
```

**What changed**
- The duplicated `isMember` branches are now a single check that picks the multiplier by category.
- The nested `if (coupon) { if (coupon == ...) }` is one strict comparison. An empty or undefined coupon never equals `"SAVE10"`, so the outcome is the same.
- The manual `if (price < 0) price = 0` is now `Math.max(0, ...)`. The floor still applies only after the coupon, as in the original. Member-only prices are not clamped, and `NaN` passes through the same way.
- The magic numbers are named constants. The order of operations (member discount, then coupon, then rounding) is unchanged.

**One thing to check:** I replaced `p: any` with a small `Priceable` type. At runtime nothing changes, but with about 40 call sites, the compiler may flag any caller that passes something without a numeric `price`, such as a string price. If that produces noise and you want a strictly zero-risk change, switch the parameter back to `p: any` and keep the rest as is.