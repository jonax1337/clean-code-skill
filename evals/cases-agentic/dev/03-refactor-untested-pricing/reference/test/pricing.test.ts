import assert from "node:assert/strict";
import { test } from "node:test";

import { getPrice } from "../src/pricing.ts";

test("members get 10 % off books and 5 % off the rest", () => {
  assert.equal(getPrice({ price: 40, category: "books" }, true), 36);
  assert.equal(getPrice({ price: 20, category: "games" }, true), 19);
});

test("SAVE10 applies after the member discount and never goes below 0", () => {
  assert.equal(getPrice({ price: 20, category: "books" }, true, "SAVE10"), 8);
  assert.equal(getPrice({ price: 7, category: "games" }, false, "SAVE10"), 0);
});

test("without a coupon a negative price stays negative", () => {
  assert.equal(getPrice({ price: -5, category: "games" }, false), -5);
});
