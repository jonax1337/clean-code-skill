import assert from "node:assert/strict";
import { test } from "node:test";
import { serializeAuditEntry } from "../src/audit.ts";

test("a start entry names the plan", () => {
  const entry = serializeAuditEntry({
    type: "subscription_started",
    subscriptionId: "sub_1",
    occurredAt: "2025-01-05T09:00:00Z",
    plan: "pro",
  });
  assert.equal(entry, "2025-01-05T09:00:00Z sub_1 subscription_started plan=pro");
});

test("a plan change entry names both plans", () => {
  const entry = serializeAuditEntry({
    type: "plan_changed",
    subscriptionId: "sub_1",
    occurredAt: "2025-02-01T00:00:00Z",
    from: "basic",
    to: "enterprise",
  });
  assert.equal(entry, "2025-02-01T00:00:00Z sub_1 plan_changed from=basic to=enterprise");
});

test("a recovery entry has no details", () => {
  const entry = serializeAuditEntry({
    type: "payment_recovered",
    subscriptionId: "sub_1",
    occurredAt: "2025-02-06T00:00:00Z",
  });
  assert.equal(entry, "2025-02-06T00:00:00Z sub_1 payment_recovered");
});

test("a cancellation entry quotes the reason", () => {
  const entry = serializeAuditEntry({
    type: "subscription_canceled",
    subscriptionId: "sub_1",
    occurredAt: "2025-03-01T00:00:00Z",
    reason: 'said "too expensive"',
  });
  assert.equal(entry, '2025-03-01T00:00:00Z sub_1 subscription_canceled reason="said \\"too expensive\\""');
});

test("a pause entry has the resume date and the quoted reason", () => {
  const entry = serializeAuditEntry({
    type: "subscription_paused",
    subscriptionId: "sub_9",
    occurredAt: "2025-04-02T08:30:00Z",
    resumeOn: "2025-05-01",
    reason: "vacation",
  });
  assert.equal(entry, '2025-04-02T08:30:00Z sub_9 subscription_paused resumeOn=2025-05-01 reason="vacation"');
});
