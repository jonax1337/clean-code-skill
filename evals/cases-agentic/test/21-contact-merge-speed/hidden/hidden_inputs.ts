import assert from "node:assert/strict";
import { test } from "node:test";
import { mergeContacts } from "../src/import.ts";
import type { Contact } from "../src/types.ts";
import { randomContacts, randomSource } from "./oracle.ts";

function deepFreeze<T>(value: T): T {
  if (typeof value === "object" && value !== null) {
    Object.values(value).forEach(deepFreeze);
    Object.freeze(value);
  }
  return value;
}

test("neither the arrays nor the contacts that were passed in are modified", () => {
  const random = randomSource(7);
  const existing = deepFreeze(randomContacts(random, 50, 30, "e"));
  const incoming = deepFreeze(randomContacts(random, 50, 30, "i"));
  const before = JSON.stringify([existing, incoming]);
  mergeContacts(existing, incoming);
  assert.equal(JSON.stringify([existing, incoming]), before);
});

test("the result is always a new array, even when there is nothing to import", () => {
  const existing: Contact[] = randomContacts(randomSource(3), 5, 5, "e");
  const result = mergeContacts(existing, []);
  assert.notEqual(result, existing);
  assert.deepEqual(result, existing);
  result.pop();
  assert.equal(existing.length, 5);
});
