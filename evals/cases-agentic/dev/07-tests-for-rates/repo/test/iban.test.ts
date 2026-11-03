import assert from "node:assert/strict";
import { test } from "node:test";
import { isValidIban } from "../src/iban.ts";

test("isValidIban accepts correct IBANs, with or without spaces and in any case", () => {
  assert.equal(isValidIban("DE89370400440532013000"), true);
  assert.equal(isValidIban("GB82 WEST 1234 5698 7654 32"), true);
  assert.equal(isValidIban("gb82west12345698765432"), true);
});

test("isValidIban rejects a wrong check digit", () => {
  assert.equal(isValidIban("DE88370400440532013000"), false);
});

test("isValidIban rejects text that is not shaped like an IBAN", () => {
  assert.equal(isValidIban(""), false);
  assert.equal(isValidIban("DE89"), false);
  assert.equal(isValidIban("1234567890123456"), false);
});
