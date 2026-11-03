import assert from "node:assert/strict";
import { test } from "node:test";
import { mergeContact } from "../src/merge.ts";

const base = { id: "1", email: "a@x.io", name: "Ada", phone: "", tags: ["vip"], updatedAt: 10 };

test("the incoming fields win unless they are empty", () => {
  const merged = mergeContact(base, { ...base, id: "2", name: "", phone: "555", tags: ["new"], updatedAt: 5 });
  assert.deepEqual(merged, { id: "1", email: "a@x.io", name: "Ada", phone: "555", tags: ["vip", "new"], updatedAt: 10 });
});
