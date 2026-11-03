import assert from "node:assert/strict";
import { test } from "node:test";
import type { SubscriptionEvent } from "../src/events.ts";
import { reduceSubscription, replay } from "../src/subscription.ts";

const started: SubscriptionEvent = {
  type: "subscription_started",
  subscriptionId: "sub_1",
  occurredAt: "2025-01-05T09:00:00Z",
  plan: "basic",
};

test("a started subscription is active on its plan", () => {
  const state = replay([started]);
  assert.equal(state.id, "sub_1");
  assert.equal(state.plan, "basic");
  assert.equal(state.status, "active");
  assert.equal(state.startedAt, "2025-01-05T09:00:00Z");
  assert.equal(state.canceledAt, null);
});

test("a plan change switches the plan", () => {
  const state = replay([
    started,
    { type: "plan_changed", subscriptionId: "sub_1", occurredAt: "2025-02-01T00:00:00Z", from: "basic", to: "pro" },
  ]);
  assert.equal(state.plan, "pro");
});

test("a failed payment makes the subscription past due and a recovery makes it active again", () => {
  const failed: SubscriptionEvent = {
    type: "payment_failed",
    subscriptionId: "sub_1",
    occurredAt: "2025-02-05T00:00:00Z",
    attempt: 2,
  };
  const pastDue = reduceSubscription(replay([started]), failed);
  assert.equal(pastDue.status, "past_due");
  assert.equal(pastDue.failedAttempts, 2);

  const recovered = reduceSubscription(pastDue, {
    type: "payment_recovered",
    subscriptionId: "sub_1",
    occurredAt: "2025-02-06T00:00:00Z",
  });
  assert.equal(recovered.status, "active");
  assert.equal(recovered.failedAttempts, 0);
});

test("cancelling records when it happened and a canceled subscription stays canceled", () => {
  const canceled = replay([
    started,
    { type: "subscription_canceled", subscriptionId: "sub_1", occurredAt: "2025-03-01T00:00:00Z", reason: "too expensive" },
  ]);
  assert.equal(canceled.status, "canceled");
  assert.equal(canceled.canceledAt, "2025-03-01T00:00:00Z");

  const afterFailure = reduceSubscription(canceled, {
    type: "payment_failed",
    subscriptionId: "sub_1",
    occurredAt: "2025-03-02T00:00:00Z",
    attempt: 1,
  });
  assert.equal(afterFailure, canceled);
});

test("a history that does not begin with the start is rejected", () => {
  assert.throws(() => replay([]), /starts with subscription_started/);
});

const paused: SubscriptionEvent = {
  type: "subscription_paused",
  subscriptionId: "sub_1",
  occurredAt: "2025-03-10T00:00:00Z",
  resumeOn: "2025-04-10",
  reason: "vacation",
};

test("pausing an active subscription remembers the resume date", () => {
  const state = replay([started, paused]);
  assert.equal(state.status, "paused");
  assert.equal(state.resumeOn, "2025-04-10");
});

test("only an active subscription can be paused", () => {
  const pastDue = replay([
    started,
    { type: "payment_failed", subscriptionId: "sub_1", occurredAt: "2025-03-05T00:00:00Z", attempt: 1 },
  ]);
  assert.equal(reduceSubscription(pastDue, paused), pastDue);

  const alreadyPaused = replay([started, paused]);
  const later: SubscriptionEvent = { ...paused, resumeOn: "2025-06-01" };
  assert.equal(reduceSubscription(alreadyPaused, later).resumeOn, "2025-04-10");
});

test("payment events leave a paused subscription paused", () => {
  const state = replay([
    started,
    paused,
    { type: "payment_failed", subscriptionId: "sub_1", occurredAt: "2025-03-12T00:00:00Z", attempt: 1 },
    { type: "payment_recovered", subscriptionId: "sub_1", occurredAt: "2025-03-13T00:00:00Z" },
  ]);
  assert.equal(state.status, "paused");
  assert.equal(state.failedAttempts, 0);
});

test("cancelling a paused subscription clears the resume date", () => {
  const state = replay([
    started,
    paused,
    { type: "subscription_canceled", subscriptionId: "sub_1", occurredAt: "2025-03-20T00:00:00Z", reason: "moved" },
  ]);
  assert.equal(state.status, "canceled");
  assert.equal(state.resumeOn, null);
});
