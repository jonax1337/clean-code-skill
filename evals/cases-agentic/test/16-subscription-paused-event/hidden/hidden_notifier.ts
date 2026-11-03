import assert from "node:assert/strict";
import { test } from "node:test";
import { notificationsFor } from "../src/notifier.ts";

test("a pause sends the customer one email with the resume date and nothing else", () => {
  const notifications = notificationsFor({
    type: "subscription_paused",
    subscriptionId: "sub_9",
    occurredAt: "2025-04-02T08:30:00Z",
    resumeOn: "2025-05-01",
    reason: "vacation",
  });
  assert.deepEqual(notifications, [
    { audience: "customer", template: "subscription-paused", data: { resumeOn: "2025-05-01" } },
  ]);
});

test("the billing team is not told about a pause", () => {
  const notifications = notificationsFor({
    type: "subscription_paused",
    subscriptionId: "sub_9",
    occurredAt: "2025-04-02T08:30:00Z",
    resumeOn: "2025-05-01",
    reason: "payment trouble",
  });
  assert.equal(notifications.filter((notification) => notification.audience !== "customer").length, 0);
});

test("the other events keep their emails", () => {
  assert.deepEqual(
    notificationsFor({
      type: "payment_failed",
      subscriptionId: "sub_9",
      occurredAt: "2025-04-03T00:00:00Z",
      attempt: 3,
    }),
    [
      { audience: "customer", template: "payment-failed", data: { attempt: "3" } },
      { audience: "billing-team", template: "payment-escalation", data: { attempt: "3" } },
    ],
  );
  assert.deepEqual(
    notificationsFor({ type: "payment_recovered", subscriptionId: "sub_9", occurredAt: "2025-04-04T00:00:00Z" }),
    [],
  );
});
