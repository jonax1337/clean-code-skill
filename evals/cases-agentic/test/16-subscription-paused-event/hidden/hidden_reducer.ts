import assert from "node:assert/strict";
import { test } from "node:test";
import type { SubscriptionEvent } from "../src/events.ts";
import { reduceSubscription, replay } from "../src/subscription.ts";
import type { Subscription } from "../src/subscription.ts";

const started: SubscriptionEvent = {
  type: "subscription_started",
  subscriptionId: "sub_7",
  occurredAt: "2025-01-05T09:00:00Z",
  plan: "pro",
};
const paused: SubscriptionEvent = {
  type: "subscription_paused",
  subscriptionId: "sub_7",
  occurredAt: "2025-03-10T00:00:00Z",
  resumeOn: "2025-04-10",
  reason: "vacation",
};
const failed = (attempt: number): SubscriptionEvent => ({
  type: "payment_failed",
  subscriptionId: "sub_7",
  occurredAt: "2025-03-11T00:00:00Z",
  attempt,
});
const recovered: SubscriptionEvent = {
  type: "payment_recovered",
  subscriptionId: "sub_7",
  occurredAt: "2025-03-12T00:00:00Z",
};
const canceled: SubscriptionEvent = {
  type: "subscription_canceled",
  subscriptionId: "sub_7",
  occurredAt: "2025-03-20T00:00:00Z",
  reason: "moved",
};

test("a new subscription has no resume date", () => {
  assert.equal(replay([started]).resumeOn, null);
});

test("an active subscription becomes paused and remembers the resume date", () => {
  const state = replay([started, paused]);
  assert.equal(state.status, "paused");
  assert.equal(state.resumeOn, "2025-04-10");
  assert.equal(state.plan, "pro");
  assert.equal(state.id, "sub_7");
  assert.equal(state.canceledAt, null);
  assert.equal(state.failedAttempts, 0);
});

test("pausing does not modify the state it was given", () => {
  const before = replay([started]);
  const frozen: Subscription = Object.freeze({ ...before });
  const after = reduceSubscription(frozen, paused);
  assert.notEqual(after, frozen);
  assert.equal(frozen.status, "active");
  assert.equal(frozen.resumeOn, null);
});

test("a past due subscription is not paused", () => {
  const pastDue = replay([started, failed(2)]);
  const after = reduceSubscription(pastDue, paused);
  assert.equal(after.status, "past_due");
  assert.equal(after.resumeOn, null);
  assert.equal(after.failedAttempts, 2);
});

test("a canceled subscription is not paused", () => {
  const after = replay([started, canceled, paused]);
  assert.equal(after.status, "canceled");
  assert.equal(after.resumeOn, null);
});

test("pausing a paused subscription keeps the first resume date", () => {
  const second: SubscriptionEvent = { ...paused, resumeOn: "2025-09-01", reason: "again" };
  const after = replay([started, paused, second]);
  assert.equal(after.status, "paused");
  assert.equal(after.resumeOn, "2025-04-10");
});

test("a failed payment does not move a paused subscription", () => {
  const after = replay([started, paused, failed(1)]);
  assert.equal(after.status, "paused");
  assert.equal(after.failedAttempts, 0);
  assert.equal(after.resumeOn, "2025-04-10");
});

test("a recovered payment does not move a paused subscription", () => {
  const after = replay([started, paused, recovered]);
  assert.equal(after.status, "paused");
  assert.equal(after.resumeOn, "2025-04-10");
});

test("a plan change on a paused subscription keeps it paused", () => {
  const change: SubscriptionEvent = {
    type: "plan_changed",
    subscriptionId: "sub_7",
    occurredAt: "2025-03-15T00:00:00Z",
    from: "pro",
    to: "basic",
  };
  const after = replay([started, paused, change]);
  assert.equal(after.status, "paused");
  assert.equal(after.plan, "basic");
});

test("cancelling a paused subscription cancels it and clears the resume date", () => {
  const after = replay([started, paused, canceled]);
  assert.equal(after.status, "canceled");
  assert.equal(after.canceledAt, "2025-03-20T00:00:00Z");
  assert.equal(after.resumeOn, null);
});

test("payments after cancelling a paused subscription change nothing", () => {
  const after = replay([started, paused, canceled, failed(1)]);
  assert.equal(after.status, "canceled");
});
