import assert from "node:assert/strict";
import { test } from "node:test";
import { notificationsFor } from "../src/notifier.ts";

test("a new subscription gets a welcome email", () => {
  const notifications = notificationsFor({
    type: "subscription_started",
    subscriptionId: "sub_1",
    occurredAt: "2025-01-05T09:00:00Z",
    plan: "pro",
  });
  assert.deepEqual(notifications, [{ audience: "customer", template: "welcome", data: { plan: "pro" } }]);
});

test("a failed payment tells the customer, and from the third attempt the billing team too", () => {
  const event = { type: "payment_failed", subscriptionId: "sub_1", occurredAt: "2025-02-05T00:00:00Z" } as const;
  assert.deepEqual(notificationsFor({ ...event, attempt: 2 }), [
    { audience: "customer", template: "payment-failed", data: { attempt: "2" } },
  ]);
  assert.deepEqual(notificationsFor({ ...event, attempt: 3 }), [
    { audience: "customer", template: "payment-failed", data: { attempt: "3" } },
    { audience: "billing-team", template: "payment-escalation", data: { attempt: "3" } },
  ]);
});

test("a recovery sends nothing", () => {
  const notifications = notificationsFor({
    type: "payment_recovered",
    subscriptionId: "sub_1",
    occurredAt: "2025-02-06T00:00:00Z",
  });
  assert.deepEqual(notifications, []);
});

test("a cancellation confirms to the customer with the reason", () => {
  const notifications = notificationsFor({
    type: "subscription_canceled",
    subscriptionId: "sub_1",
    occurredAt: "2025-03-01T00:00:00Z",
    reason: "too expensive",
  });
  assert.deepEqual(notifications, [
    { audience: "customer", template: "subscription-canceled", data: { reason: "too expensive" } },
  ]);
});

test("a pause only tells the customer when billing resumes", () => {
  const notifications = notificationsFor({
    type: "subscription_paused",
    subscriptionId: "sub_1",
    occurredAt: "2025-03-10T00:00:00Z",
    resumeOn: "2025-04-10",
    reason: "vacation",
  });
  assert.deepEqual(notifications, [
    { audience: "customer", template: "subscription-paused", data: { resumeOn: "2025-04-10" } },
  ]);
});
