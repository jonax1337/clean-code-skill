import assert from "node:assert/strict";
import { test } from "node:test";
import { serializeAuditEntry } from "../src/audit.ts";

test("a pause entry has the resume date, then the quoted reason", () => {
  const entry = serializeAuditEntry({
    type: "subscription_paused",
    subscriptionId: "sub_9",
    occurredAt: "2025-04-02T08:30:00Z",
    resumeOn: "2025-05-01",
    reason: "vacation",
  });
  assert.equal(entry, '2025-04-02T08:30:00Z sub_9 subscription_paused resumeOn=2025-05-01 reason="vacation"');
});

test("the reason of a pause entry is escaped like a cancellation reason", () => {
  const entry = serializeAuditEntry({
    type: "subscription_paused",
    subscriptionId: "sub_9",
    occurredAt: "2025-04-02T08:30:00Z",
    resumeOn: "2025-05-01",
    reason: 'back in "May"\nmaybe',
  });
  assert.equal(
    entry,
    '2025-04-02T08:30:00Z sub_9 subscription_paused resumeOn=2025-05-01 reason="back in \\"May\\"\\nmaybe"',
  );
});

test("entries of the other events keep their format", () => {
  assert.equal(
    serializeAuditEntry({
      type: "subscription_canceled",
      subscriptionId: "sub_9",
      occurredAt: "2025-04-03T00:00:00Z",
      reason: "moved",
    }),
    '2025-04-03T00:00:00Z sub_9 subscription_canceled reason="moved"',
  );
  assert.equal(
    serializeAuditEntry({
      type: "payment_failed",
      subscriptionId: "sub_9",
      occurredAt: "2025-04-03T00:00:00Z",
      attempt: 3,
    }),
    "2025-04-03T00:00:00Z sub_9 payment_failed attempt=3",
  );
});
