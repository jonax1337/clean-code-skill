import assert from "node:assert/strict";
import { test } from "node:test";
import { formatMinor } from "../src/format.ts";

test("formatMinor groups thousands and places the decimal point", () => {
  assert.equal(formatMinor(123456, 2), "1,234.56");
  assert.equal(formatMinor(100000000, 2), "1,000,000.00");
});

test("formatMinor pads amounts smaller than one unit", () => {
  assert.equal(formatMinor(5, 2), "0.05");
  assert.equal(formatMinor(7, 3), "0.007");
});

test("formatMinor leaves out the decimal point for currencies without minor units", () => {
  assert.equal(formatMinor(1500, 0), "1,500");
});

test("formatMinor keeps the sign in front", () => {
  assert.equal(formatMinor(-250, 2), "-2.50");
});
