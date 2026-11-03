import assert from "node:assert/strict";
import { test } from "node:test";
import { mergeContacts } from "../src/import.ts";
import type { Contact } from "../src/types.ts";

function contact(id: string, email: string, overrides: Partial<Contact> = {}): Contact {
  return { id, email, name: `Name ${id}`, phone: "", tags: [], updatedAt: 1, ...overrides };
}

test("new contacts are appended in arrival order", () => {
  const result = mergeContacts([contact("1", "a@x.io")], [contact("2", "b@x.io"), contact("3", "c@x.io")]);
  assert.deepEqual(
    result.map((c) => c.id),
    ["1", "2", "3"],
  );
});

test("a contact with a known email is merged into the existing entry", () => {
  const result = mergeContacts([contact("1", "a@x.io", { tags: ["vip"] })], [contact("2", "a@x.io", { tags: ["beta"] })]);
  assert.equal(result.length, 1);
  assert.equal(result[0].id, "1");
  assert.deepEqual(result[0].tags, ["vip", "beta"]);
});

test("emails are compared without case and surrounding whitespace", () => {
  const result = mergeContacts([contact("1", "Ada@X.io")], [contact("2", " ada@x.IO ")]);
  assert.equal(result.length, 1);
});

test("duplicates inside the incoming list are merged with each other", () => {
  const result = mergeContacts([], [contact("1", "a@x.io", { phone: "111" }), contact("2", "a@x.io", { name: "" })]);
  assert.equal(result.length, 1);
  assert.equal(result[0].phone, "111");
});
