import assert from "node:assert/strict";
import { test } from "node:test";
import { mergeContacts } from "../src/import.ts";
import type { Contact } from "../src/types.ts";

function countedContact(id: number, emailNumber: number, counter: { reads: number }): Contact {
  const contact = { id: `c${id}`, name: `Name ${id}`, phone: "", tags: [], updatedAt: id } as unknown as Contact;
  Object.defineProperty(contact, "email", {
    enumerable: true,
    get() {
      counter.reads++;
      return `user${emailNumber}@example.com`;
    },
  });
  return contact;
}

test("looks at each email a constant number of times, not once per other contact", () => {
  const size = 1500;
  const counter = { reads: 0 };
  // Every second incoming contact matches an existing one; the rest are new.
  const existing = Array.from({ length: size }, (_, i) => countedContact(i, i, counter));
  const incoming = Array.from({ length: size }, (_, i) => countedContact(size + i, i % 2 === 0 ? i : size + i, counter));
  const result = mergeContacts(existing, incoming);
  assert.equal(result.length, size + size / 2);
  assert.ok(counter.reads <= 10 * (existing.length + incoming.length), `${counter.reads} email reads for ${2 * size} contacts`);
});
