I couldn't run anything here, so nothing below has been executed. Because the function has about 40 callers, I pinned its behavior with tests first and then refactored.

## Step 1: Characterization tests (write and pass these *before* touching the code)

```ts
// pricing.test.ts  (Jest/Vitest-style globals; adjust the import if needed)
import { getPrice } from "./pricing";

describe("getPrice", () => {
  const book = { price: 20, category: "books" };
  const toy = { price: 20, category: "toys" };

  it("charges full price to non-members", () => {
    expect(getPrice(book, false)).toBe(20);
    expect(getPrice(toy, false)).toBe(20);
  });

  it("gives members 10% off books", () => {
    expect(getPrice(book, true)).toBe(18);
  });

  it("gives members 5% off everything else", () => {
    expect(getPrice(toy, true)).toBe(19);
  });

  it("treats a missing category as non-book", () => {
    expect(getPrice({ price: 20 }, true)).toBe(19);
  });

  it("applies SAVE10 after the member discount", () => {
    expect(getPrice(book, true, "SAVE10")).toBe(8);
    expect(getPrice(toy, false, "SAVE10")).toBe(10);
  });

  it("clamps to 0 when SAVE10 would go negative", () => {
    expect(getPrice({ price: 5 }, false, "SAVE10")).toBe(0);
  });

  it("ignores unknown or empty coupons", () => {
    expect(getPrice(toy, false, "BOGUS")).toBe(20);
    expect(getPrice(toy, false, "")).toBe(20);
    expect(getPrice(toy, false, "save10")).toBe(20);
  });

  it("only clamps when a coupon is applied", () => {
    expect(getPrice({ price: -5 }, false)).toBe(-5);
  });

  it("rounds to two decimals", () => {
    expect(getPrice({ price: 19.99, category: "books" }, true)).toBe(17.99);
    expect(getPrice({ price: 9.99 }, true)).toBe(9.49);
  });
});
```

## Step 2: The refactor

```ts
// pricing.ts
interface Priceable {
  price: number;
  category?: string;
}

const MEMBER_DISCOUNT_BY_CATEGORY: Record<string, number> = {
  books: 0.10,
};
const DEFAULT_MEMBER_DISCOUNT = 0.05;

const SAVE10_AMOUNT = 10;

function applyMemberDiscount(price: number, category?: string): number {
  const rate = category === "books" ? 0.9 : 0.95;
  return price * rate;
}

function applyCoupon(price: number, coupon?: string): number {
  return coupon === "SAVE10" ? Math.max(0, price - SAVE10_AMOUNT) : price;
}

function roundToCents(amount: number): number {
  return Math.round(amount * 100) / 100;
}

export function getPrice(p: Priceable, isMember: boolean, coupon?: string): number {
  const memberPrice = isMember ? applyMemberDiscount(p.price, p.category) : p.price;
  return roundToCents(applyCoupon(memberPrice, coupon));
}
```

Delete the two unused `MEMBER_DISCOUNT_*` constants above. I left them in by mistake, and they'd be dead code. Here is the clean version:

```ts
// pricing.ts
interface Priceable {
  price: number;
  category?: string;
}

const BOOK_MEMBER_MULTIPLIER = 0.9;
const DEFAULT_MEMBER_MULTIPLIER = 0.95;
const SAVE10_AMOUNT = 10;

function applyMemberDiscount(price: number, category?: string): number {
  const multiplier = category === "books" ? BOOK_MEMBER_MULTIPLIER : DEFAULT_MEMBER_MULTIPLIER;
  return price * multiplier;
}

function applyCoupon(price: number, coupon?: string): number {
  return coupon === "SAVE10" ? Math.max(0, price - SAVE10_AMOUNT) : price;
}

function roundToCents(amount: number): number {
  return Math.round(amount * 100) / 100;
}

export function getPrice(p: Priceable, isMember: boolean, coupon?: string): number {
  const memberPrice = isMember ? applyMemberDiscount(p.price, p.category) : p.price;
  return roundToCents(applyCoupon(memberPrice, coupon));
}
```

## Why behavior is unchanged
- **Same multipliers:** I kept `0.9` and `0.95` as multipliers rather than rewriting them as `1 - rate`, because that could change floating-point results.
- **Same coupon logic:** `if (coupon) { if (coupon == "SAVE10") … }` is equivalent to `coupon === "SAVE10"`. An empty or undefined coupon never matches.
- **Same clamp:** `Math.max(0, price - 10)` matches `if (price < 0) price = 0`. It still applies only when the coupon applies, so a negative base price without a coupon stays negative, and the tests pin that.
- **Same rounding and signature:** the argument order and the exported name are unchanged.

## Risks to check
- **`any` is now a type:** `p: any` became `Priceable`. If the compiler flags any of the 40 call sites, such as object literals with extra fields or a `price` that isn't a `number`, fix the type at the caller. Don't loosen it back to `any`. If you want zero compile-time risk in this change, keep `p: any` for now and tighten it in a separate commit.
- **`==` became `===`:** this only differs if someone passes a non-string `category`, such as a `String` object. That's unlikely, but a quick grep of the callers would confirm.

## Log
1. Read the function and listed its behaviors, including the edge cases (clamp only with a coupon, missing category, and the empty-string coupon).
2. Wrote characterization tests first, so the refactor has a safety net. Run them against the *old* code and confirm they pass.
3. Split the function into three pure steps (member discount, coupon, rounding) and named the magic numbers.
4. Replaced the nested `if`s with a ternary and `Math.max`, and the loose `==` with `===`.
5. Replaced `any` with a minimal `Priceable` interface.

I didn't run the crapper, dryer or mutator tools, and I haven't committed or pushed anything. They aren't available in this session, and the directory isn't a git repo. Once you've run the tests, I'd suggest committing the tests and the refactor as two separate commits.