import assert from "node:assert/strict";
import { test } from "node:test";

import { getPrice } from "../src/pricing.ts";

test("non-members pay the list price", () => {
  assert.equal(getPrice({ price: 19.99, category: "games" }, false), 19.99);
});

test("members get 10 % off books", () => {
  assert.equal(getPrice({ price: 40, category: "books" }, true), 36);
});

test("members get 5 % off everything else, rounded to cents", () => {
  assert.equal(getPrice({ price: 19.99, category: "games" }, true), 18.99);
  assert.equal(getPrice({ price: 33.33, category: "music" }, true), 31.66);
});

test("a missing category counts as 'everything else'", () => {
  assert.equal(getPrice({ price: 100 }, true), 95);
});

test("SAVE10 subtracts 10 after the member discount", () => {
  assert.equal(getPrice({ price: 20, category: "books" }, true, "SAVE10"), 8);
  assert.equal(getPrice({ price: 25, category: "games" }, false, "SAVE10"), 15);
});

test("SAVE10 never takes the price below 0", () => {
  assert.equal(getPrice({ price: 7, category: "games" }, false, "SAVE10"), 0);
});

test("unknown, lowercase and empty coupons are ignored", () => {
  assert.equal(getPrice({ price: 25, category: "games" }, false, "save10"), 25);
  assert.equal(getPrice({ price: 25, category: "games" }, false, "SAVE20"), 25);
  assert.equal(getPrice({ price: 25, category: "games" }, false, ""), 25);
});

test("without a coupon the price is not clamped", () => {
  assert.equal(getPrice({ price: -5, category: "games" }, false), -5);
});

test("results are rounded to cents", () => {
  assert.equal(getPrice({ price: 0.1 + 0.2, category: "games" }, false), 0.3);
});
