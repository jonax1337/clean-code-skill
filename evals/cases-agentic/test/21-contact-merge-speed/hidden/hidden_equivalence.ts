import assert from "node:assert/strict";
import { test } from "node:test";
import { mergeContacts } from "../src/import.ts";
import { randomContacts, randomSource, referenceMergeContacts } from "./oracle.ts";

test("gives the same result as the original merge on random inputs with many duplicates", () => {
  for (let seed = 1; seed <= 40; seed++) {
    const random = randomSource(seed);
    // A small email pool makes duplicates inside both lists, and between them, very likely.
    const existing = randomContacts(random, 30, 25, "e");
    const incoming = randomContacts(random, 40, 25, "i");
    assert.deepEqual(mergeContacts(existing, incoming), referenceMergeContacts(existing, incoming), `seed ${seed}`);
  }
});

test("when the existing book already holds the same email twice, the first entry receives the merge", () => {
  const entry = (id: string, email: string) => ({ id, email, name: id, phone: "", tags: [], updatedAt: 1 });
  const existing = [entry("a", "dup@x.io"), entry("b", "other@x.io"), entry("c", "DUP@x.io")];
  const incoming = [{ ...entry("n", "dup@x.io"), phone: "999" }];
  const result = mergeContacts(existing, incoming);
  assert.deepEqual(result, referenceMergeContacts(existing, incoming));
  assert.equal(result[0].phone, "999");
  assert.equal(result[2].phone, "");
});

test("does not remember anything between calls, even for the same array", () => {
  const entry = (id: string, email: string) => ({ id, email, name: id, phone: "", tags: [], updatedAt: 1 });
  const existing = [entry("a", "a@x.io")];
  const incoming = [entry("b", "b@x.io")];
  assert.deepEqual(mergeContacts(existing, incoming), referenceMergeContacts(existing, incoming));
  existing.push(entry("c", "b@x.io"));
  incoming.push(entry("d", "c@x.io"));
  assert.deepEqual(mergeContacts(existing, incoming), referenceMergeContacts(existing, incoming));
  assert.deepEqual(mergeContacts([], []), []);
});
