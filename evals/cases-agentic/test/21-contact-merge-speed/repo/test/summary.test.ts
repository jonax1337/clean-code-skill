import assert from "node:assert/strict";
import { test } from "node:test";
import { summarize } from "../src/summary.ts";

test("summarize counts contacts, phones and tags", () => {
  const summary = summarize([
    { id: "1", email: "a@x.io", name: "A", phone: "1", tags: ["vip", "beta"], updatedAt: 1 },
    { id: "2", email: "b@x.io", name: "B", phone: "", tags: ["beta"], updatedAt: 1 },
  ]);
  assert.deepEqual(summary, { total: 2, withPhone: 1, tagCounts: { vip: 1, beta: 2 } });
});
