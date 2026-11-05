# Blind pull-request pairs

Two coding agents did the same task. For each pair, decide which pull request you would rather merge, as a strict
reviewer: correct and preserved behavior, only what was asked, reuse, readability, tests that protect the change,
and a report that is accurate about what was changed and verified. Length is not a merit.

Write A, B or tie into the `winner` column of `ratings.csv`. Do not open `key.json` before you are done.

## P01: Adding a subscription pause event (TypeScript)

Repository: `evals/cases-agentic/test/16-subscription-paused-event/repo/`

### Task

We want customers to be able to pause their subscription, so billing needs a new `subscription_paused` event. It carries `resumeOn` (the date billing picks up again, as `YYYY-MM-DD`) and a `reason` (free text, like the cancellation reason). Here is how it should behave:

- State: an active subscription becomes `paused`, and the subscription remembers `resumeOn` (it is `null` whenever the subscription is not paused). Only an active subscription can be paused; in any other status the event changes nothing. While paused, nothing is billed, so payment events leave a paused subscription as it is. Cancelling a paused subscription works as usual and also clears `resumeOn`.
- Audit log: same line format as the other events, with the resume date and then the reason (quoted the way the cancellation reason is), e.g. `2025-04-02T08:30:00Z sub_9 subscription_paused resumeOn=2025-05-01 reason="vacation"`.
- Notifications: the customer gets a `subscription-paused` email that carries the resume date as `resumeOn`. Nobody else is notified.

Resuming is a separate piece of work, so leave that out. Please add tests too.

### Change A

````text
<diff>
diff --git a/src/audit.ts b/src/audit.ts
index 8db4703..d0fb480 100644
--- a/src/audit.ts
+++ b/src/audit.ts
@@ -15,12 +15,14 @@ function auditDetails(event: SubscriptionEvent): string {
     case "plan_changed":
       return `from=${event.from} to=${event.to}`;
     case "payment_failed":
       return `attempt=${event.attempt}`;
     case "payment_recovered":
       return "";
     case "subscription_canceled":
       return `reason=${JSON.stringify(event.reason)}`;
+    case "subscription_paused":
+      return `resumeOn=${event.resumeOn} reason=${JSON.stringify(event.reason)}`;
     default:
       return assertNever(event);
   }
 }
diff --git a/src/events.ts b/src/events.ts
index e42e30f..b45f4d0 100644
--- a/src/events.ts
+++ b/src/events.ts
@@ -27,14 +27,22 @@ export interface PaymentRecovered extends EventBase {
   type: "payment_recovered";
 }
 
 export interface SubscriptionCanceled extends EventBase {
   type: "subscription_canceled";
   reason: string;
 }
 
+export interface SubscriptionPaused extends EventBase {
+  type: "subscription_paused";
+  /** The date billing picks up again, as YYYY-MM-DD. */
+  resumeOn: string;
+  reason: string;
+}
+
 export type SubscriptionEvent =
   | SubscriptionStarted
   | PlanChanged
   | PaymentFailed
   | PaymentRecovered
-  | SubscriptionCanceled;
+  | SubscriptionCanceled
+  | SubscriptionPaused;
diff --git a/src/notifier.ts b/src/notifier.ts
index e54194a..62a5dd1 100644
--- a/src/notifier.ts
+++ b/src/notifier.ts
@@ -18,16 +18,18 @@ export function notificationsFor(event: SubscriptionEvent): Notification[] {
     case "plan_changed":
       return [{ audience: "customer", template: "plan-changed", data: { from: event.from, to: event.to } }];
     case "payment_failed":
       return paymentFailedNotifications(event);
     case "payment_recovered":
       return [];
     case "subscription_canceled":
       return [{ audience: "customer", template: "subscription-canceled", data: { reason: event.reason } }];
+    case "subscription_paused":
+      return [{ audience: "customer", template: "subscription-paused", data: { resumeOn: event.resumeOn } }];
     default:
       return assertNever(event);
   }
 }
 
 function paymentFailedNotifications(event: PaymentFailed): Notification[] {
   const data = { attempt: String(event.attempt) };
   const notifications: Notification[] = [{ audience: "customer", template: "payment-failed", data }];
diff --git a/src/subscription.ts b/src/subscription.ts
index 9b6603e..5bbe360 100644
--- a/src/subscription.ts
+++ b/src/subscription.ts
@@ -1,21 +1,23 @@
 import { assertNever } from "./assert-never.ts";
 import type { Plan, SubscriptionEvent, SubscriptionStarted } from "./events.ts";
 
-export type SubscriptionStatus = "active" | "past_due" | "canceled";
+export type SubscriptionStatus = "active" | "past_due" | "paused" | "canceled";
 
 export interface Subscription {
   id: string;
   plan: Plan;
   status: SubscriptionStatus;
   /** The attempt number of the latest failed charge; 0 while payments are fine. */
   failedAttempts: number;
   startedAt: string;
   canceledAt: string | null;
+  /** The date billing picks up again (YYYY-MM-DD); null unless the subscription is paused. */
+  resumeOn: string | null;
 }
 
 /** The state of a subscription after all of its events, oldest first. The first event must be the start. */
 export function replay(events: readonly SubscriptionEvent[]): Subscription {
   const [first, ...rest] = events;
   if (first?.type !== "subscription_started") {
     throw new Error("A subscription history starts with subscription_started");
   }
@@ -25,37 +27,43 @@ export function replay(events: readonly SubscriptionEvent[]): Subscription {
 export function reduceSubscription(state: Subscription, event: SubscriptionEvent): Subscription {
   switch (event.type) {
     case "subscription_started":
       // A repeated start event changes nothing.
       return state;
     case "plan_changed":
       return { ...state, plan: event.to };
     case "payment_failed":
-      if (state.status === "canceled") {
+      if (state.status === "canceled" || state.status === "paused") {
         return state;
       }
       return { ...state, status: "past_due", failedAttempts: event.attempt };
     case "payment_recovered":
       if (state.status !== "past_due") {
         return state;
       }
       return { ...state, status: "active", failedAttempts: 0 };
     case "subscription_canceled":
       if (state.status === "canceled") {
         return state;
       }
-      return { ...state, status: "canceled", canceledAt: event.occurredAt };
+      return { ...state, status: "canceled", canceledAt: event.occurredAt, resumeOn: null };
+    case "subscription_paused":
+      if (state.status !== "active") {
+        return state;
+      }
+      return { ...state, status: "paused", resumeOn: event.resumeOn };
     default:
       return assertNever(event);
   }
 }
 
 function startedSubscription(event: SubscriptionStarted): Subscription {
   return {
     id: event.subscriptionId,
     plan: event.plan,
     status: "active",
     failedAttempts: 0,
     startedAt: event.occurredAt,
     canceledAt: null,
+    resumeOn: null,
   };
 }
diff --git a/test/audit.test.ts b/test/audit.test.ts
index 23af255..b20aa77 100644
--- a/test/audit.test.ts
+++ b/test/audit.test.ts
@@ -36,8 +36,19 @@ test("a cancellation entry quotes the reason", () => {
   const entry = serializeAuditEntry({
     type: "subscription_canceled",
     subscriptionId: "sub_1",
     occurredAt: "2025-03-01T00:00:00Z",
     reason: 'said "too expensive"',
   });
   assert.equal(entry, '2025-03-01T00:00:00Z sub_1 subscription_canceled reason="said \\"too expensive\\""');
 });
+
+test("a pause entry has the resume date and the quoted reason", () => {
+  const entry = serializeAuditEntry({
+    type: "subscription_paused",
+    subscriptionId: "sub_9",
+    occurredAt: "2025-04-02T08:30:00Z",
+    resumeOn: "2025-05-01",
+    reason: "vacation",
+  });
+  assert.equal(entry, '2025-04-02T08:30:00Z sub_9 subscription_paused resumeOn=2025-05-01 reason="vacation"');
+});
diff --git a/test/notifier.test.ts b/test/notifier.test.ts
index 648ba43..901e9eb 100644
--- a/test/notifier.test.ts
+++ b/test/notifier.test.ts
@@ -38,8 +38,21 @@ test("a cancellation confirms to the customer with the reason", () => {
     subscriptionId: "sub_1",
     occurredAt: "2025-03-01T00:00:00Z",
     reason: "too expensive",
   });
   assert.deepEqual(notifications, [
     { audience: "customer", template: "subscription-canceled", data: { reason: "too expensive" } },
   ]);
 });
+
+test("a pause tells only the customer when billing resumes", () => {
+  const notifications = notificationsFor({
+    type: "subscription_paused",
+    subscriptionId: "sub_1",
+    occurredAt: "2025-04-02T08:30:00Z",
+    resumeOn: "2025-05-01",
+    reason: "vacation",
+  });
+  assert.deepEqual(notifications, [
+    { audience: "customer", template: "subscription-paused", data: { resumeOn: "2025-05-01" } },
+  ]);
+});
diff --git a/test/subscription.test.ts b/test/subscription.test.ts
index f154a91..7f1e7a7 100644
--- a/test/subscription.test.ts
+++ b/test/subscription.test.ts
@@ -62,8 +62,71 @@ test("cancelling records when it happened and a canceled subscription stays canc
     attempt: 1,
   });
   assert.equal(afterFailure, canceled);
 });
 
 test("a history that does not begin with the start is rejected", () => {
   assert.throws(() => replay([]), /starts with subscription_started/);
 });
+
+const paused: SubscriptionEvent = {
+  type: "subscription_paused",
+  subscriptionId: "sub_1",
+  occurredAt: "2025-04-02T08:30:00Z",
+  resumeOn: "2025-05-01",
+  reason: "vacation",
+};
+
+test("pausing an active subscription pauses it and remembers when billing resumes", () => {
+  const state = replay([started, paused]);
+  assert.equal(state.status, "paused");
+  assert.equal(state.resumeOn, "2025-05-01");
+});
+
+test("resumeOn is null until the subscription is paused", () => {
+  assert.equal(replay([started]).resumeOn, null);
+});
+
+test("pausing changes nothing unless the subscription is active", () => {
+  const pastDue = replay([
+    started,
+    { type: "payment_failed", subscriptionId: "sub_1", occurredAt: "2025-02-05T00:00:00Z", attempt: 1 },
+  ]);
+  assert.equal(reduceSubscription(pastDue, paused), pastDue);
+
+  const canceled = replay([
+    started,
+    { type: "subscription_canceled", subscriptionId: "sub_1", occurredAt: "2025-03-01T00:00:00Z", reason: "x" },
+  ]);
+  assert.equal(reduceSubscription(canceled, paused), canceled);
+
+  const alreadyPaused = replay([started, paused]);
+  assert.equal(reduceSubscription(alreadyPaused, { ...paused, resumeOn: "2025-06-01" }), alreadyPaused);
+});
+
+test("payment events leave a paused subscription as it is", () => {
+  const state = replay([started, paused]);
+  const failed = reduceSubscription(state, {
+    type: "payment_failed",
+    subscriptionId: "sub_1",
+    occurredAt: "2025-04-03T00:00:00Z",
+    attempt: 1,
+  });
+  assert.equal(failed, state);
+  const recovered = reduceSubscription(state, {
+    type: "payment_recovered",
+    subscriptionId: "sub_1",
+    occurredAt: "2025-04-04T00:00:00Z",
+  });
+  assert.equal(recovered, state);
+});
+
+test("cancelling a paused subscription cancels it and clears resumeOn", () => {
+  const state = replay([
+    started,
+    paused,
+    { type: "subscription_canceled", subscriptionId: "sub_1", occurredAt: "2025-04-10T00:00:00Z", reason: "x" },
+  ]);
+  assert.equal(state.status, "canceled");
+  assert.equal(state.canceledAt, "2025-04-10T00:00:00Z");
+  assert.equal(state.resumeOn, null);
+});

</diff>
<report>
The `subscription_paused` event now works end to end. `npm test` passes (20 tests, 0 failures) and `npm run typecheck` reports no errors.

- **State:**
  - `src/subscription.ts` has a new `paused` status and a `resumeOn: string | null` field, which is `null` until a pause.
  - Only an `active` subscription is paused; in any other status the event changes nothing.
  - `payment_failed` now also leaves a paused subscription unchanged. `payment_recovered` already did, because it only acts on `past_due`.
  - Cancelling a paused subscription works as before and also sets `resumeOn` back to `null`.
- **Audit log:** `src/audit.ts` writes `resumeOn=… reason="…"`, with the reason quoted the same way as for cancellation. Your example line is one of the new tests.
- **Notifications:** `src/notifier.ts` sends the customer a `subscription-paused` email with `resumeOn` in its data, and nobody else.
- **Event type:** the event itself is defined in `src/events.ts`.
- **Tests:** I added tests in all three test files. They cover:
  - pausing an active subscription;
  - ignoring a pause from `past_due`, `canceled` or already-`paused`;
  - payment events on a paused subscription;
  - cancelling from `paused`;
  - the audit line;
  - the email.

Resuming is not implemented, as you asked. A paused subscription has no way back to `active` yet.

I didn't check that `resumeOn` is a valid `YYYY-MM-DD` date. The event just carries whatever string it is given, as `occurredAt` does today.
</report>
````

### Change B

````text
<diff>
diff --git a/src/audit.ts b/src/audit.ts
index 8db4703..d0fb480 100644
--- a/src/audit.ts
+++ b/src/audit.ts
@@ -15,12 +15,14 @@ function auditDetails(event: SubscriptionEvent): string {
     case "plan_changed":
       return `from=${event.from} to=${event.to}`;
     case "payment_failed":
       return `attempt=${event.attempt}`;
     case "payment_recovered":
       return "";
     case "subscription_canceled":
       return `reason=${JSON.stringify(event.reason)}`;
+    case "subscription_paused":
+      return `resumeOn=${event.resumeOn} reason=${JSON.stringify(event.reason)}`;
     default:
       return assertNever(event);
   }
 }
diff --git a/src/events.ts b/src/events.ts
index e42e30f..b45f4d0 100644
--- a/src/events.ts
+++ b/src/events.ts
@@ -27,14 +27,22 @@ export interface PaymentRecovered extends EventBase {
   type: "payment_recovered";
 }
 
 export interface SubscriptionCanceled extends EventBase {
   type: "subscription_canceled";
   reason: string;
 }
 
+export interface SubscriptionPaused extends EventBase {
+  type: "subscription_paused";
+  /** The date billing picks up again, as YYYY-MM-DD. */
+  resumeOn: string;
+  reason: string;
+}
+
 export type SubscriptionEvent =
   | SubscriptionStarted
   | PlanChanged
   | PaymentFailed
   | PaymentRecovered
-  | SubscriptionCanceled;
+  | SubscriptionCanceled
+  | SubscriptionPaused;
diff --git a/src/index.ts b/src/index.ts
index 4d512c4..6acfaf0 100644
--- a/src/index.ts
+++ b/src/index.ts
@@ -1,6 +1,6 @@
 export { serializeAuditEntry } from "./audit.ts";
-export type { Plan, SubscriptionEvent } from "./events.ts";
+export type { Plan, SubscriptionEvent, SubscriptionPaused } from "./events.ts";
 export { notificationsFor } from "./notifier.ts";
 export type { Notification } from "./notifier.ts";
 export { reduceSubscription, replay } from "./subscription.ts";
 export type { Subscription, SubscriptionStatus } from "./subscription.ts";
diff --git a/src/notifier.ts b/src/notifier.ts
index e54194a..62a5dd1 100644
--- a/src/notifier.ts
+++ b/src/notifier.ts
@@ -18,16 +18,18 @@ export function notificationsFor(event: SubscriptionEvent): Notification[] {
     case "plan_changed":
       return [{ audience: "customer", template: "plan-changed", data: { from: event.from, to: event.to } }];
     case "payment_failed":
       return paymentFailedNotifications(event);
     case "payment_recovered":
       return [];
     case "subscription_canceled":
       return [{ audience: "customer", template: "subscription-canceled", data: { reason: event.reason } }];
+    case "subscription_paused":
+      return [{ audience: "customer", template: "subscription-paused", data: { resumeOn: event.resumeOn } }];
     default:
       return assertNever(event);
   }
 }
 
 function paymentFailedNotifications(event: PaymentFailed): Notification[] {
   const data = { attempt: String(event.attempt) };
   const notifications: Notification[] = [{ audience: "customer", template: "payment-failed", data }];
diff --git a/src/subscription.ts b/src/subscription.ts
index 9b6603e..b706113 100644
--- a/src/subscription.ts
+++ b/src/subscription.ts
@@ -1,21 +1,23 @@
 import { assertNever } from "./assert-never.ts";
 import type { Plan, SubscriptionEvent, SubscriptionStarted } from "./events.ts";
 
-export type SubscriptionStatus = "active" | "past_due" | "canceled";
+export type SubscriptionStatus = "active" | "past_due" | "paused" | "canceled";
 
 export interface Subscription {
   id: string;
   plan: Plan;
   status: SubscriptionStatus;
   /** The attempt number of the latest failed charge; 0 while payments are fine. */
   failedAttempts: number;
   startedAt: string;
   canceledAt: string | null;
+  /** The date billing picks up again (YYYY-MM-DD); null whenever the subscription is not paused. */
+  resumeOn: string | null;
 }
 
 /** The state of a subscription after all of its events, oldest first. The first event must be the start. */
 export function replay(events: readonly SubscriptionEvent[]): Subscription {
   const [first, ...rest] = events;
   if (first?.type !== "subscription_started") {
     throw new Error("A subscription history starts with subscription_started");
   }
@@ -25,37 +27,43 @@ export function replay(events: readonly SubscriptionEvent[]): Subscription {
 export function reduceSubscription(state: Subscription, event: SubscriptionEvent): Subscription {
   switch (event.type) {
     case "subscription_started":
       // A repeated start event changes nothing.
       return state;
     case "plan_changed":
       return { ...state, plan: event.to };
     case "payment_failed":
-      if (state.status === "canceled") {
+      if (state.status === "canceled" || state.status === "paused") {
         return state;
       }
       return { ...state, status: "past_due", failedAttempts: event.attempt };
     case "payment_recovered":
       if (state.status !== "past_due") {
         return state;
       }
       return { ...state, status: "active", failedAttempts: 0 };
     case "subscription_canceled":
       if (state.status === "canceled") {
         return state;
       }
-      return { ...state, status: "canceled", canceledAt: event.occurredAt };
+      return { ...state, status: "canceled", canceledAt: event.occurredAt, resumeOn: null };
+    case "subscription_paused":
+      if (state.status !== "active") {
+        return state;
+      }
+      return { ...state, status: "paused", resumeOn: event.resumeOn };
     default:
       return assertNever(event);
   }
 }
 
 function startedSubscription(event: SubscriptionStarted): Subscription {
   return {
     id: event.subscriptionId,
     plan: event.plan,
     status: "active",
     failedAttempts: 0,
     startedAt: event.occurredAt,
     canceledAt: null,
+    resumeOn: null,
   };
 }
diff --git a/test/audit.test.ts b/test/audit.test.ts
index 23af255..275a5ca 100644
--- a/test/audit.test.ts
+++ b/test/audit.test.ts
@@ -36,8 +36,19 @@ test("a cancellation entry quotes the reason", () => {
   const entry = serializeAuditEntry({
     type: "subscription_canceled",
     subscriptionId: "sub_1",
     occurredAt: "2025-03-01T00:00:00Z",
     reason: 'said "too expensive"',
   });
   assert.equal(entry, '2025-03-01T00:00:00Z sub_1 subscription_canceled reason="said \\"too expensive\\""');
 });
+
+test("a pause entry has the resume date and the quoted reason", () => {
+  const entry = serializeAuditEntry({
+    type: "subscription_paused",
+    subscriptionId: "sub_9",
+    occurredAt: "2025-04-02T08:30:00Z",
+    resumeOn: "2025-05-01",
+    reason: "vacation",
+  });
+  assert.equal(entry, '2025-04-02T08:30:00Z sub_9 subscription_paused resumeOn=2025-05-01 reason="vacation"');
+});
diff --git a/test/notifier.test.ts b/test/notifier.test.ts
index 648ba43..3f9e0c6 100644
--- a/test/notifier.test.ts
+++ b/test/notifier.test.ts
@@ -38,8 +38,21 @@ test("a cancellation confirms to the customer with the reason", () => {
     subscriptionId: "sub_1",
     occurredAt: "2025-03-01T00:00:00Z",
     reason: "too expensive",
   });
   assert.deepEqual(notifications, [
     { audience: "customer", template: "subscription-canceled", data: { reason: "too expensive" } },
   ]);
 });
+
+test("a pause tells only the customer, with the resume date", () => {
+  const notifications = notificationsFor({
+    type: "subscription_paused",
+    subscriptionId: "sub_9",
+    occurredAt: "2025-04-02T08:30:00Z",
+    resumeOn: "2025-05-01",
+    reason: "vacation",
+  });
+  assert.deepEqual(notifications, [
+    { audience: "customer", template: "subscription-paused", data: { resumeOn: "2025-05-01" } },
+  ]);
+});
diff --git a/test/subscription.test.ts b/test/subscription.test.ts
index f154a91..02f6888 100644
--- a/test/subscription.test.ts
+++ b/test/subscription.test.ts
@@ -62,8 +62,68 @@ test("cancelling records when it happened and a canceled subscription stays canc
     attempt: 1,
   });
   assert.equal(afterFailure, canceled);
 });
 
 test("a history that does not begin with the start is rejected", () => {
   assert.throws(() => replay([]), /starts with subscription_started/);
 });
+
+const paused: SubscriptionEvent = {
+  type: "subscription_paused",
+  subscriptionId: "sub_1",
+  occurredAt: "2025-04-02T08:30:00Z",
+  resumeOn: "2025-05-01",
+  reason: "vacation",
+};
+
+test("pausing an active subscription records the resume date; it is null otherwise", () => {
+  assert.equal(replay([started]).resumeOn, null);
+  const state = replay([started, paused]);
+  assert.equal(state.status, "paused");
+  assert.equal(state.resumeOn, "2025-05-01");
+});
+
+test("pausing only works on an active subscription", () => {
+  const pastDue = reduceSubscription(replay([started]), {
+    type: "payment_failed",
+    subscriptionId: "sub_1",
+    occurredAt: "2025-02-05T00:00:00Z",
+    attempt: 1,
+  });
+  assert.equal(reduceSubscription(pastDue, paused), pastDue);
+
+  const canceled = replay([
+    started,
+    { type: "subscription_canceled", subscriptionId: "sub_1", occurredAt: "2025-03-01T00:00:00Z", reason: "x" },
+  ]);
+  assert.equal(reduceSubscription(canceled, paused), canceled);
+
+  const alreadyPaused = replay([started, paused]);
+  assert.equal(
+    reduceSubscription(alreadyPaused, { ...paused, resumeOn: "2025-09-01" }),
+    alreadyPaused,
+  );
+});
+
+test("payment events leave a paused subscription as it is", () => {
+  const state = replay([started, paused]);
+  assert.equal(
+    reduceSubscription(state, { type: "payment_failed", subscriptionId: "sub_1", occurredAt: "2025-04-05T00:00:00Z", attempt: 1 }),
+    state,
+  );
+  assert.equal(
+    reduceSubscription(state, { type: "payment_recovered", subscriptionId: "sub_1", occurredAt: "2025-04-06T00:00:00Z" }),
+    state,
+  );
+});
+
+test("cancelling a paused subscription cancels it and clears the resume date", () => {
+  const state = replay([
+    started,
+    paused,
+    { type: "subscription_canceled", subscriptionId: "sub_1", occurredAt: "2025-04-10T00:00:00Z", reason: "x" },
+  ]);
+  assert.equal(state.status, "canceled");
+  assert.equal(state.canceledAt, "2025-04-10T00:00:00Z");
+  assert.equal(state.resumeOn, null);
+});

</diff>
<report>
I added the `subscription_paused` event to state, the audit log and notifications. I ran `npm test` (19 tests, all passing) and `npm run typecheck`, which printed no errors. I didn't commit anything.

- **State** (`src/subscription.ts`):
  - There is a new `paused` status and a `resumeOn` field, which is `null` unless the subscription is paused.
  - Pausing only changes an `active` subscription. In any other status, including one that is already paused, the event leaves the state alone.
  - `payment_failed` now also leaves a paused subscription untouched. `payment_recovered` already did, because it only acts on `past_due`.
  - Cancelling a paused subscription cancels it as usual and sets `resumeOn` back to `null`.
- **Audit log** (`src/audit.ts`): the line looks like `… sub_9 subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way as the cancellation reason.
- **Notifications** (`src/notifier.ts`): the customer gets a `subscription-paused` email with `resumeOn` in its data, and nobody else is notified.
- **Event type and exports**: `SubscriptionPaused` is defined in `src/events.ts` and exported from `src/index.ts`.
- **Tests**: I added four state tests (pause records the date, pause is ignored outside `active`, payment events leave a paused subscription alone, cancel clears `resumeOn`). I also added one audit test and one notifier test.

Resuming is not included, as you asked. Because there is no resume event yet, a paused subscription can only end by being cancelled.
</report>
````

## P02: Refund command for the order service (Java)

Repository: `evals/cases-agentic/test/13-refund-command-handler/repo/`

### Task

We need to be able to refund orders. Please add a `RefundOrder(orderId, amount)` command to the order service. Support wants these rules: only shipped or delivered orders can be refunded, a refund can be partial but all refunds of an order together can never be more than what the customer actually paid, and the refund is recorded on the order (it already has `amountRefunded`). The order's status stays as it is.

### Change A

````text
<diff>
diff --git a/src/main/java/shop/Order.java b/src/main/java/shop/Order.java
index 72812b4..3fca155 100644
--- a/src/main/java/shop/Order.java
+++ b/src/main/java/shop/Order.java
@@ -65,12 +65,16 @@ public final class Order {
     public void markShipped() {
         this.status = OrderStatus.SHIPPED;
     }
 
     public void markDelivered() {
         this.status = OrderStatus.DELIVERED;
     }
 
+    public void recordRefund(BigDecimal amount) {
+        this.amountRefunded = this.amountRefunded.add(amount);
+    }
+
     public void cancel() {
         this.status = OrderStatus.CANCELLED;
     }
 }
diff --git a/src/main/java/shop/OrderServices.java b/src/main/java/shop/OrderServices.java
index 88ea463..cdcf316 100644
--- a/src/main/java/shop/OrderServices.java
+++ b/src/main/java/shop/OrderServices.java
@@ -7,11 +7,12 @@ public final class OrderServices {
 
     public static CommandBus createBus(OrderRepository orders) {
         CommandBus bus = new CommandBus();
         bus.register(PlaceOrder.class, new PlaceOrderHandler(orders));
         bus.register(PayOrder.class, new PayOrderHandler(orders));
         bus.register(ShipOrder.class, new ShipOrderHandler(orders));
         bus.register(DeliverOrder.class, new DeliverOrderHandler(orders));
         bus.register(CancelOrder.class, new CancelOrderHandler(orders));
+        bus.register(RefundOrder.class, new RefundOrderHandler(orders));
         return bus;
     }
 }
diff --git a/src/main/java/shop/RefundOrder.java b/src/main/java/shop/RefundOrder.java
new file mode 100644
index 0000000..38aee82
--- /dev/null
+++ b/src/main/java/shop/RefundOrder.java
@@ -0,0 +1,5 @@
+package shop;
+
+import java.math.BigDecimal;
+
+public record RefundOrder(String orderId, BigDecimal amount) {}
diff --git a/src/main/java/shop/RefundOrderHandler.java b/src/main/java/shop/RefundOrderHandler.java
new file mode 100644
index 0000000..e01087e
--- /dev/null
+++ b/src/main/java/shop/RefundOrderHandler.java
@@ -0,0 +1,41 @@
+package shop;
+
+import java.util.Optional;
+
+public final class RefundOrderHandler implements CommandHandler<RefundOrder> {
+    private final OrderRepository orders;
+
+    public RefundOrderHandler(OrderRepository orders) {
+        this.orders = orders;
+    }
+
+    @Override
+    public Result<Order> handle(RefundOrder command) {
+        Validator validator = new Validator()
+                .requireText("orderId", command.orderId())
+                .requireMoney("amount", command.amount());
+        if (!validator.isValid()) {
+            return validator.failure();
+        }
+        Optional<Order> found = orders.find(command.orderId());
+        if (found.isEmpty()) {
+            return Result.failure(ErrorCode.NOT_FOUND, "Order " + command.orderId() + " does not exist");
+        }
+        Order order = found.get();
+        if (order.status() != OrderStatus.SHIPPED && order.status() != OrderStatus.DELIVERED) {
+            return Result.failure(
+                    ErrorCode.INVALID_STATE,
+                    "Only shipped or delivered orders can be refunded, but order " + order.id() + " is "
+                            + order.status());
+        }
+        if (order.amountRefunded().add(command.amount()).compareTo(order.amountPaid()) > 0) {
+            return Result.failure(
+                    ErrorCode.INVALID_INPUT,
+                    "Refund " + command.amount() + " exceeds the refundable amount "
+                            + order.amountPaid().subtract(order.amountRefunded()));
+        }
+        order.recordRefund(command.amount());
+        orders.save(order);
+        return Result.ok(order);
+    }
+}
diff --git a/src/test/java/shop/RefundOrderHandlerTest.java b/src/test/java/shop/RefundOrderHandlerTest.java
new file mode 100644
index 0000000..7e53570
--- /dev/null
+++ b/src/test/java/shop/RefundOrderHandlerTest.java
@@ -0,0 +1,70 @@
+package shop;
+
+import static org.junit.jupiter.api.Assertions.assertEquals;
+import static org.junit.jupiter.api.Assertions.assertFalse;
+import static org.junit.jupiter.api.Assertions.assertTrue;
+
+import java.math.BigDecimal;
+import org.junit.jupiter.api.BeforeEach;
+import org.junit.jupiter.api.Test;
+
+class RefundOrderHandlerTest {
+    private final OrderRepository orders = new InMemoryOrderRepository();
+    private final CommandBus bus = OrderServices.createBus(orders);
+
+    @BeforeEach
+    void placePayAndShip() {
+        bus.dispatch(new PlaceOrder("o-1", "c-1", new BigDecimal("100.00")));
+        bus.dispatch(new PayOrder("o-1", new BigDecimal("80.00")));
+        bus.dispatch(new ShipOrder("o-1"));
+    }
+
+    private static BigDecimal money(String v) {
+        return new BigDecimal(v);
+    }
+
+    @Test
+    void recordsPartialRefundsAndKeepsStatus() {
+        assertTrue(bus.dispatch(new RefundOrder("o-1", money("30.00"))).isOk());
+        assertTrue(bus.dispatch(new RefundOrder("o-1", money("20.00"))).isOk());
+
+        Order stored = orders.find("o-1").orElseThrow();
+        assertEquals(0, money("50.00").compareTo(stored.amountRefunded()));
+        assertEquals(OrderStatus.SHIPPED, stored.status());
+    }
+
+    @Test
+    void allowsRefundOfExactlyWhatWasPaidOnDeliveredOrder() {
+        bus.dispatch(new DeliverOrder("o-1"));
+
+        assertTrue(bus.dispatch(new RefundOrder("o-1", money("80.00"))).isOk());
+        assertEquals(OrderStatus.DELIVERED, orders.find("o-1").orElseThrow().status());
+    }
+
+    @Test
+    void rejectsRefundsAddingUpToMoreThanPaid() {
+        bus.dispatch(new RefundOrder("o-1", money("50.00")));
+
+        Result<Order> result = bus.dispatch(new RefundOrder("o-1", money("30.01")));
+
+        assertFalse(result.isOk());
+        assertEquals(ErrorCode.INVALID_INPUT, result.error().code());
+        assertEquals(0, money("50.00").compareTo(orders.find("o-1").orElseThrow().amountRefunded()));
+    }
+
+    @Test
+    void rejectsOrdersThatAreNotShippedOrDelivered() {
+        bus.dispatch(new PlaceOrder("o-2", "c-1", money("10.00")));
+        bus.dispatch(new PayOrder("o-2", money("10.00")));
+
+        Result<Order> result = bus.dispatch(new RefundOrder("o-2", money("5.00")));
+
+        assertEquals(ErrorCode.INVALID_STATE, result.error().code());
+    }
+
+    @Test
+    void rejectsNonPositiveAmountAndUnknownOrder() {
+        assertEquals(ErrorCode.INVALID_INPUT, bus.dispatch(new RefundOrder("o-1", money("0"))).error().code());
+        assertEquals(ErrorCode.NOT_FOUND, bus.dispatch(new RefundOrder("nope", money("1.00"))).error().code());
+    }
+}

</diff>
<report>
`RefundOrder(orderId, amount)` now works as its own command, and all 25 tests pass, including the 5 new ones. I haven't committed anything.

- **Status:** only `SHIPPED` or `DELIVERED` orders can be refunded. Anything else fails with `INVALID_STATE`.
- **Limit:** the refunds on an order together can't exceed `amountPaid`, which can be lower than the order total. A refund that would go over fails with `INVALID_INPUT`, and the message includes the amount still refundable.
- **Recording:** each refund is added to `amountRefunded`, so partial refunds accumulate. The order's status doesn't change.
- **Input checks:** the amount goes through the same validator as payments, so it must be positive with at most two decimals. An unknown order returns `NOT_FOUND`.

The new files are `RefundOrder.java`, `RefundOrderHandler.java` and `RefundOrderHandlerTest.java`. I also added `recordRefund` to `Order.java` and registered the handler in `OrderServices.java`.

I ran the tests with `java tools/RunTests.java`, since Maven and Gradle aren't installed here.
</report>
````

### Change B

````text
<diff>
diff --git a/README.md b/README.md
index 175bb8d..dd1441d 100644
--- a/README.md
+++ b/README.md
@@ -8,18 +8,20 @@ unknown order, wrong status) as a failed `Result`; they do not throw.
 
 | Command        | Handler               | Moves the order from              |
 |----------------|-----------------------|-----------------------------------|
 | `PlaceOrder`   | `PlaceOrderHandler`   | (new) to `PLACED`                 |
 | `PayOrder`     | `PayOrderHandler`     | `PLACED` to `PAID`                |
 | `ShipOrder`    | `ShipOrderHandler`    | `PAID` to `SHIPPED`               |
 | `DeliverOrder` | `DeliverOrderHandler` | `SHIPPED` to `DELIVERED`          |
 | `CancelOrder`  | `CancelOrderHandler`  | `PLACED` or `PAID` to `CANCELLED` |
+| `RefundOrder`  | `RefundOrderHandler`  | stays `SHIPPED` or `DELIVERED`    |
 
 All handlers are registered in `OrderServices.createBus`. Commands are sent through `CommandBus.dispatch`.
 
-An order's amount paid can be lower than its total, for example when a voucher covered part of it. Money is
+An order's amount paid can be lower than its total, for example when a voucher covered part of it. Refunds
+can be partial, but all refunds of an order together never exceed the amount paid. Money is
 `BigDecimal` with at most two decimal places.
 
 ## Tests
 
 `java tools/RunTests.java` compiles `src/main` and `src/test` into `build/` and runs all JUnit 5 tests with the
 console launcher in `lib/`. It needs a JDK (17 or newer).
diff --git a/src/main/java/shop/Order.java b/src/main/java/shop/Order.java
index 72812b4..780b1a5 100644
--- a/src/main/java/shop/Order.java
+++ b/src/main/java/shop/Order.java
@@ -65,12 +65,16 @@ public final class Order {
     public void markShipped() {
         this.status = OrderStatus.SHIPPED;
     }
 
     public void markDelivered() {
         this.status = OrderStatus.DELIVERED;
     }
 
+    public void recordRefund(BigDecimal amount) {
+        this.amountRefunded = this.amountRefunded.add(amount);
+    }
+
     public void cancel() {
         this.status = OrderStatus.CANCELLED;
     }
 }
diff --git a/src/main/java/shop/OrderServices.java b/src/main/java/shop/OrderServices.java
index 88ea463..4e53f98 100644
--- a/src/main/java/shop/OrderServices.java
+++ b/src/main/java/shop/OrderServices.java
@@ -7,11 +7,12 @@ public final class OrderServices {
 
     public static CommandBus createBus(OrderRepository orders) {
         CommandBus bus = new CommandBus();
         bus.register(PlaceOrder.class, new PlaceOrderHandler(orders));
         bus.register(PayOrder.class, new PayOrderHandler(orders));
         bus.register(ShipOrder.class, new ShipOrderHandler(orders));
         bus.register(DeliverOrder.class, new DeliverOrderHandler(orders));
         bus.register(CancelOrder.class, new CancelOrderHandler(orders));
+        bus.register(RefundOrder.class, new RefundOrderHandler(orders));
         return bus;
     }
 }
diff --git a/src/main/java/shop/RefundOrder.java b/src/main/java/shop/RefundOrder.java
new file mode 100644
index 0000000..38aee82
--- /dev/null
+++ b/src/main/java/shop/RefundOrder.java
@@ -0,0 +1,5 @@
+package shop;
+
+import java.math.BigDecimal;
+
+public record RefundOrder(String orderId, BigDecimal amount) {}
diff --git a/src/main/java/shop/RefundOrderHandler.java b/src/main/java/shop/RefundOrderHandler.java
new file mode 100644
index 0000000..24fba35
--- /dev/null
+++ b/src/main/java/shop/RefundOrderHandler.java
@@ -0,0 +1,43 @@
+package shop;
+
+import java.math.BigDecimal;
+import java.util.Optional;
+
+public final class RefundOrderHandler implements CommandHandler<RefundOrder> {
+    private final OrderRepository orders;
+
+    public RefundOrderHandler(OrderRepository orders) {
+        this.orders = orders;
+    }
+
+    @Override
+    public Result<Order> handle(RefundOrder command) {
+        Validator validator = new Validator()
+                .requireText("orderId", command.orderId())
+                .requireMoney("amount", command.amount());
+        if (!validator.isValid()) {
+            return validator.failure();
+        }
+        Optional<Order> found = orders.find(command.orderId());
+        if (found.isEmpty()) {
+            return Result.failure(ErrorCode.NOT_FOUND, "Order " + command.orderId() + " does not exist");
+        }
+        Order order = found.get();
+        if (order.status() != OrderStatus.SHIPPED && order.status() != OrderStatus.DELIVERED) {
+            return Result.failure(
+                    ErrorCode.INVALID_STATE,
+                    "Only shipped or delivered orders can be refunded, but order " + order.id() + " is "
+                            + order.status());
+        }
+        BigDecimal refundable = order.amountPaid().subtract(order.amountRefunded());
+        if (command.amount().compareTo(refundable) > 0) {
+            return Result.failure(
+                    ErrorCode.INVALID_INPUT,
+                    "Refund " + command.amount() + " is more than the " + refundable
+                            + " still refundable on order " + order.id());
+        }
+        order.recordRefund(command.amount());
+        orders.save(order);
+        return Result.ok(order);
+    }
+}
diff --git a/src/test/java/shop/RefundOrderHandlerTest.java b/src/test/java/shop/RefundOrderHandlerTest.java
new file mode 100644
index 0000000..cbd37aa
--- /dev/null
+++ b/src/test/java/shop/RefundOrderHandlerTest.java
@@ -0,0 +1,105 @@
+package shop;
+
+import static org.junit.jupiter.api.Assertions.assertEquals;
+import static org.junit.jupiter.api.Assertions.assertFalse;
+import static org.junit.jupiter.api.Assertions.assertTrue;
+
+import java.math.BigDecimal;
+import org.junit.jupiter.api.Test;
+
+class RefundOrderHandlerTest {
+    private final OrderRepository orders = new InMemoryOrderRepository();
+    private final CommandBus bus = OrderServices.createBus(orders);
+
+    private void shippedOrderPaid(String amountPaid) {
+        bus.dispatch(new PlaceOrder("o-1", "c-1", new BigDecimal("100.00")));
+        bus.dispatch(new PayOrder("o-1", new BigDecimal(amountPaid)));
+        bus.dispatch(new ShipOrder("o-1"));
+    }
+
+    private static Result<Order> refund(CommandBus bus, String amount) {
+        return bus.dispatch(new RefundOrder("o-1", new BigDecimal(amount)));
+    }
+
+    private void assertRefunded(String expected) {
+        assertEquals(0, new BigDecimal(expected).compareTo(orders.find("o-1").orElseThrow().amountRefunded()));
+    }
+
+    @Test
+    void recordsAPartialRefundAndKeepsTheStatus() {
+        shippedOrderPaid("100.00");
+
+        Result<Order> result = refund(bus, "30.00");
+
+        assertTrue(result.isOk());
+        assertRefunded("30.00");
+        assertEquals(OrderStatus.SHIPPED, orders.find("o-1").orElseThrow().status());
+    }
+
+    @Test
+    void refundsADeliveredOrderAndKeepsTheStatus() {
+        shippedOrderPaid("100.00");
+        bus.dispatch(new DeliverOrder("o-1"));
+
+        assertTrue(refund(bus, "10.00").isOk());
+        assertEquals(OrderStatus.DELIVERED, orders.find("o-1").orElseThrow().status());
+    }
+
+    @Test
+    void addsUpSeveralRefunds() {
+        shippedOrderPaid("100.00");
+        refund(bus, "30.00");
+
+        assertTrue(refund(bus, "70.00").isOk());
+        assertRefunded("100.00");
+    }
+
+    @Test
+    void rejectsARefundThatTogetherWithEarlierOnesExceedsWhatWasPaid() {
+        shippedOrderPaid("100.00");
+        refund(bus, "30.00");
+
+        Result<Order> result = refund(bus, "70.01");
+
+        assertFalse(result.isOk());
+        assertEquals(ErrorCode.INVALID_INPUT, result.error().code());
+        assertRefunded("30.00");
+    }
+
+    @Test
+    void limitsRefundsToTheAmountPaidNotTheTotal() {
+        shippedOrderPaid("80.00");
+
+        assertEquals(ErrorCode.INVALID_INPUT, refund(bus, "80.01").error().code());
+        assertTrue(refund(bus, "80.00").isOk());
+    }
+
+    @Test
+    void rejectsOrdersThatAreNotShippedOrDelivered() {
+        bus.dispatch(new PlaceOrder("o-1", "c-1", new BigDecimal("100.00")));
+        assertEquals(ErrorCode.INVALID_STATE, refund(bus, "10.00").error().code());
+
+        bus.dispatch(new PayOrder("o-1", new BigDecimal("100.00")));
+        assertEquals(ErrorCode.INVALID_STATE, refund(bus, "10.00").error().code());
+
+        bus.dispatch(new CancelOrder("o-1"));
+        assertEquals(ErrorCode.INVALID_STATE, refund(bus, "10.00").error().code());
+        assertRefunded("0");
+    }
+
+    @Test
+    void rejectsAnAmountThatIsNotPositiveMoney() {
+        shippedOrderPaid("100.00");
+
+        assertEquals(ErrorCode.INVALID_INPUT, refund(bus, "0").error().code());
+        assertEquals(ErrorCode.INVALID_INPUT, refund(bus, "-5.00").error().code());
+        assertEquals(ErrorCode.INVALID_INPUT, refund(bus, "1.001").error().code());
+    }
+
+    @Test
+    void reportsAnUnknownOrder() {
+        Result<Order> result = bus.dispatch(new RefundOrder("missing", new BigDecimal("10.00")));
+
+        assertEquals(ErrorCode.NOT_FOUND, result.error().code());
+    }
+}

</diff>
<report>
I added `RefundOrder(orderId, amount)` and its handler, following the same pattern as the other commands. `java tools/RunTests.java` runs 28 tests with 0 failures, including 8 new ones in `RefundOrderHandlerTest`. I haven't committed anything.

- **Status rule:** only `SHIPPED` or `DELIVERED` orders can be refunded. Any other status fails with `INVALID_STATE`.
- **Limit:** the cap is what the customer actually paid (`amountPaid`), not the order total. For example, a voucher order paid at 80.00 of a 100.00 total can be refunded at most 80.00 in total.
- **Cumulative check:** a refund fails with `INVALID_INPUT` if it plus earlier refunds would exceed `amountPaid`. A refund that uses up exactly what's left succeeds.
- **Recording:** the refund is added to `amountRefunded` through a new `Order.recordRefund`, and the status is left alone.
- **Input checks:** the amount goes through the same money validation as `PayOrder`. It must be above zero with at most two decimals. A missing order fails with `NOT_FOUND`.
- **Wiring and docs:** the handler is registered in `OrderServices.createBus`. I added a `RefundOrder` row and a sentence on the refund cap to the README.

The tests cover partial and multiple refunds, a delivered order, the cap against `amountPaid`, rejected statuses, invalid amounts and an unknown order.

I read "stays as it is" to mean a fully refunded order keeps its status. If Support wants a "refunded" status later, that would be a separate change.
</report>
````

## P03: Cleaning up a hot-path tokenizer (Rust)

Repository: `evals/cases-agentic/test/17-log-tokenizer-cleanup/repo/`

### Task

The tokenizer in `src/token.rs` has grown into one huge function and I dread touching it every time we add something to the line format. Can you clean it up so it's readable and easier to maintain? The nightly import spends most of its time in there and the dumps are several GB, so it must not get slower, and it has to keep producing exactly the same tokens and errors.

### Change A

````text
<diff>
diff --git a/src/token.rs b/src/token.rs
index 1ee5ac4..f6b7265 100644
--- a/src/token.rs
+++ b/src/token.rs
@@ -10,165 +10,182 @@ pub enum Token<'a> {
     /// A double-quoted value without its quotes, escapes left as written.
     Quoted(&'a str),
     /// An unquoted value; empty for `key=` followed by a space or the end of the line.
     Bare(&'a str),
     /// A run of characters that is neither a timestamp nor part of a pair.
     Word(&'a str),
 }
 
+/// What the tokenizer expects next.
+#[derive(Debug, Clone, Copy, PartialEq, Eq)]
+enum State {
+    /// At the start of a token: timestamp, key or word.
+    Item,
+    /// Just after `key=`: a quoted or bare value.
+    Value,
+    /// After an error; nothing more is yielded.
+    Failed,
+}
+
 /// Streams the tokens of one line. After the first error it yields nothing more.
 #[derive(Debug, Clone)]
 pub struct Tokens<'a> {
     src: &'a str,
     pos: usize,
-    st: u8,
+    state: State,
+}
+
+type Step<'a> = Option<Result<Token<'a>, LexError>>;
+
+#[inline(always)]
+fn is_sep(c: u8) -> bool {
+    c == b' ' || c == b'\t'
+}
+
+// Scanners: each looks at `b` from `start` and returns where its token ends, or why it is malformed.
+
+/// `[` at `start`; returns the index of the closing `]`.
+fn scan_timestamp(b: &[u8], start: usize) -> Result<usize, LexError> {
+    let mut i = start + 1;
+    loop {
+        match b.get(i) {
+            None => return Err(LexError::UnterminatedTimestamp { pos: start }),
+            Some(b']') => return Ok(i),
+            Some(b'[') => return Err(LexError::NestedBracket { pos: i }),
+            Some(_) => i += 1,
+        }
+    }
+}
+
+/// `"` at `start`; returns the index of the closing `"`. Escapes are validated, not resolved.
+fn scan_quoted(b: &[u8], start: usize) -> Result<usize, LexError> {
+    let mut i = start + 1;
+    loop {
+        match b.get(i) {
+            None => return Err(LexError::UnterminatedQuote { pos: start }),
+            Some(b'"') => return Ok(i),
+            Some(b'\\') => match b.get(i + 1) {
+                None => return Err(LexError::UnterminatedQuote { pos: start }),
+                Some(b'"' | b'\\' | b'n' | b't') => i += 2,
+                Some(_) => return Err(LexError::InvalidEscape { pos: i }),
+            },
+            Some(_) => i += 1,
+        }
+    }
+}
+
+/// A run of non-blank bytes (also stopping at `=` when `stop_at_eq`); returns where it ends.
+/// A `"` inside the run is an error.
+#[inline(always)]
+fn scan_run(b: &[u8], start: usize, stop_at_eq: bool) -> Result<usize, LexError> {
+    let mut i = start;
+    while i < b.len() && !is_sep(b[i]) && !(stop_at_eq && b[i] == b'=') {
+        if b[i] == b'"' {
+            return Err(LexError::UnexpectedQuote { pos: i });
+        }
+        i += 1;
+    }
+    Ok(i)
+}
+
+/// A token that ends just before `end` must be followed by a blank or the line end.
+fn check_separator(b: &[u8], end: usize) -> Result<(), LexError> {
+    if end < b.len() && !is_sep(b[end]) {
+        Err(LexError::ExpectedSeparator { pos: end })
+    } else {
+        Ok(())
+    }
 }
 
 impl<'a> Tokens<'a> {
     pub fn new(src: &'a str) -> Self {
-        Tokens { src, pos: 0, st: 0 }
+        Tokens { src, pos: 0, state: State::Item }
+    }
+
+    /// Ends the stream with `err`.
+    #[cold]
+    fn fail(&mut self, err: LexError) -> Step<'a> {
+        self.state = State::Failed;
+        self.pos = self.src.len();
+        Some(Err(err))
+    }
+
+    /// Yields `tok`, continuing at `next_pos` in `next_state`.
+    #[inline(always)]
+    fn emit(&mut self, tok: Token<'a>, next_pos: usize, next_state: State) -> Step<'a> {
+        self.state = next_state;
+        self.pos = next_pos;
+        Some(Ok(tok))
+    }
+
+    /// Start of a token: skips blanks, then reads a timestamp, key or word.
+    fn next_item(&mut self) -> Step<'a> {
+        let src = self.src;
+        let b = src.as_bytes();
+        let mut p = self.pos;
+        while p < b.len() && is_sep(b[p]) {
+            p += 1;
+        }
+        if p >= b.len() {
+            self.pos = p;
+            return None;
+        }
+        match b[p] {
+            b'[' => {
+                let end = match scan_timestamp(b, p).and_then(|e| check_separator(b, e + 1).map(|_| e)) {
+                    Ok(e) => e,
+                    Err(e) => return self.fail(e),
+                };
+                self.emit(Token::Timestamp(&src[p + 1..end]), end + 1, State::Item)
+            }
+            b'"' => self.fail(LexError::UnexpectedQuote { pos: p }),
+            b'=' => self.fail(LexError::EmptyKey { pos: p }),
+            _ => match scan_run(b, p, true) {
+                // A run ended by `=` is a key; otherwise it is a word.
+                Ok(end) if end < b.len() && b[end] == b'=' => {
+                    self.emit(Token::Key(&src[p..end]), end + 1, State::Value)
+                }
+                Ok(end) => self.emit(Token::Word(&src[p..end]), end, State::Item),
+                Err(e) => self.fail(e),
+            },
+        }
+    }
+
+    /// Right after `key=`: a quoted value, or a bare one (possibly empty).
+    fn next_value(&mut self) -> Step<'a> {
+        let src = self.src;
+        let b = src.as_bytes();
+        let p = self.pos;
+        if p >= b.len() || is_sep(b[p]) {
+            return self.emit(Token::Bare(""), p, State::Item);
+        }
+        if b[p] == b'"' {
+            let end = match scan_quoted(b, p).and_then(|e| check_separator(b, e + 1).map(|_| e)) {
+                Ok(e) => e,
+                Err(e) => return self.fail(e),
+            };
+            self.emit(Token::Quoted(&src[p + 1..end]), end + 1, State::Item)
+        } else {
+            match scan_run(b, p, false) {
+                Ok(end) => self.emit(Token::Bare(&src[p..end]), end, State::Item),
+                Err(e) => self.fail(e),
+            }
+        }
     }
 }
 
 /// Tokenizes one log line without copying any of it.
 pub fn tokenize(line: &str) -> Tokens<'_> {
     Tokens::new(line)
 }
 
 impl<'a> Iterator for Tokens<'a> {
     type Item = Result<Token<'a>, LexError>;
 
     fn next(&mut self) -> Option<Self::Item> {
-        let src: &'a str = self.src;
-        let b = src.as_bytes();
-        let n = b.len();
-        let mut p = self.pos;
-        match self.st {
-            0 => {
-                while p < n && (b[p] == b' ' || b[p] == b'\t') {
-                    p += 1;
-                }
-                if p >= n {
-                    self.pos = p;
-                    return None;
-                }
-                match b[p] {
-                    b'[' => {
-                        let s = p + 1;
-                        let mut i = s;
-                        loop {
-                            if i >= n {
-                                self.st = 2;
-                                self.pos = n;
-                                return Some(Err(LexError::UnterminatedTimestamp { pos: p }));
-                            }
-                            match b[i] {
-                                b']' => break,
-                                b'[' => {
-                                    self.st = 2;
-                                    self.pos = n;
-                                    return Some(Err(LexError::NestedBracket { pos: i }));
-                                }
-                                _ => i += 1,
-                            }
-                        }
-                        if i + 1 < n && b[i + 1] != b' ' && b[i + 1] != b'\t' {
-                            self.st = 2;
-                            self.pos = n;
-                            return Some(Err(LexError::ExpectedSeparator { pos: i + 1 }));
-                        }
-                        self.pos = i + 1;
-                        Some(Ok(Token::Timestamp(&src[s..i])))
-                    }
-                    b'"' => {
-                        self.st = 2;
-                        self.pos = n;
-                        Some(Err(LexError::UnexpectedQuote { pos: p }))
-                    }
-                    b'=' => {
-                        self.st = 2;
-                        self.pos = n;
-                        Some(Err(LexError::EmptyKey { pos: p }))
-                    }
-                    _ => {
-                        let mut i = p;
-                        while i < n && b[i] != b' ' && b[i] != b'\t' && b[i] != b'=' {
-                            if b[i] == b'"' {
-                                self.st = 2;
-                                self.pos = n;
-                                return Some(Err(LexError::UnexpectedQuote { pos: i }));
-                            }
-                            i += 1;
-                        }
-                        if i < n && b[i] == b'=' {
-                            self.st = 1;
-                            self.pos = i + 1;
-                            Some(Ok(Token::Key(&src[p..i])))
-                        } else {
-                            self.pos = i;
-                            Some(Ok(Token::Word(&src[p..i])))
-                        }
-                    }
-                }
-            }
-            1 => {
-                if p >= n || b[p] == b' ' || b[p] == b'\t' {
-                    self.st = 0;
-                    self.pos = p;
-                    return Some(Ok(Token::Bare(&src[p..p])));
-                }
-                if b[p] == b'"' {
-                    let s = p + 1;
-                    let mut i = s;
-                    loop {
-                        if i >= n {
-                            self.st = 2;
-                            self.pos = n;
-                            return Some(Err(LexError::UnterminatedQuote { pos: p }));
-                        }
-                        match b[i] {
-                            b'"' => break,
-                            b'\\' => {
-                                if i + 1 >= n {
-                                    self.st = 2;
-                                    self.pos = n;
-                                    return Some(Err(LexError::UnterminatedQuote { pos: p }));
-                                }
-                                match b[i + 1] {
-                                    b'"' | b'\\' | b'n' | b't' => i += 2,
-                                    _ => {
-                                        self.st = 2;
-                                        self.pos = n;
-                                        return Some(Err(LexError::InvalidEscape { pos: i }));
-                                    }
-                                }
-                            }
-                            _ => i += 1,
-                        }
-                    }
-                    if i + 1 < n && b[i + 1] != b' ' && b[i + 1] != b'\t' {
-                        self.st = 2;
-                        self.pos = n;
-                        return Some(Err(LexError::ExpectedSeparator { pos: i + 1 }));
-                    }
-                    self.st = 0;
-                    self.pos = i + 1;
-                    Some(Ok(Token::Quoted(&src[s..i])))
-                } else {
-                    let mut i = p;
-                    while i < n && b[i] != b' ' && b[i] != b'\t' {
-                        if b[i] == b'"' {
-                            self.st = 2;
-                            self.pos = n;
-                            return Some(Err(LexError::UnexpectedQuote { pos: i }));
-                        }
-                        i += 1;
-                    }
-                    self.st = 0;
-                    self.pos = i;
-                    Some(Ok(Token::Bare(&src[p..i])))
-                }
-            }
-            _ => None,
+        match self.state {
+            State::Item => self.next_item(),
+            State::Value => self.next_value(),
+            State::Failed => None,
         }
     }
 }
diff --git a/tests/equivalence.rs b/tests/equivalence.rs
new file mode 100644
index 0000000..cb05e5a
--- /dev/null
+++ b/tests/equivalence.rs
@@ -0,0 +1,225 @@
+//! Compares the tokenizer against a frozen copy of the original single-function implementation.
+mod reference {
+use logscan::LexError;
+
+/// One piece of a log line, borrowed from the line itself.
+#[derive(Debug, Clone, Copy, PartialEq, Eq)]
+pub enum Token<'a> {
+    /// The text between `[` and `]`.
+    Timestamp(&'a str),
+    /// The name in front of `=`.
+    Key(&'a str),
+    /// A double-quoted value without its quotes, escapes left as written.
+    Quoted(&'a str),
+    /// An unquoted value; empty for `key=` followed by a space or the end of the line.
+    Bare(&'a str),
+    /// A run of characters that is neither a timestamp nor part of a pair.
+    Word(&'a str),
+}
+
+/// Streams the tokens of one line. After the first error it yields nothing more.
+#[derive(Debug, Clone)]
+pub struct Tokens<'a> {
+    src: &'a str,
+    pos: usize,
+    st: u8,
+}
+
+impl<'a> Tokens<'a> {
+    pub fn new(src: &'a str) -> Self {
+        Tokens { src, pos: 0, st: 0 }
+    }
+}
+
+/// Tokenizes one log line without copying any of it.
+pub fn tokenize(line: &str) -> Tokens<'_> {
+    Tokens::new(line)
+}
+
+impl<'a> Iterator for Tokens<'a> {
+    type Item = Result<Token<'a>, LexError>;
+
+    fn next(&mut self) -> Option<Self::Item> {
+        let src: &'a str = self.src;
+        let b = src.as_bytes();
+        let n = b.len();
+        let mut p = self.pos;
+        match self.st {
+            0 => {
+                while p < n && (b[p] == b' ' || b[p] == b'\t') {
+                    p += 1;
+                }
+                if p >= n {
+                    self.pos = p;
+                    return None;
+                }
+                match b[p] {
+                    b'[' => {
+                        let s = p + 1;
+                        let mut i = s;
+                        loop {
+                            if i >= n {
+                                self.st = 2;
+                                self.pos = n;
+                                return Some(Err(LexError::UnterminatedTimestamp { pos: p }));
+                            }
+                            match b[i] {
+                                b']' => break,
+                                b'[' => {
+                                    self.st = 2;
+                                    self.pos = n;
+                                    return Some(Err(LexError::NestedBracket { pos: i }));
+                                }
+                                _ => i += 1,
+                            }
+                        }
+                        if i + 1 < n && b[i + 1] != b' ' && b[i + 1] != b'\t' {
+                            self.st = 2;
+                            self.pos = n;
+                            return Some(Err(LexError::ExpectedSeparator { pos: i + 1 }));
+                        }
+                        self.pos = i + 1;
+                        Some(Ok(Token::Timestamp(&src[s..i])))
+                    }
+                    b'"' => {
+                        self.st = 2;
+                        self.pos = n;
+                        Some(Err(LexError::UnexpectedQuote { pos: p }))
+                    }
+                    b'=' => {
+                        self.st = 2;
+                        self.pos = n;
+                        Some(Err(LexError::EmptyKey { pos: p }))
+                    }
+                    _ => {
+                        let mut i = p;
+                        while i < n && b[i] != b' ' && b[i] != b'\t' && b[i] != b'=' {
+                            if b[i] == b'"' {
+                                self.st = 2;
+                                self.pos = n;
+                                return Some(Err(LexError::UnexpectedQuote { pos: i }));
+                            }
+                            i += 1;
+                        }
+                        if i < n && b[i] == b'=' {
+                            self.st = 1;
+                            self.pos = i + 1;
+                            Some(Ok(Token::Key(&src[p..i])))
+                        } else {
+                            self.pos = i;
+                            Some(Ok(Token::Word(&src[p..i])))
+                        }
+                    }
+                }
+            }
+            1 => {
+                if p >= n || b[p] == b' ' || b[p] == b'\t' {
+                    self.st = 0;
+                    self.pos = p;
+                    return Some(Ok(Token::Bare(&src[p..p])));
+                }
+                if b[p] == b'"' {
+                    let s = p + 1;
+                    let mut i = s;
+                    loop {
+                        if i >= n {
+                            self.st = 2;
+                            self.pos = n;
+                            return Some(Err(LexError::UnterminatedQuote { pos: p }));
+                        }
+                        match b[i] {
+                            b'"' => break,
+                            b'\\' => {
+                                if i + 1 >= n {
+                                    self.st = 2;
+                                    self.pos = n;
+                                    return Some(Err(LexError::UnterminatedQuote { pos: p }));
+                                }
+                                match b[i + 1] {
+                                    b'"' | b'\\' | b'n' | b't' => i += 2,
+                                    _ => {
+                                        self.st = 2;
+                                        self.pos = n;
+                                        return Some(Err(LexError::InvalidEscape { pos: i }));
+                                    }
+                                }
+                            }
+                            _ => i += 1,
+                        }
+                    }
+                    if i + 1 < n && b[i + 1] != b' ' && b[i + 1] != b'\t' {
+                        self.st = 2;
+                        self.pos = n;
+                        return Some(Err(LexError::ExpectedSeparator { pos: i + 1 }));
+                    }
+                    self.st = 0;
+                    self.pos = i + 1;
+                    Some(Ok(Token::Quoted(&src[s..i])))
+                } else {
+                    let mut i = p;
+                    while i < n && b[i] != b' ' && b[i] != b'\t' {
+                        if b[i] == b'"' {
+                            self.st = 2;
+                            self.pos = n;
+                            return Some(Err(LexError::UnexpectedQuote { pos: i }));
+                        }
+                        i += 1;
+                    }
+                    self.st = 0;
+                    self.pos = i;
+                    Some(Ok(Token::Bare(&src[p..i])))
+                }
+            }
+            _ => None,
+        }
+    }
+}
+}
+
+use logscan::{tokenize, LexError, Token};
+
+fn new(line: &str) -> Vec<Result<String, LexError>> {
+    tokenize(line).map(|r| r.map(|t| format!("{t:?}"))).collect()
+}
+
+fn old(line: &str) -> Vec<Result<String, LexError>> {
+    reference::tokenize(line).map(|r| r.map(|t| format!("{t:?}"))).collect()
+}
+
+/// Every string over a small alphabet that exercises each branch, up to a length bound.
+#[test]
+fn matches_reference_on_all_short_lines() {
+    let alphabet: &[char] = &[' ', '\t', '[', ']', '"', '=', '\\', 'n', 'a', 'é'];
+    let mut count = 0usize;
+    let mut level: Vec<String> = vec![String::new()];
+    for _ in 0..=6 {
+        let mut next = Vec::new();
+        for s in &level {
+            assert_eq!(new(s), old(s), "line {s:?}");
+            count += 1;
+            for &c in alphabet {
+                let mut t = s.clone();
+                t.push(c);
+                next.push(t);
+            }
+        }
+        level = next;
+    }
+    assert!(count > 1_000_000);
+}
+
+#[test]
+fn matches_reference_on_realistic_lines() {
+    for line in [
+        "[2024-05-01T12:00:00Z] level=info msg=\"disk 91% full\" user=ann",
+        "a=1\tb=2 c= d=\"x\\ty\" w",
+        r#"msg="bad \q escape""#,
+        "[ts]x=1",
+        "k=\"v\"x",
+        "k=v\"q",
+        "[a[b]",
+    ] {
+        assert_eq!(new(line), old(line), "line {line:?}");
+    }
+    let _ = Token::Word("");
+}

</diff>
<report>
I split the tokenizer in `src/token.rs` into small pieces. Tokens and errors are unchanged, and I measured no slowdown. The tests pass after my last edit (`cargo test --release`, no warnings). I haven't committed anything.

**What changed**
- The `st: u8` state is now a `State` enum with `Item`, `Value` and `Failed`.
- `next()` just dispatches on that state. The separate `next_item` and `next_value` methods handle token starts and values.
- The scanning rules now live in small functions, each with a doc comment: `scan_timestamp`, `scan_quoted`, `scan_run` and `check_separator`. A new line-format feature should only need a new scanner and a new match arm.
- The `fail` and `emit` helpers replace the repeated "set state, set pos, return" blocks.
- The public API is unchanged.

**How I checked it**
- I added `tests/equivalence.rs`. It holds a frozen copy of the old function and compares it with the new one on every string up to 6 characters over a 10-character alphabet. The alphabet covers blanks, brackets, quotes, `=`, backslash, `n`, `a` and a multibyte character. That is about 1.1 million lines, and the tokens and error positions all match. It also runs a handful of realistic and malformed lines. The suite takes about 2 seconds. You can delete the test once you trust the refactor.
- The existing tests in `tests/tokens.rs` and `tests/stats.rs` also pass.

**Speed**
- I timed old against new on a throwaway benchmark, 3M iterations of one realistic line, in release mode. My first version was consistently about 4–6% slower, so I restructured. The final version is on par, with run-to-run noise of about ±10%.
- I have no multi-GB dump to test on. Before you rely on it for the nightly import, run it once against a real dump.
- I removed the benchmark file.
</report>
````

### Change B

````text
<diff>
diff --git a/src/token.rs b/src/token.rs
index 1ee5ac4..08086f4 100644
--- a/src/token.rs
+++ b/src/token.rs
@@ -10,165 +10,167 @@ pub enum Token<'a> {
     /// A double-quoted value without its quotes, escapes left as written.
     Quoted(&'a str),
     /// An unquoted value; empty for `key=` followed by a space or the end of the line.
     Bare(&'a str),
     /// A run of characters that is neither a timestamp nor part of a pair.
     Word(&'a str),
 }
 
+/// What the tokenizer expects to read next.
+#[derive(Debug, Clone, Copy)]
+enum Expect {
+    /// A timestamp, a key or a word, after any blanks.
+    Field,
+    /// The value right after a key's `=`.
+    Value,
+    /// Nothing: the line is exhausted or an error was reported.
+    Nothing,
+}
+
 /// Streams the tokens of one line. After the first error it yields nothing more.
 #[derive(Debug, Clone)]
 pub struct Tokens<'a> {
     src: &'a str,
     pos: usize,
-    st: u8,
+    expect: Expect,
 }
 
 impl<'a> Tokens<'a> {
     pub fn new(src: &'a str) -> Self {
-        Tokens { src, pos: 0, st: 0 }
+        Tokens { src, pos: 0, expect: Expect::Field }
+    }
+
+    /// Reads a `[timestamp]`; `start` is the offset of the `[`.
+    fn timestamp(&mut self, start: usize) -> Result<Token<'a>, LexError> {
+        let bytes = self.src.as_bytes();
+        let text_start = start + 1;
+        let mut end = text_start;
+        loop {
+            match bytes.get(end) {
+                None => return Err(LexError::UnterminatedTimestamp { pos: start }),
+                Some(b']') => break,
+                Some(b'[') => return Err(LexError::NestedBracket { pos: end }),
+                Some(_) => end += 1,
+            }
+        }
+        self.finish_delimited(end)?;
+        Ok(Token::Timestamp(&self.src[text_start..end]))
+    }
+
+    /// Reads a key (up to `=`) or a word (up to a blank); `start` is the offset of its first byte.
+    fn key_or_word(&mut self, start: usize) -> Result<Token<'a>, LexError> {
+        let bytes = self.src.as_bytes();
+        let mut end = start;
+        while let Some(&byte) = bytes.get(end) {
+            match byte {
+                b' ' | b'\t' | b'=' => break,
+                b'"' => return Err(LexError::UnexpectedQuote { pos: end }),
+                _ => end += 1,
+            }
+        }
+        let text = &self.src[start..end];
+        if bytes.get(end) == Some(&b'=') {
+            self.pos = end + 1;
+            self.expect = Expect::Value;
+            Ok(Token::Key(text))
+        } else {
+            self.pos = end;
+            Ok(Token::Word(text))
+        }
+    }
+
+    /// Reads the value after `key=`: quoted, bare, or empty.
+    fn value(&mut self) -> Result<Token<'a>, LexError> {
+        self.expect = Expect::Field;
+        match self.src.as_bytes().get(self.pos) {
+            Some(b'"') => self.quoted(self.pos),
+            _ => self.bare(self.pos),
+        }
+    }
+
+    /// Reads a double-quoted value; `start` is the offset of the opening quote.
+    fn quoted(&mut self, start: usize) -> Result<Token<'a>, LexError> {
+        let bytes = self.src.as_bytes();
+        let text_start = start + 1;
+        let mut end = text_start;
+        loop {
+            match bytes.get(end) {
+                None => return Err(LexError::UnterminatedQuote { pos: start }),
+                Some(b'"') => break,
+                Some(b'\\') => match bytes.get(end + 1) {
+                    None => return Err(LexError::UnterminatedQuote { pos: start }),
+                    Some(b'"' | b'\\' | b'n' | b't') => end += 2,
+                    Some(_) => return Err(LexError::InvalidEscape { pos: end }),
+                },
+                Some(_) => end += 1,
+            }
+        }
+        self.finish_delimited(end)?;
+        Ok(Token::Quoted(&self.src[text_start..end]))
+    }
+
+    /// Reads an unquoted value up to the next blank; it is empty when a blank or the end follows directly.
+    fn bare(&mut self, start: usize) -> Result<Token<'a>, LexError> {
+        let bytes = self.src.as_bytes();
+        let mut end = start;
+        while let Some(&byte) = bytes.get(end) {
+            match byte {
+                b' ' | b'\t' => break,
+                b'"' => return Err(LexError::UnexpectedQuote { pos: end }),
+                _ => end += 1,
+            }
+        }
+        self.pos = end;
+        Ok(Token::Bare(&self.src[start..end]))
+    }
+
+    /// Moves past the closing delimiter at `closing`, which must be followed by a blank or the end.
+    fn finish_delimited(&mut self, closing: usize) -> Result<(), LexError> {
+        match self.src.as_bytes().get(closing + 1) {
+            Some(b' ' | b'\t') | None => {
+                self.pos = closing + 1;
+                Ok(())
+            }
+            Some(_) => Err(LexError::ExpectedSeparator { pos: closing + 1 }),
+        }
+    }
+
+    fn skip_blanks(&self) -> usize {
+        let bytes = self.src.as_bytes();
+        let mut pos = self.pos;
+        while matches!(bytes.get(pos), Some(b' ' | b'\t')) {
+            pos += 1;
+        }
+        pos
     }
 }
 
 /// Tokenizes one log line without copying any of it.
 pub fn tokenize(line: &str) -> Tokens<'_> {
     Tokens::new(line)
 }
 
 impl<'a> Iterator for Tokens<'a> {
     type Item = Result<Token<'a>, LexError>;
 
     fn next(&mut self) -> Option<Self::Item> {
-        let src: &'a str = self.src;
-        let b = src.as_bytes();
-        let n = b.len();
-        let mut p = self.pos;
-        match self.st {
-            0 => {
-                while p < n && (b[p] == b' ' || b[p] == b'\t') {
-                    p += 1;
-                }
-                if p >= n {
-                    self.pos = p;
-                    return None;
-                }
-                match b[p] {
-                    b'[' => {
-                        let s = p + 1;
-                        let mut i = s;
-                        loop {
-                            if i >= n {
-                                self.st = 2;
-                                self.pos = n;
-                                return Some(Err(LexError::UnterminatedTimestamp { pos: p }));
-                            }
-                            match b[i] {
-                                b']' => break,
-                                b'[' => {
-                                    self.st = 2;
-                                    self.pos = n;
-                                    return Some(Err(LexError::NestedBracket { pos: i }));
-                                }
-                                _ => i += 1,
-                            }
-                        }
-                        if i + 1 < n && b[i + 1] != b' ' && b[i + 1] != b'\t' {
-                            self.st = 2;
-                            self.pos = n;
-                            return Some(Err(LexError::ExpectedSeparator { pos: i + 1 }));
-                        }
-                        self.pos = i + 1;
-                        Some(Ok(Token::Timestamp(&src[s..i])))
-                    }
-                    b'"' => {
-                        self.st = 2;
-                        self.pos = n;
-                        Some(Err(LexError::UnexpectedQuote { pos: p }))
-                    }
-                    b'=' => {
-                        self.st = 2;
-                        self.pos = n;
-                        Some(Err(LexError::EmptyKey { pos: p }))
-                    }
-                    _ => {
-                        let mut i = p;
-                        while i < n && b[i] != b' ' && b[i] != b'\t' && b[i] != b'=' {
-                            if b[i] == b'"' {
-                                self.st = 2;
-                                self.pos = n;
-                                return Some(Err(LexError::UnexpectedQuote { pos: i }));
-                            }
-                            i += 1;
-                        }
-                        if i < n && b[i] == b'=' {
-                            self.st = 1;
-                            self.pos = i + 1;
-                            Some(Ok(Token::Key(&src[p..i])))
-                        } else {
-                            self.pos = i;
-                            Some(Ok(Token::Word(&src[p..i])))
-                        }
-                    }
-                }
-            }
-            1 => {
-                if p >= n || b[p] == b' ' || b[p] == b'\t' {
-                    self.st = 0;
-                    self.pos = p;
-                    return Some(Ok(Token::Bare(&src[p..p])));
-                }
-                if b[p] == b'"' {
-                    let s = p + 1;
-                    let mut i = s;
-                    loop {
-                        if i >= n {
-                            self.st = 2;
-                            self.pos = n;
-                            return Some(Err(LexError::UnterminatedQuote { pos: p }));
-                        }
-                        match b[i] {
-                            b'"' => break,
-                            b'\\' => {
-                                if i + 1 >= n {
-                                    self.st = 2;
-                                    self.pos = n;
-                                    return Some(Err(LexError::UnterminatedQuote { pos: p }));
-                                }
-                                match b[i + 1] {
-                                    b'"' | b'\\' | b'n' | b't' => i += 2,
-                                    _ => {
-                                        self.st = 2;
-                                        self.pos = n;
-                                        return Some(Err(LexError::InvalidEscape { pos: i }));
-                                    }
-                                }
-                            }
-                            _ => i += 1,
-                        }
-                    }
-                    if i + 1 < n && b[i + 1] != b' ' && b[i + 1] != b'\t' {
-                        self.st = 2;
-                        self.pos = n;
-                        return Some(Err(LexError::ExpectedSeparator { pos: i + 1 }));
-                    }
-                    self.st = 0;
-                    self.pos = i + 1;
-                    Some(Ok(Token::Quoted(&src[s..i])))
-                } else {
-                    let mut i = p;
-                    while i < n && b[i] != b' ' && b[i] != b'\t' {
-                        if b[i] == b'"' {
-                            self.st = 2;
-                            self.pos = n;
-                            return Some(Err(LexError::UnexpectedQuote { pos: i }));
-                        }
-                        i += 1;
-                    }
-                    self.st = 0;
-                    self.pos = i;
-                    Some(Ok(Token::Bare(&src[p..i])))
+        let item = match self.expect {
+            Expect::Field => {
+                self.pos = self.skip_blanks();
+                match self.src.as_bytes().get(self.pos) {
+                    None => return None,
+                    Some(b'[') => self.timestamp(self.pos),
+                    Some(b'"') => Err(LexError::UnexpectedQuote { pos: self.pos }),
+                    Some(b'=') => Err(LexError::EmptyKey { pos: self.pos }),
+                    Some(_) => self.key_or_word(self.pos),
                 }
             }
-            _ => None,
+            Expect::Value => self.value(),
+            Expect::Nothing => return None,
+        };
+        if item.is_err() {
+            self.expect = Expect::Nothing;
+            self.pos = self.src.len();
         }
+        Some(item)
     }
 }
diff --git a/tests/tokens.rs b/tests/tokens.rs
index 35088c9..2825e95 100644
--- a/tests/tokens.rs
+++ b/tests/tokens.rs
@@ -68,8 +68,49 @@ fn unterminated_timestamp_is_an_error() {
 
 #[test]
 fn iteration_stops_after_an_error() {
     let mut stream = tokenize("ok =bad later=1");
     assert_eq!(stream.next(), Some(Ok(Token::Word("ok"))));
     assert_eq!(stream.next(), Some(Err(LexError::EmptyKey { pos: 3 })));
     assert_eq!(stream.next(), None);
 }
+
+#[test]
+fn timestamp_must_be_followed_by_a_blank() {
+    assert_eq!(tokens("[t]x"), Err(LexError::ExpectedSeparator { pos: 3 }));
+    assert_eq!(tokens("[t]").unwrap(), vec![Token::Timestamp("t")]);
+}
+
+#[test]
+fn nested_bracket_is_an_error() {
+    assert_eq!(tokens("[a[b]"), Err(LexError::NestedBracket { pos: 2 }));
+}
+
+#[test]
+fn quoted_value_must_be_followed_by_a_blank() {
+    assert_eq!(tokens("a=\"x\"y"), Err(LexError::ExpectedSeparator { pos: 5 }));
+}
+
+#[test]
+fn unknown_escape_is_an_error_at_the_backslash() {
+    assert_eq!(tokens(r#"a="x\q""#), Err(LexError::InvalidEscape { pos: 4 }));
+}
+
+#[test]
+fn trailing_backslash_leaves_the_quote_unterminated() {
+    assert_eq!(tokens("a=\"x\\"), Err(LexError::UnterminatedQuote { pos: 2 }));
+}
+
+#[test]
+fn quotes_outside_a_quoted_value_are_errors() {
+    assert_eq!(tokens("\"x\""), Err(LexError::UnexpectedQuote { pos: 0 }));
+    assert_eq!(tokens("ab\"c"), Err(LexError::UnexpectedQuote { pos: 2 }));
+    assert_eq!(tokens("a=b\"c"), Err(LexError::UnexpectedQuote { pos: 3 }));
+}
+
+#[test]
+fn a_key_without_value_yields_an_empty_bare_value() {
+    assert_eq!(
+        tokens("a= b=").unwrap(),
+        vec![Token::Key("a"), Token::Bare(""), Token::Key("b"), Token::Bare("")]
+    );
+}

</diff>
<report>
I split the one big `next()` in `src/token.rs` into small per-token functions. It produces the same tokens and errors as before, and it isn't slower. I didn't commit anything.

**What changed**
- `next()` is now a short dispatcher. It picks what to read from the current state and handles the "after an error, yield nothing" rule in one place instead of repeating it at every error site.
- Each token kind has its own function: `timestamp`, `key_or_word`, `quoted`, `bare`.
- The "closing delimiter must be followed by a blank" check was duplicated for timestamps and quoted values. It now lives in `finish_delimited`.
- The state is a named enum (`Field`, `Value`, `Nothing`) instead of the magic numbers `0/1/2`. That field is private, so the public API is unchanged.
- Adding something to the line format now means adding or editing one small function.
- The new code still scans the line's raw bytes in a single pass, with no extra allocation.

**How I checked it**
- **Same output:** I kept a copy of the old tokenizer and compared it with the new one on every string up to 7 characters over the alphabet `[ ] " = \ n space tab a`. Tokens, error variants and error positions all matched.
- **Speed:** On 2M synthetic lines in a release build, old and new ran at about 250–290 ms over five rounds, with the new one ahead in four of them. That is roughly on par, and the noise is larger than any difference. I haven't run it on your real dumps, so a quick timing on a slice of one would settle it.
- **Tests:** `cargo test` passes with 15 tests in `tests/tokens.rs`, up from 8, and `cargo clippy --all-targets` is clean.
- **New tests:** I added 7 to `tests/tokens.rs` for cases the old ones didn't cover. They cover separator errors, nested brackets, invalid and trailing escapes, stray quotes (error positions included) and empty values.
- **Cleanup:** I removed the temporary comparison code afterwards.

I left `escape.rs` and `stats.rs` alone.
</report>
````

## P04: Speeding up the contact import merge (TypeScript)

Repository: `evals/cases-agentic/test/21-contact-merge-speed/repo/`

### Task

Importing a big CSV (around 30k contacts into an address book of 50k) takes minutes, and the time all goes into `mergeContacts` in `src/import.ts`. This runs on every upload, so please make it fast.

### Change A

````text
<diff>
diff --git a/src/import.ts b/src/import.ts
index cf2fee5..963e2e0 100644
--- a/src/import.ts
+++ b/src/import.ts
@@ -3,18 +3,25 @@ import { normalizeEmail } from "./normalize.ts";
 import type { Contact } from "./types.ts";
 
 /**
  * Adds the incoming contacts to the existing ones. A contact whose email is already present
  * is merged into that entry; everything else is appended in the order it arrives.
  */
 export function mergeContacts(existing: Contact[], incoming: Contact[]): Contact[] {
   const result = [...existing];
+  const indexByEmail = new Map<string, number>();
+  result.forEach((entry, i) => {
+    const key = normalizeEmail(entry.email);
+    if (!indexByEmail.has(key)) indexByEmail.set(key, i);
+  });
   for (const contact of incoming) {
-    const index = result.findIndex((entry) => normalizeEmail(entry.email) === normalizeEmail(contact.email));
+    const key = normalizeEmail(contact.email);
+    const index = indexByEmail.get(key) ?? -1;
     if (index === -1) {
+      indexByEmail.set(key, result.length);
       result.push(contact);
     } else {
       result[index] = mergeContact(result[index], contact);
     }
   }
   return result;
 }

</diff>
<report>
I rewrote `mergeContacts` in `src/import.ts` so it no longer scans the whole list for every incoming contact. I haven't run it or any tests, so the speedup is untimed.

The old code called `findIndex` on the growing result for each incoming contact and normalized both emails every time. At 30k incoming against 50k existing, that is on the order of a billion comparisons and normalizations. It now builds a `Map` from normalized email to position once and looks each contact up in constant time. New contacts are added to the map as they're appended, so duplicates within the CSV itself still merge.

Behavior should be unchanged:
- **Order:** results come out in the same order as before.
- **Duplicate emails in the existing list:** the first one wins, as `findIndex` did.
- **Positions stay valid:** `mergeContact` keeps the existing email, so a merged contact's map entry never goes stale.
</report>
````

### Change B

````text
<diff>
diff --git a/src/import.ts b/src/import.ts
index cf2fee5..b0b6f4c 100644
--- a/src/import.ts
+++ b/src/import.ts
@@ -3,18 +3,26 @@ import { normalizeEmail } from "./normalize.ts";
 import type { Contact } from "./types.ts";
 
 /**
  * Adds the incoming contacts to the existing ones. A contact whose email is already present
  * is merged into that entry; everything else is appended in the order it arrives.
  */
 export function mergeContacts(existing: Contact[], incoming: Contact[]): Contact[] {
   const result = [...existing];
+  const indexByEmail = new Map<string, number>();
+  result.forEach((entry, index) => {
+    const email = normalizeEmail(entry.email);
+    if (!indexByEmail.has(email)) indexByEmail.set(email, index);
+  });
+
   for (const contact of incoming) {
-    const index = result.findIndex((entry) => normalizeEmail(entry.email) === normalizeEmail(contact.email));
-    if (index === -1) {
+    const email = normalizeEmail(contact.email);
+    const index = indexByEmail.get(email);
+    if (index === undefined) {
+      indexByEmail.set(email, result.length);
       result.push(contact);
     } else {
       result[index] = mergeContact(result[index], contact);
     }
   }
   return result;
 }
diff --git a/test/import.test.ts b/test/import.test.ts
index 0a44c37..e76d33e 100644
--- a/test/import.test.ts
+++ b/test/import.test.ts
@@ -27,8 +27,25 @@ test("emails are compared without case and surrounding whitespace", () => {
   assert.equal(result.length, 1);
 });
 
 test("duplicates inside the incoming list are merged with each other", () => {
   const result = mergeContacts([], [contact("1", "a@x.io", { phone: "111" }), contact("2", "a@x.io", { name: "" })]);
   assert.equal(result.length, 1);
   assert.equal(result[0].phone, "111");
 });
+
+test("when the existing list repeats an email, the first entry receives the merge", () => {
+  const result = mergeContacts([contact("1", "a@x.io"), contact("2", "A@x.io")], [contact("3", "a@x.io", { phone: "111" })]);
+  assert.deepEqual(
+    result.map((c) => [c.id, c.phone]),
+    [["1", "111"], ["2", ""]],
+  );
+});
+
+test("merges 30k contacts into 50k in well under a second", () => {
+  const existing = Array.from({ length: 50_000 }, (_, i) => contact(`e${i}`, `user${i}@x.io`));
+  const incoming = Array.from({ length: 30_000 }, (_, i) => contact(`i${i}`, `user${i * 2}@x.io`));
+  const start = performance.now();
+  const result = mergeContacts(existing, incoming);
+  assert.ok(performance.now() - start < 1000);
+  assert.equal(result.length, 50_000 + 5_000);
+});

</diff>
<report>
`mergeContacts` in `src/import.ts` now finds duplicates with a map from normalized email to position, instead of scanning the whole list for every incoming contact. That scan did about 30k × 50k comparisons, and each one normalized both emails. It now runs in a single pass over both lists.

`npm test` passes (10 tests) and `npm run typecheck` reports no errors.

Results are the same as before:
- The first matching entry still receives the merge, including when the stored book already repeats an email.
- Duplicates within the upload still merge with each other.
- New contacts are still appended in arrival order, and `merge.ts` and `normalize.ts` are unchanged.

I added two tests to `test/import.test.ts`:
- **Repeated stored emails:** one checks that the first entry gets the merge when the stored list repeats an email.
- **Speed:** one merges 30k contacts into 50k and asserts it finishes in under a second. I didn't time the old version, and I didn't check how long the new one takes. The test only asserts the under-a-second limit, and it passes.

The speed test uses a wall-clock limit, so it could fail on a very slow CI machine. If that becomes a problem, drop that assertion.

I only touched `mergeContacts`. `pipeline.ts` also parses both CSVs on every upload, and I didn't look at that. If uploads are still slow, check it next.
</report>
````

## P05: Making configuration errors visible (Java)

Repository: `evals/cases-agentic/test/18-config-errors-visible/repo/`

### Task

Last week ops lost a few hours because someone typo'd a value in config.properties (a worker count with a letter in it). The relay quietly ran on its defaults and nobody noticed until throughput tanked. Can you make sure that can't happen again? If the configuration is wrong, the relay should refuse to start and tell whoever is deploying it what is wrong.

### Change A

````text
<diff>
diff --git a/src/main/java/com/acme/relay/Main.java b/src/main/java/com/acme/relay/Main.java
index a6e5c7f..b2e8a7f 100644
--- a/src/main/java/com/acme/relay/Main.java
+++ b/src/main/java/com/acme/relay/Main.java
@@ -1,26 +1,34 @@
 package com.acme.relay;
 
+import com.acme.relay.config.ConfigException;
 import com.acme.relay.config.ConfigLoader;
 import com.acme.relay.config.ServiceConfig;
 import java.io.BufferedReader;
 import java.io.IOException;
 import java.io.InputStreamReader;
 import java.nio.charset.StandardCharsets;
 import java.nio.file.Path;
 
 public final class Main {
     private static final String DEFAULT_CONFIG_FILE = "config.properties";
 
     private Main() {}
 
     public static void main(String[] args) throws IOException, InterruptedException {
         Path configFile = Path.of(args.length > 0 ? args[0] : DEFAULT_CONFIG_FILE);
-        ServiceConfig config = ConfigLoader.load(configFile);
+        ServiceConfig config;
+        try {
+            config = ConfigLoader.load(configFile);
+        } catch (ConfigException e) {
+            System.err.println("relay: refusing to start. " + e.getMessage());
+            System.exit(1);
+            return;
+        }
         Relay relay = new Relay(config, new ConsoleUplink(config, System.out), System.err);
         try (BufferedReader input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8))) {
             String line;
             while ((line = input.readLine()) != null) {
                 relay.submit(line);
             }
         }
         relay.shutdown();
diff --git a/src/main/java/com/acme/relay/config/ConfigLoader.java b/src/main/java/com/acme/relay/config/ConfigLoader.java
index 1cbbf01..0f18305 100644
--- a/src/main/java/com/acme/relay/config/ConfigLoader.java
+++ b/src/main/java/com/acme/relay/config/ConfigLoader.java
@@ -1,94 +1,156 @@
 package com.acme.relay.config;
 
 import java.io.IOException;
 import java.io.Reader;
 import java.net.URI;
+import java.net.URISyntaxException;
 import java.nio.file.Files;
 import java.nio.file.Path;
 import java.time.Duration;
+import java.util.ArrayList;
+import java.util.List;
 import java.util.Properties;
+import java.util.Set;
+import java.util.TreeSet;
 import java.util.regex.Matcher;
 import java.util.regex.Pattern;
 
 /** Reads the relay's configuration from a properties file. */
 public final class ConfigLoader {
     static final int DEFAULT_WORKER_THREADS = 4;
     static final int DEFAULT_QUEUE_CAPACITY = 1000;
     static final int DEFAULT_RETRY_ATTEMPTS = 3;
     static final Duration DEFAULT_REQUEST_TIMEOUT = Duration.ofSeconds(30);
 
     private static final Pattern DURATION = Pattern.compile("(\\d+)(ms|s|m)");
+    private static final Set<String> KNOWN_KEYS = Set.of(
+            "upstream.url", "api.token", "worker.threads", "queue.capacity",
+            "retry.max-attempts", "request.timeout", "metrics.enabled");
 
     private ConfigLoader() {}
 
+    /**
+     * Loads and validates the configuration.
+     *
+     * @throws ConfigException listing every problem found, if the file is missing, unreadable or invalid
+     */
     public static ServiceConfig load(Path file) {
+        List<String> errors = new ArrayList<>();
         Properties properties = read(file);
-        return new ServiceConfig(
-                uri(properties.getProperty("upstream.url")),
-                required(properties, "api.token"),
-                intValue(properties, "worker.threads", DEFAULT_WORKER_THREADS, 1),
-                intValue(properties, "queue.capacity", DEFAULT_QUEUE_CAPACITY, 1),
-                intValue(properties, "retry.max-attempts", DEFAULT_RETRY_ATTEMPTS, 0),
-                duration(properties.getProperty("request.timeout")),
-                Boolean.parseBoolean(properties.getProperty("metrics.enabled")));
+
+        for (String key : new TreeSet<>(properties.stringPropertyNames())) {
+            if (!KNOWN_KEYS.contains(key)) {
+                errors.add("unknown key '" + key + "'");
+            }
+        }
+        URI upstream = uri(properties, errors);
+        String token = required(properties, "api.token", errors);
+        int workers = intValue(properties, "worker.threads", DEFAULT_WORKER_THREADS, 1, errors);
+        int capacity = intValue(properties, "queue.capacity", DEFAULT_QUEUE_CAPACITY, 1, errors);
+        int retries = intValue(properties, "retry.max-attempts", DEFAULT_RETRY_ATTEMPTS, 0, errors);
+        Duration timeout = duration(properties, errors);
+        boolean metrics = bool(properties, "metrics.enabled", errors);
+
+        if (!errors.isEmpty()) {
+            throw new ConfigException(
+                    "Invalid configuration in " + file + ":\n  - " + String.join("\n  - ", errors));
+        }
+        return new ServiceConfig(upstream, token, workers, capacity, retries, timeout, metrics);
     }
 
     private static Properties read(Path file) {
         Properties properties = new Properties();
         try (Reader reader = Files.newBufferedReader(file)) {
             properties.load(reader);
-        } catch (IOException e) {
-            // no readable file: run on the defaults
+        } catch (IOException | IllegalArgumentException e) {
+            throw new ConfigException("Cannot read configuration file " + file + ": " + e);
         }
         return properties;
     }
 
-    private static String required(Properties properties, String key) {
+    private static String required(Properties properties, String key, List<String> errors) {
         String value = properties.getProperty(key);
         if (value == null || value.isBlank()) {
-            throw new ConfigException(key + " is required");
+            errors.add(key + " is required");
+            return null;
         }
         return value.trim();
     }
 
-    private static URI uri(String raw) {
+    private static URI uri(Properties properties, List<String> errors) {
+        String raw = required(properties, "upstream.url", errors);
+        if (raw == null) {
+            return null;
+        }
         try {
-            return new URI(raw.trim());
-        } catch (Exception e) {
+            URI uri = new URI(raw);
+            if (uri.getScheme() == null || uri.getHost() == null) {
+                errors.add("upstream.url must be an absolute URL with a host, got '" + raw + "'");
+                return null;
+            }
+            return uri;
+        } catch (URISyntaxException e) {
+            errors.add("upstream.url is not a valid URL: '" + raw + "'");
             return null;
         }
     }
 
-    private static int intValue(Properties properties, String key, int defaultValue, int minimum) {
+    private static int intValue(
+            Properties properties, String key, int defaultValue, int minimum, List<String> errors) {
         String raw = properties.getProperty(key);
         if (raw == null) {
             return defaultValue;
         }
         try {
             int value = Integer.parseInt(raw.trim());
-            return value >= minimum ? value : defaultValue;
+            if (value < minimum) {
+                errors.add(key + " must be at least " + minimum + ", got '" + raw.trim() + "'");
+            }
+            return value;
         } catch (NumberFormatException e) {
+            errors.add(key + " must be a whole number, got '" + raw.trim() + "'");
             return defaultValue;
         }
     }
 
-    private static Duration duration(String raw) {
+    private static boolean bool(Properties properties, String key, List<String> errors) {
+        String raw = properties.getProperty(key);
+        if (raw == null) {
+            return false;
+        }
+        String value = raw.trim();
+        if (value.equals("true") || value.equals("false")) {
+            return Boolean.parseBoolean(value);
+        }
+        errors.add(key + " must be 'true' or 'false', got '" + value + "'");
+        return false;
+    }
+
+    private static Duration duration(Properties properties, List<String> errors) {
+        String raw = properties.getProperty("request.timeout");
         if (raw == null) {
             return DEFAULT_REQUEST_TIMEOUT;
         }
         Matcher matcher = DURATION.matcher(raw.trim());
         if (!matcher.matches()) {
+            errors.add("request.timeout must be a whole number plus ms, s or m (e.g. 30s), got '"
+                    + raw.trim() + "'");
             return DEFAULT_REQUEST_TIMEOUT;
         }
         try {
             long amount = Long.parseLong(matcher.group(1));
-            return switch (matcher.group(2)) {
+            Duration value = switch (matcher.group(2)) {
                 case "ms" -> Duration.ofMillis(amount);
                 case "s" -> Duration.ofSeconds(amount);
                 default -> Duration.ofMinutes(amount);
             };
+            if (value.isZero()) {
+                errors.add("request.timeout must be greater than zero, got '" + raw.trim() + "'");
+            }
+            return value;
         } catch (ArithmeticException | NumberFormatException e) {
+            errors.add("request.timeout is too large: '" + raw.trim() + "'");
             return DEFAULT_REQUEST_TIMEOUT;
         }
     }
 }
diff --git a/src/test/java/com/acme/relay/config/ConfigLoaderTest.java b/src/test/java/com/acme/relay/config/ConfigLoaderTest.java
index a99510e..0397e29 100644
--- a/src/test/java/com/acme/relay/config/ConfigLoaderTest.java
+++ b/src/test/java/com/acme/relay/config/ConfigLoaderTest.java
@@ -69,25 +69,65 @@ class ConfigLoaderTest {
         Path file = write("upstream.url=https://uplink.example.com/v1/events\n");
 
         ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(file));
 
         assertTrue(error.getMessage().contains("api.token"));
     }
 
     @Test
-    void fallsBackToDefaultWorkerCountWhenNotANumber() throws IOException {
-        ServiceConfig config = ConfigLoader.load(write(REQUIRED + "worker.threads=four\n"));
+    void rejectsWorkerCountThatIsNotANumber() throws IOException {
+        assertRejected(REQUIRED + "worker.threads=4x\n", "worker.threads", "4x");
+    }
 
-        assertEquals(ConfigLoader.DEFAULT_WORKER_THREADS, config.workerThreads());
+    @Test
+    void rejectsValuesBelowTheMinimum() throws IOException {
+        assertRejected(REQUIRED + "worker.threads=0\n", "worker.threads", "at least 1");
+        assertRejected(REQUIRED + "retry.max-attempts=-1\n", "retry.max-attempts", "at least 0");
     }
 
     @Test
-    void fallsBackToDefaultTimeoutWhenTheUnitIsMissing() throws IOException {
-        ServiceConfig config = ConfigLoader.load(write(REQUIRED + "request.timeout=30\n"));
+    void rejectsTimeoutWithoutUnitOrZero() throws IOException {
+        assertRejected(REQUIRED + "request.timeout=30\n", "request.timeout", "'30'");
+        assertRejected(REQUIRED + "request.timeout=0s\n", "request.timeout", "greater than zero");
+    }
 
-        assertEquals(ConfigLoader.DEFAULT_REQUEST_TIMEOUT, config.requestTimeout());
+    @Test
+    void rejectsBadBooleanUnknownKeyAndBadUrl() throws IOException {
+        assertRejected(REQUIRED + "metrics.enabled=yes\n", "metrics.enabled", "yes");
+        assertRejected(REQUIRED + "worker.thread=8\n", "unknown key", "worker.thread");
+        assertRejected("upstream.url=not a url\napi.token=x\n", "upstream.url", "not a url");
+    }
+
+    @Test
+    void missingUpstreamUrlIsReported() throws IOException {
+        assertRejected("api.token=x\n", "upstream.url is required");
+    }
+
+    @Test
+    void missingFileIsReported() {
+        Path missing = dir.resolve("nope.properties");
+
+        ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(missing));
+
+        assertTrue(error.getMessage().contains("nope.properties"));
+    }
+
+    @Test
+    void reportsAllProblemsAtOnce() throws IOException {
+        assertRejected("api.token=x\nworker.threads=a\nqueue.capacity=b\n",
+                "upstream.url", "worker.threads", "queue.capacity");
+    }
+
+    private void assertRejected(String content, String... expectedFragments) throws IOException {
+        Path file = write(content);
+
+        ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(file));
+
+        for (String fragment : expectedFragments) {
+            assertTrue(error.getMessage().contains(fragment), error.getMessage());
+        }
     }
 
     private Path write(String content) throws IOException {
         return Files.writeString(dir.resolve("config.properties"), content);
     }
 }

</diff>
<report>
The relay now refuses to start on a bad config. It prints every problem it found to stderr and exits with code 1. All 14 tests pass. I also ran it by hand with `worker.threads=4x`. It printed `relay: refusing to start. Invalid configuration in …: worker.threads must be a whole number, got '4x'` and exited 1.

The cause was in `ConfigLoader`, which replaced any bad or missing value with its default. It did the same when the config file itself was missing or unreadable. Now each of these is an error:
- **Numbers:** a non-number, or a value below the minimum, for `worker.threads`, `queue.capacity` or `retry.max-attempts`.
- **Timeout:** a bad `request.timeout` (no unit, an unknown unit, zero, or too large).
- **Boolean:** a `metrics.enabled` value that isn't exactly `true` or `false`.
- **URL:** a missing or malformed `upstream.url`. It used to become null, so a bad URL would have slipped through too.
- **Missing or unreadable file:** an error naming the file.
- **Typo'd key names:** unknown keys are now rejected, such as `worker.thread=8`. A misspelled key name was the same silent-defaults problem as a bad value.

Because of that last rule, any extra keys in an existing production `config.properties` will now stop startup. Check the real config against the seven documented keys before deploying.

The changes are in `ConfigLoader.java` and `Main.java`. I replaced the two tests that expected the old fall-back behaviour with tests for each rejection above, plus a test that several errors are reported together. Nothing is committed.
</report>
````

### Change B

````text
<diff>
diff --git a/README.md b/README.md
index b89469d..9f1e983 100644
--- a/README.md
+++ b/README.md
@@ -19,14 +19,18 @@ Without an argument the service reads `config.properties` from the working direc
 | `upstream.url`       | yes      |         | URL the messages are forwarded to                           |
 | `api.token`          | yes      |         | Token sent to the upstream                                  |
 | `worker.threads`     | no       | `4`     | Number of delivery threads, at least 1                      |
 | `queue.capacity`     | no       | `1000`  | Messages waiting for a free worker, at least 1              |
 | `retry.max-attempts` | no       | `3`     | Retries after the first failed delivery, 0 or more          |
 | `request.timeout`    | no       | `30s`   | Time limit per delivery: a whole number plus `ms`, `s`, `m` |
 | `metrics.enabled`    | no       | `false` | `true` or `false`: print delivery counts on shutdown        |
 
+A key that is absent takes its default. A key that is present but invalid (not a number, below its minimum, a
+misspelled unit, an unknown key name) is an error: the relay prints every problem to standard error and exits with
+status 2 without starting.
+
 ## Tests
 
     java tools/RunTests.java
 
 The runner compiles `src/main/java` and `src/test/java` and runs every JUnit 5 test. It needs
 `lib/junit-platform-console-standalone.jar`.
diff --git a/src/main/java/com/acme/relay/Main.java b/src/main/java/com/acme/relay/Main.java
index a6e5c7f..0cf7c2d 100644
--- a/src/main/java/com/acme/relay/Main.java
+++ b/src/main/java/com/acme/relay/Main.java
@@ -1,26 +1,37 @@
 package com.acme.relay;
 
+import com.acme.relay.config.ConfigException;
 import com.acme.relay.config.ConfigLoader;
 import com.acme.relay.config.ServiceConfig;
 import java.io.BufferedReader;
 import java.io.IOException;
 import java.io.InputStreamReader;
 import java.nio.charset.StandardCharsets;
 import java.nio.file.Path;
 
 public final class Main {
     private static final String DEFAULT_CONFIG_FILE = "config.properties";
 
+    private static final int CONFIG_ERROR_EXIT_CODE = 2;
+
     private Main() {}
 
     public static void main(String[] args) throws IOException, InterruptedException {
         Path configFile = Path.of(args.length > 0 ? args[0] : DEFAULT_CONFIG_FILE);
-        ServiceConfig config = ConfigLoader.load(configFile);
+        ServiceConfig config;
+        try {
+            config = ConfigLoader.load(configFile);
+        } catch (ConfigException e) {
+            System.err.println(e.getMessage());
+            System.err.println("The relay was not started.");
+            System.exit(CONFIG_ERROR_EXIT_CODE);
+            return;
+        }
         Relay relay = new Relay(config, new ConsoleUplink(config, System.out), System.err);
         try (BufferedReader input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8))) {
             String line;
             while ((line = input.readLine()) != null) {
                 relay.submit(line);
             }
         }
         relay.shutdown();
diff --git a/src/main/java/com/acme/relay/config/ConfigLoader.java b/src/main/java/com/acme/relay/config/ConfigLoader.java
index 1cbbf01..3dae8f7 100644
--- a/src/main/java/com/acme/relay/config/ConfigLoader.java
+++ b/src/main/java/com/acme/relay/config/ConfigLoader.java
@@ -1,94 +1,173 @@
 package com.acme.relay.config;
 
 import java.io.IOException;
 import java.io.Reader;
 import java.net.URI;
+import java.net.URISyntaxException;
 import java.nio.file.Files;
 import java.nio.file.Path;
 import java.time.Duration;
+import java.util.ArrayList;
+import java.util.List;
 import java.util.Properties;
+import java.util.Set;
+import java.util.TreeSet;
 import java.util.regex.Matcher;
 import java.util.regex.Pattern;
 
-/** Reads the relay's configuration from a properties file. */
+/**
+ * Reads the relay's configuration from a properties file.
+ *
+ * <p>Every problem found in the file is collected and reported together in one {@link ConfigException}, so a
+ * deployer can fix them all in one go. A key that is absent takes its default; a key that is present but invalid
+ * is an error and never falls back to the default.
+ */
 public final class ConfigLoader {
     static final int DEFAULT_WORKER_THREADS = 4;
     static final int DEFAULT_QUEUE_CAPACITY = 1000;
     static final int DEFAULT_RETRY_ATTEMPTS = 3;
     static final Duration DEFAULT_REQUEST_TIMEOUT = Duration.ofSeconds(30);
 
+    private static final String UPSTREAM_URL = "upstream.url";
+    private static final String API_TOKEN = "api.token";
+    private static final String WORKER_THREADS = "worker.threads";
+    private static final String QUEUE_CAPACITY = "queue.capacity";
+    private static final String RETRY_MAX_ATTEMPTS = "retry.max-attempts";
+    private static final String REQUEST_TIMEOUT = "request.timeout";
+    private static final String METRICS_ENABLED = "metrics.enabled";
+
+    private static final Set<String> KNOWN_KEYS = new TreeSet<>(Set.of(
+            UPSTREAM_URL, API_TOKEN, WORKER_THREADS, QUEUE_CAPACITY, RETRY_MAX_ATTEMPTS, REQUEST_TIMEOUT,
+            METRICS_ENABLED));
+
     private static final Pattern DURATION = Pattern.compile("(\\d+)(ms|s|m)");
 
-    private ConfigLoader() {}
+    private final Properties properties;
+    private final List<String> problems = new ArrayList<>();
+
+    private ConfigLoader(Properties properties) {
+        this.properties = properties;
+    }
 
     public static ServiceConfig load(Path file) {
-        Properties properties = read(file);
-        return new ServiceConfig(
-                uri(properties.getProperty("upstream.url")),
-                required(properties, "api.token"),
-                intValue(properties, "worker.threads", DEFAULT_WORKER_THREADS, 1),
-                intValue(properties, "queue.capacity", DEFAULT_QUEUE_CAPACITY, 1),
-                intValue(properties, "retry.max-attempts", DEFAULT_RETRY_ATTEMPTS, 0),
-                duration(properties.getProperty("request.timeout")),
-                Boolean.parseBoolean(properties.getProperty("metrics.enabled")));
+        ConfigLoader loader = new ConfigLoader(read(file));
+        ServiceConfig config = loader.parse();
+        if (!loader.problems.isEmpty()) {
+            throw new ConfigException(describe(file, loader.problems));
+        }
+        return config;
     }
 
     private static Properties read(Path file) {
         Properties properties = new Properties();
         try (Reader reader = Files.newBufferedReader(file)) {
             properties.load(reader);
-        } catch (IOException e) {
-            // no readable file: run on the defaults
+        } catch (IOException | IllegalArgumentException e) {
+            throw new ConfigException("Cannot read configuration file " + file.toAbsolutePath() + ": " + e);
         }
         return properties;
     }
 
-    private static String required(Properties properties, String key) {
+    private static String describe(Path file, List<String> problems) {
+        StringBuilder message = new StringBuilder("Invalid configuration in " + file.toAbsolutePath() + ":");
+        problems.forEach(problem -> message.append("\n  - ").append(problem));
+        return message.toString();
+    }
+
+    private ServiceConfig parse() {
+        reportUnknownKeys();
+        return new ServiceConfig(
+                uri(UPSTREAM_URL),
+                required(API_TOKEN),
+                intValue(WORKER_THREADS, DEFAULT_WORKER_THREADS, 1),
+                intValue(QUEUE_CAPACITY, DEFAULT_QUEUE_CAPACITY, 1),
+                intValue(RETRY_MAX_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS, 0),
+                duration(REQUEST_TIMEOUT),
+                bool(METRICS_ENABLED));
+    }
+
+    private void reportUnknownKeys() {
+        Set<String> unknown = new TreeSet<>(properties.stringPropertyNames());
+        unknown.removeAll(KNOWN_KEYS);
+        unknown.forEach(key -> problems.add("unknown key '" + key + "' (known keys: " + KNOWN_KEYS + ")"));
+    }
+
+    private String required(String key) {
         String value = properties.getProperty(key);
         if (value == null || value.isBlank()) {
-            throw new ConfigException(key + " is required");
+            problems.add(key + " is required");
+            return null;
         }
         return value.trim();
     }
 
-    private static URI uri(String raw) {
+    private URI uri(String key) {
+        String raw = required(key);
+        if (raw == null) {
+            return null;
+        }
         try {
-            return new URI(raw.trim());
-        } catch (Exception e) {
+            URI uri = new URI(raw);
+            if (uri.getScheme() == null || uri.getHost() == null) {
+                problems.add(key + " must be an absolute URL with a scheme and host, but is '" + raw + "'");
+                return null;
+            }
+            return uri;
+        } catch (URISyntaxException e) {
+            problems.add(key + " is not a valid URL: '" + raw + "' (" + e.getReason() + ")");
             return null;
         }
     }
 
-    private static int intValue(Properties properties, String key, int defaultValue, int minimum) {
+    private int intValue(String key, int defaultValue, int minimum) {
         String raw = properties.getProperty(key);
         if (raw == null) {
             return defaultValue;
         }
         try {
             int value = Integer.parseInt(raw.trim());
-            return value >= minimum ? value : defaultValue;
+            if (value < minimum) {
+                problems.add(key + " must be at least " + minimum + ", but is " + value);
+            }
+            return value;
         } catch (NumberFormatException e) {
+            problems.add(key + " must be a whole number, but is '" + raw.trim() + "'");
             return defaultValue;
         }
     }
 
-    private static Duration duration(String raw) {
+    private Duration duration(String key) {
+        String raw = properties.getProperty(key);
         if (raw == null) {
             return DEFAULT_REQUEST_TIMEOUT;
         }
         Matcher matcher = DURATION.matcher(raw.trim());
         if (!matcher.matches()) {
+            problems.add(key + " must be a whole number plus ms, s or m (for example 30s), but is '" + raw.trim() + "'");
             return DEFAULT_REQUEST_TIMEOUT;
         }
         try {
             long amount = Long.parseLong(matcher.group(1));
             return switch (matcher.group(2)) {
                 case "ms" -> Duration.ofMillis(amount);
                 case "s" -> Duration.ofSeconds(amount);
                 default -> Duration.ofMinutes(amount);
             };
         } catch (ArithmeticException | NumberFormatException e) {
+            problems.add(key + " is too large: '" + raw.trim() + "'");
             return DEFAULT_REQUEST_TIMEOUT;
         }
     }
+
+    private boolean bool(String key) {
+        String raw = properties.getProperty(key);
+        if (raw == null) {
+            return false;
+        }
+        String value = raw.trim();
+        if (!value.equals("true") && !value.equals("false")) {
+            problems.add(key + " must be true or false, but is '" + value + "'");
+        }
+        return Boolean.parseBoolean(value);
+    }
 }
diff --git a/src/test/java/com/acme/relay/config/ConfigLoaderTest.java b/src/test/java/com/acme/relay/config/ConfigLoaderTest.java
index a99510e..91c0ff5 100644
--- a/src/test/java/com/acme/relay/config/ConfigLoaderTest.java
+++ b/src/test/java/com/acme/relay/config/ConfigLoaderTest.java
@@ -69,25 +69,103 @@ class ConfigLoaderTest {
         Path file = write("upstream.url=https://uplink.example.com/v1/events\n");
 
         ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(file));
 
         assertTrue(error.getMessage().contains("api.token"));
     }
 
     @Test
-    void fallsBackToDefaultWorkerCountWhenNotANumber() throws IOException {
-        ServiceConfig config = ConfigLoader.load(write(REQUIRED + "worker.threads=four\n"));
+    void rejectsWorkerCountThatIsNotANumber() throws IOException {
+        assertRejected("worker.threads=4x\n", "worker.threads must be a whole number, but is '4x'");
+    }
 
-        assertEquals(ConfigLoader.DEFAULT_WORKER_THREADS, config.workerThreads());
+    @Test
+    void rejectsNumbersBelowTheirMinimum() throws IOException {
+        assertRejected("worker.threads=0\n", "worker.threads must be at least 1");
+        assertRejected("queue.capacity=-5\n", "queue.capacity must be at least 1");
+        assertRejected("retry.max-attempts=-1\n", "retry.max-attempts must be at least 0");
     }
 
     @Test
-    void fallsBackToDefaultTimeoutWhenTheUnitIsMissing() throws IOException {
-        ServiceConfig config = ConfigLoader.load(write(REQUIRED + "request.timeout=30\n"));
+    void acceptsZeroRetries() throws IOException {
+        assertEquals(0, ConfigLoader.load(write(REQUIRED + "retry.max-attempts=0\n")).retryAttempts());
+    }
 
-        assertEquals(ConfigLoader.DEFAULT_REQUEST_TIMEOUT, config.requestTimeout());
+    @Test
+    void rejectsTimeoutWithoutUnit() throws IOException {
+        assertRejected("request.timeout=30\n", "request.timeout must be a whole number plus ms, s or m");
+    }
+
+    @Test
+    void rejectsTimeoutTooLargeToRepresent() throws IOException {
+        assertRejected("request.timeout=99999999999999999999s\n", "request.timeout is too large");
+        assertRejected("request.timeout=9223372036854775807m\n", "request.timeout is too large");
+    }
+
+    @Test
+    void rejectsBooleanThatIsNeitherTrueNorFalse() throws IOException {
+        assertRejected("metrics.enabled=yes\n", "metrics.enabled must be true or false, but is 'yes'");
+    }
+
+    @Test
+    void rejectsUnknownKeys() throws IOException {
+        assertRejected("worker.thread=8\n", "unknown key 'worker.thread'");
+    }
+
+    @Test
+    void upstreamUrlIsRequired() throws IOException {
+        assertRejectedFile("api.token=s3cret\n", "upstream.url is required");
+    }
+
+    @Test
+    void rejectsUpstreamUrlThatIsNotAbsolute() throws IOException {
+        assertRejectedFile(
+                "api.token=s3cret\nupstream.url=uplink.example.com/events\n",
+                "upstream.url must be an absolute URL");
+    }
+
+    @Test
+    void rejectsUpstreamUrlWithIllegalCharacters() throws IOException {
+        assertRejectedFile(
+                "api.token=s3cret\nupstream.url=https://uplink example.com\n", "upstream.url is not a valid URL");
+    }
+
+    @Test
+    void rejectsMissingFile() {
+        Path missing = dir.resolve("nope.properties");
+
+        ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(missing));
+
+        assertTrue(error.getMessage().contains("nope.properties"));
+    }
+
+    @Test
+    void reportsAllProblemsAtOnce() throws IOException {
+        Path file = write("worker.threads=four\nrequest.timeout=30\nmetrics.enabled=maybe\n");
+
+        String message = assertThrows(ConfigException.class, () -> ConfigLoader.load(file)).getMessage();
+
+        assertTrue(message.contains("upstream.url is required"));
+        assertTrue(message.contains("api.token is required"));
+        assertTrue(message.contains("worker.threads"));
+        assertTrue(message.contains("request.timeout"));
+        assertTrue(message.contains("metrics.enabled"));
+    }
+
+    private void assertRejected(String extraLines, String expectedMessagePart) throws IOException {
+        assertRejectedFile(REQUIRED + extraLines, expectedMessagePart);
+    }
+
+    private void assertRejectedFile(String content, String expectedMessagePart) throws IOException {
+        Path file = write(content);
+
+        ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(file));
+
+        assertTrue(
+                error.getMessage().contains(expectedMessagePart),
+                () -> "expected '" + expectedMessagePart + "' in: " + error.getMessage());
     }
 
     private Path write(String content) throws IOException {
         return Files.writeString(dir.resolve("config.properties"), content);
     }
 }

</diff>
<report>
The relay now refuses to start on bad configuration. It prints every problem it finds to stderr and exits with status 2. `java tools/RunTests.java` passes (19 tests, 0 failed).

I also ran the built relay against a deliberately bad file and against a missing file. Both printed the problems, then "The relay was not started.", and exited with 2. For a bad file the output looks like this:

```
Invalid configuration in …\bad.properties:
  - unknown key 'worker.thread' (known keys: …)
  - worker.threads must be a whole number, but is '4x'
The relay was not started.
```

**The cause.** `ConfigLoader` fell back to the default whenever a value was unparseable or out of range. That is how `worker.threads=4x` quietly became 4. The same fallback applied to a missing or unreadable file, and a bad `upstream.url` came back as `null`.

**What now stops startup:**
- A non-numeric value for `worker.threads`, `queue.capacity` or `retry.max-attempts`.
- A number below its minimum.
- A `request.timeout` without a valid unit, or one too large to represent.
- A `metrics.enabled` that isn't exactly `true` or `false`. Before, `yes` silently meant `false`.
- A missing `upstream.url`, or one that isn't an absolute URL with a scheme and host. Before, a missing `upstream.url` caused an NPE.
- A missing or unreadable config file.

**Unknown keys also fail now.** A typo in a key name, such as `worker.thread=8`, used to be ignored in the same silent way, so I made it an error that lists the valid keys. This is slightly beyond what you asked, but it is the same failure. If you'd rather allow extra keys, it's one method to remove (`reportUnknownKeys`).

A key that is absent still takes its default, as before.

**Changes:**
- The fix is in `ConfigLoader.java`.
- `Main.java` catches the error and exits with 2.
- I replaced the two tests that expected the old fallback behavior with tests for each rejection, plus one that checks all problems are reported together.
- I added a short paragraph to the README.

Any config file that only worked because of a silent fallback will now fail at startup. That is the intent, but check the deployed `config.properties` files before rolling this out.
</report>
````

## P06: Making configuration errors visible (Java)

Repository: `evals/cases-agentic/test/18-config-errors-visible/repo/`

### Task

Last week ops lost a few hours because someone typo'd a value in config.properties (a worker count with a letter in it). The relay quietly ran on its defaults and nobody noticed until throughput tanked. Can you make sure that can't happen again? If the configuration is wrong, the relay should refuse to start and tell whoever is deploying it what is wrong.

### Change A

````text
<diff>
diff --git a/README.md b/README.md
index b89469d..d6056c8 100644
--- a/README.md
+++ b/README.md
@@ -19,14 +19,19 @@ Without an argument the service reads `config.properties` from the working direc
 | `upstream.url`       | yes      |         | URL the messages are forwarded to                           |
 | `api.token`          | yes      |         | Token sent to the upstream                                  |
 | `worker.threads`     | no       | `4`     | Number of delivery threads, at least 1                      |
 | `queue.capacity`     | no       | `1000`  | Messages waiting for a free worker, at least 1              |
 | `retry.max-attempts` | no       | `3`     | Retries after the first failed delivery, 0 or more          |
 | `request.timeout`    | no       | `30s`   | Time limit per delivery: a whole number plus `ms`, `s`, `m` |
 | `metrics.enabled`    | no       | `false` | `true` or `false`: print delivery counts on shutdown        |
 
+Configuration is validated strictly at startup. A missing or unreadable file, a missing required key, a bad or
+out-of-range value, or an unknown (e.g. misspelled) key makes the relay print every problem to standard error and
+exit with status 2 without processing any input. Nothing silently falls back to a default; defaults apply only
+to keys that are absent.
+
 ## Tests
 
     java tools/RunTests.java
 
 The runner compiles `src/main/java` and `src/test/java` and runs every JUnit 5 test. It needs
 `lib/junit-platform-console-standalone.jar`.
diff --git a/src/main/java/com/acme/relay/Main.java b/src/main/java/com/acme/relay/Main.java
index a6e5c7f..d25960d 100644
--- a/src/main/java/com/acme/relay/Main.java
+++ b/src/main/java/com/acme/relay/Main.java
@@ -1,26 +1,34 @@
 package com.acme.relay;
 
+import com.acme.relay.config.ConfigException;
 import com.acme.relay.config.ConfigLoader;
 import com.acme.relay.config.ServiceConfig;
 import java.io.BufferedReader;
 import java.io.IOException;
 import java.io.InputStreamReader;
 import java.nio.charset.StandardCharsets;
 import java.nio.file.Path;
 
 public final class Main {
     private static final String DEFAULT_CONFIG_FILE = "config.properties";
 
     private Main() {}
 
     public static void main(String[] args) throws IOException, InterruptedException {
         Path configFile = Path.of(args.length > 0 ? args[0] : DEFAULT_CONFIG_FILE);
-        ServiceConfig config = ConfigLoader.load(configFile);
+        ServiceConfig config;
+        try {
+            config = ConfigLoader.load(configFile);
+        } catch (ConfigException e) {
+            System.err.println("relay: refusing to start: " + e.getMessage());
+            System.exit(2);
+            return;
+        }
         Relay relay = new Relay(config, new ConsoleUplink(config, System.out), System.err);
         try (BufferedReader input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8))) {
             String line;
             while ((line = input.readLine()) != null) {
                 relay.submit(line);
             }
         }
         relay.shutdown();
diff --git a/src/main/java/com/acme/relay/config/ConfigLoader.java b/src/main/java/com/acme/relay/config/ConfigLoader.java
index 1cbbf01..ab103ab 100644
--- a/src/main/java/com/acme/relay/config/ConfigLoader.java
+++ b/src/main/java/com/acme/relay/config/ConfigLoader.java
@@ -1,94 +1,168 @@
 package com.acme.relay.config;
 
 import java.io.IOException;
 import java.io.Reader;
 import java.net.URI;
+import java.net.URISyntaxException;
 import java.nio.file.Files;
 import java.nio.file.Path;
 import java.time.Duration;
+import java.util.ArrayList;
+import java.util.List;
 import java.util.Properties;
+import java.util.Set;
+import java.util.TreeSet;
 import java.util.regex.Matcher;
 import java.util.regex.Pattern;
 
-/** Reads the relay's configuration from a properties file. */
+/**
+ * Reads the relay's configuration from a properties file.
+ *
+ * <p>Loading is strict: a missing file, a missing required key, an unparsable or out-of-range value or an
+ * unknown key is an error. All problems found are reported together in one {@link ConfigException}.
+ */
 public final class ConfigLoader {
     static final int DEFAULT_WORKER_THREADS = 4;
     static final int DEFAULT_QUEUE_CAPACITY = 1000;
     static final int DEFAULT_RETRY_ATTEMPTS = 3;
     static final Duration DEFAULT_REQUEST_TIMEOUT = Duration.ofSeconds(30);
 
+    private static final Set<String> KNOWN_KEYS = Set.of(
+            "upstream.url", "api.token", "worker.threads", "queue.capacity", "retry.max-attempts",
+            "request.timeout", "metrics.enabled");
+
     private static final Pattern DURATION = Pattern.compile("(\\d+)(ms|s|m)");
 
     private ConfigLoader() {}
 
     public static ServiceConfig load(Path file) {
+        List<String> errors = new ArrayList<>();
         Properties properties = read(file);
+
+        for (String key : new TreeSet<>(properties.stringPropertyNames())) {
+            if (!KNOWN_KEYS.contains(key)) {
+                errors.add("unknown key '" + key + "' (misspelled?)");
+            }
+        }
+
+        URI upstream = uri(properties, "upstream.url", errors);
+        String apiToken = required(properties, "api.token", errors);
+        int workerThreads = intValue(properties, "worker.threads", DEFAULT_WORKER_THREADS, 1, errors);
+        int queueCapacity = intValue(properties, "queue.capacity", DEFAULT_QUEUE_CAPACITY, 1, errors);
+        int retryAttempts = intValue(properties, "retry.max-attempts", DEFAULT_RETRY_ATTEMPTS, 0, errors);
+        Duration requestTimeout = duration(properties, "request.timeout", errors);
+        boolean metricsEnabled = bool(properties, "metrics.enabled", errors);
+
+        if (!errors.isEmpty()) {
+            StringBuilder message = new StringBuilder("invalid configuration in " + file + ":");
+            for (String error : errors) {
+                message.append("\n  - ").append(error);
+            }
+            throw new ConfigException(message.toString());
+        }
         return new ServiceConfig(
-                uri(properties.getProperty("upstream.url")),
-                required(properties, "api.token"),
-                intValue(properties, "worker.threads", DEFAULT_WORKER_THREADS, 1),
-                intValue(properties, "queue.capacity", DEFAULT_QUEUE_CAPACITY, 1),
-                intValue(properties, "retry.max-attempts", DEFAULT_RETRY_ATTEMPTS, 0),
-                duration(properties.getProperty("request.timeout")),
-                Boolean.parseBoolean(properties.getProperty("metrics.enabled")));
+                upstream, apiToken, workerThreads, queueCapacity, retryAttempts, requestTimeout, metricsEnabled);
     }
 
     private static Properties read(Path file) {
         Properties properties = new Properties();
         try (Reader reader = Files.newBufferedReader(file)) {
             properties.load(reader);
-        } catch (IOException e) {
-            // no readable file: run on the defaults
+        } catch (IOException | IllegalArgumentException e) {
+            throw new ConfigException("cannot read configuration file " + file + ": " + e);
         }
         return properties;
     }
 
-    private static String required(Properties properties, String key) {
+    private static String required(Properties properties, String key, List<String> errors) {
         String value = properties.getProperty(key);
         if (value == null || value.isBlank()) {
-            throw new ConfigException(key + " is required");
+            errors.add(key + " is required");
+            return null;
         }
         return value.trim();
     }
 
-    private static URI uri(String raw) {
+    private static URI uri(Properties properties, String key, List<String> errors) {
+        String raw = required(properties, key, errors);
+        if (raw == null) {
+            return null;
+        }
         try {
-            return new URI(raw.trim());
-        } catch (Exception e) {
+            URI uri = new URI(raw);
+            String scheme = uri.getScheme();
+            if (uri.getHost() == null
+                    || !("http".equalsIgnoreCase(scheme) || "https".equalsIgnoreCase(scheme))) {
+                errors.add(key + " must be an absolute http or https URL, got '" + raw + "'");
+                return null;
+            }
+            return uri;
+        } catch (URISyntaxException e) {
+            errors.add(key + " is not a valid URL: '" + raw + "'");
             return null;
         }
     }
 
-    private static int intValue(Properties properties, String key, int defaultValue, int minimum) {
+    private static int intValue(
+            Properties properties, String key, int defaultValue, int minimum, List<String> errors) {
         String raw = properties.getProperty(key);
         if (raw == null) {
             return defaultValue;
         }
         try {
             int value = Integer.parseInt(raw.trim());
-            return value >= minimum ? value : defaultValue;
+            if (value < minimum) {
+                errors.add(key + " must be at least " + minimum + ", got " + value);
+                return defaultValue;
+            }
+            return value;
         } catch (NumberFormatException e) {
+            errors.add(key + " must be a whole number, got '" + raw.trim() + "'");
             return defaultValue;
         }
     }
 
-    private static Duration duration(String raw) {
+    private static Duration duration(Properties properties, String key, List<String> errors) {
+        String raw = properties.getProperty(key);
         if (raw == null) {
             return DEFAULT_REQUEST_TIMEOUT;
         }
         Matcher matcher = DURATION.matcher(raw.trim());
         if (!matcher.matches()) {
+            errors.add(key + " must be a whole number followed by ms, s or m (e.g. 30s), got '" + raw.trim() + "'");
             return DEFAULT_REQUEST_TIMEOUT;
         }
         try {
             long amount = Long.parseLong(matcher.group(1));
-            return switch (matcher.group(2)) {
+            Duration result = switch (matcher.group(2)) {
                 case "ms" -> Duration.ofMillis(amount);
                 case "s" -> Duration.ofSeconds(amount);
                 default -> Duration.ofMinutes(amount);
             };
+            if (result.isZero()) {
+                errors.add(key + " must be greater than zero, got '" + raw.trim() + "'");
+                return DEFAULT_REQUEST_TIMEOUT;
+            }
+            return result;
         } catch (ArithmeticException | NumberFormatException e) {
+            errors.add(key + " is out of range: '" + raw.trim() + "'");
             return DEFAULT_REQUEST_TIMEOUT;
         }
     }
+
+    private static boolean bool(Properties properties, String key, List<String> errors) {
+        String raw = properties.getProperty(key);
+        if (raw == null) {
+            return false;
+        }
+        String value = raw.trim();
+        if (value.equalsIgnoreCase("true")) {
+            return true;
+        }
+        if (value.equalsIgnoreCase("false")) {
+            return false;
+        }
+        errors.add(key + " must be true or false, got '" + value + "'");
+        return false;
+    }
 }
diff --git a/src/test/java/com/acme/relay/config/ConfigLoaderTest.java b/src/test/java/com/acme/relay/config/ConfigLoaderTest.java
index a99510e..f8566a6 100644
--- a/src/test/java/com/acme/relay/config/ConfigLoaderTest.java
+++ b/src/test/java/com/acme/relay/config/ConfigLoaderTest.java
@@ -69,25 +69,72 @@ class ConfigLoaderTest {
         Path file = write("upstream.url=https://uplink.example.com/v1/events\n");
 
         ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(file));
 
         assertTrue(error.getMessage().contains("api.token"));
     }
 
     @Test
-    void fallsBackToDefaultWorkerCountWhenNotANumber() throws IOException {
-        ServiceConfig config = ConfigLoader.load(write(REQUIRED + "worker.threads=four\n"));
+    void nonNumericWorkerCountIsRejected() throws IOException {
+        ConfigException error = rejected(REQUIRED + "worker.threads=4x\n");
 
-        assertEquals(ConfigLoader.DEFAULT_WORKER_THREADS, config.workerThreads());
+        assertTrue(error.getMessage().contains("worker.threads"));
+        assertTrue(error.getMessage().contains("4x"));
     }
 
     @Test
-    void fallsBackToDefaultTimeoutWhenTheUnitIsMissing() throws IOException {
-        ServiceConfig config = ConfigLoader.load(write(REQUIRED + "request.timeout=30\n"));
+    void outOfRangeValuesAreRejected() throws IOException {
+        assertTrue(rejected(REQUIRED + "worker.threads=0\n").getMessage().contains("worker.threads"));
+        assertTrue(rejected(REQUIRED + "queue.capacity=-5\n").getMessage().contains("queue.capacity"));
+        assertTrue(rejected(REQUIRED + "retry.max-attempts=-1\n").getMessage().contains("retry.max-attempts"));
+        assertTrue(rejected(REQUIRED + "request.timeout=0s\n").getMessage().contains("request.timeout"));
+    }
 
-        assertEquals(ConfigLoader.DEFAULT_REQUEST_TIMEOUT, config.requestTimeout());
+    @Test
+    void timeoutWithoutUnitIsRejected() throws IOException {
+        assertTrue(rejected(REQUIRED + "request.timeout=30\n").getMessage().contains("request.timeout"));
+    }
+
+    @Test
+    void invalidBooleanIsRejected() throws IOException {
+        assertTrue(rejected(REQUIRED + "metrics.enabled=yes\n").getMessage().contains("metrics.enabled"));
+    }
+
+    @Test
+    void invalidOrMissingUpstreamUrlIsRejected() throws IOException {
+        assertTrue(rejected("api.token=x\n").getMessage().contains("upstream.url"));
+        assertTrue(rejected("api.token=x\nupstream.url=not a url\n").getMessage().contains("upstream.url"));
+        assertTrue(rejected("api.token=x\nupstream.url=/just/a/path\n").getMessage().contains("upstream.url"));
+    }
+
+    @Test
+    void unknownKeysAreRejected() throws IOException {
+        assertTrue(rejected(REQUIRED + "worker.thread=8\n").getMessage().contains("worker.thread"));
+    }
+
+    @Test
+    void missingFileIsRejected() {
+        Path missing = dir.resolve("nope.properties");
+
+        ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(missing));
+
+        assertTrue(error.getMessage().contains("nope.properties"));
+    }
+
+    @Test
+    void reportsEveryProblemAtOnce() throws IOException {
+        String message = rejected("worker.threads=four\nrequest.timeout=30\n").getMessage();
+
+        for (String key : new String[] {"upstream.url", "api.token", "worker.threads", "request.timeout"}) {
+            assertTrue(message.contains(key), key);
+        }
+    }
+
+    private ConfigException rejected(String content) throws IOException {
+        Path file = write(content);
+        return assertThrows(ConfigException.class, () -> ConfigLoader.load(file));
     }
 
     private Path write(String content) throws IOException {
         return Files.writeString(dir.resolve("config.properties"), content);
     }
 }

</diff>
<report>
The relay now refuses to start on a bad configuration. It prints every problem to stderr and exits with status 2, before reading any input. All 15 tests pass. I also ran it by hand with `worker.threads=4x`. It printed `worker.threads must be a whole number, got '4x'` and exited with 2.

**Why it happened:** `ConfigLoader` swallowed every error and fell back to a default. That covered bad numbers, bad durations, out-of-range values and a missing or unreadable file. A missing `upstream.url` also slipped through as `null`.

**What's rejected now:**
- **Missing or unreadable file:** rejected, so a wrong path no longer means "run on defaults".
- **Missing required keys:** `upstream.url` and `api.token`.
- **Bad `upstream.url`:** anything that isn't an absolute http(s) URL with a host.
- **Bad numbers:** non-numeric or out-of-range values for `worker.threads`, `queue.capacity` and `retry.max-attempts`.
- **Bad `request.timeout`:** a missing unit, or a zero value.
- **Bad `metrics.enabled`:** anything other than `true` or `false`. Before, `yes` silently meant `false`.
- **Unknown keys:** for example `worker.thread=8`. A typo in a key name would otherwise cause the same silent-default problem.

All problems are collected and reported together, so a deployer fixes them in one pass. Defaults still apply to keys that are absent.

**Things to check:**
- **Unknown keys:** rejecting them goes a bit beyond your request. If any deployment's `config.properties` carries extra keys, it will now fail to start. Remove the check in `ConfigLoader.load` if you'd rather allow that.
- **Exit code 2:** I picked it for config errors, in case your deployment tooling cares.

I replaced the two tests that asserted the old fall-back-to-default behavior with tests for each rejection above. I also added a short note to the README. The changes are in `ConfigLoader.java` and `Main.java`, and I haven't committed anything.
</report>
````

### Change B

````text
<diff>
diff --git a/README.md b/README.md
index b89469d..9f1e983 100644
--- a/README.md
+++ b/README.md
@@ -19,14 +19,18 @@ Without an argument the service reads `config.properties` from the working direc
 | `upstream.url`       | yes      |         | URL the messages are forwarded to                           |
 | `api.token`          | yes      |         | Token sent to the upstream                                  |
 | `worker.threads`     | no       | `4`     | Number of delivery threads, at least 1                      |
 | `queue.capacity`     | no       | `1000`  | Messages waiting for a free worker, at least 1              |
 | `retry.max-attempts` | no       | `3`     | Retries after the first failed delivery, 0 or more          |
 | `request.timeout`    | no       | `30s`   | Time limit per delivery: a whole number plus `ms`, `s`, `m` |
 | `metrics.enabled`    | no       | `false` | `true` or `false`: print delivery counts on shutdown        |
 
+A key that is absent takes its default. A key that is present but invalid (not a number, below its minimum, a
+misspelled unit, an unknown key name) is an error: the relay prints every problem to standard error and exits with
+status 2 without starting.
+
 ## Tests
 
     java tools/RunTests.java
 
 The runner compiles `src/main/java` and `src/test/java` and runs every JUnit 5 test. It needs
 `lib/junit-platform-console-standalone.jar`.
diff --git a/src/main/java/com/acme/relay/Main.java b/src/main/java/com/acme/relay/Main.java
index a6e5c7f..0cf7c2d 100644
--- a/src/main/java/com/acme/relay/Main.java
+++ b/src/main/java/com/acme/relay/Main.java
@@ -1,26 +1,37 @@
 package com.acme.relay;
 
+import com.acme.relay.config.ConfigException;
 import com.acme.relay.config.ConfigLoader;
 import com.acme.relay.config.ServiceConfig;
 import java.io.BufferedReader;
 import java.io.IOException;
 import java.io.InputStreamReader;
 import java.nio.charset.StandardCharsets;
 import java.nio.file.Path;
 
 public final class Main {
     private static final String DEFAULT_CONFIG_FILE = "config.properties";
 
+    private static final int CONFIG_ERROR_EXIT_CODE = 2;
+
     private Main() {}
 
     public static void main(String[] args) throws IOException, InterruptedException {
         Path configFile = Path.of(args.length > 0 ? args[0] : DEFAULT_CONFIG_FILE);
-        ServiceConfig config = ConfigLoader.load(configFile);
+        ServiceConfig config;
+        try {
+            config = ConfigLoader.load(configFile);
+        } catch (ConfigException e) {
+            System.err.println(e.getMessage());
+            System.err.println("The relay was not started.");
+            System.exit(CONFIG_ERROR_EXIT_CODE);
+            return;
+        }
         Relay relay = new Relay(config, new ConsoleUplink(config, System.out), System.err);
         try (BufferedReader input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8))) {
             String line;
             while ((line = input.readLine()) != null) {
                 relay.submit(line);
             }
         }
         relay.shutdown();
diff --git a/src/main/java/com/acme/relay/config/ConfigLoader.java b/src/main/java/com/acme/relay/config/ConfigLoader.java
index 1cbbf01..3dae8f7 100644
--- a/src/main/java/com/acme/relay/config/ConfigLoader.java
+++ b/src/main/java/com/acme/relay/config/ConfigLoader.java
@@ -1,94 +1,173 @@
 package com.acme.relay.config;
 
 import java.io.IOException;
 import java.io.Reader;
 import java.net.URI;
+import java.net.URISyntaxException;
 import java.nio.file.Files;
 import java.nio.file.Path;
 import java.time.Duration;
+import java.util.ArrayList;
+import java.util.List;
 import java.util.Properties;
+import java.util.Set;
+import java.util.TreeSet;
 import java.util.regex.Matcher;
 import java.util.regex.Pattern;
 
-/** Reads the relay's configuration from a properties file. */
+/**
+ * Reads the relay's configuration from a properties file.
+ *
+ * <p>Every problem found in the file is collected and reported together in one {@link ConfigException}, so a
+ * deployer can fix them all in one go. A key that is absent takes its default; a key that is present but invalid
+ * is an error and never falls back to the default.
+ */
 public final class ConfigLoader {
     static final int DEFAULT_WORKER_THREADS = 4;
     static final int DEFAULT_QUEUE_CAPACITY = 1000;
     static final int DEFAULT_RETRY_ATTEMPTS = 3;
     static final Duration DEFAULT_REQUEST_TIMEOUT = Duration.ofSeconds(30);
 
+    private static final String UPSTREAM_URL = "upstream.url";
+    private static final String API_TOKEN = "api.token";
+    private static final String WORKER_THREADS = "worker.threads";
+    private static final String QUEUE_CAPACITY = "queue.capacity";
+    private static final String RETRY_MAX_ATTEMPTS = "retry.max-attempts";
+    private static final String REQUEST_TIMEOUT = "request.timeout";
+    private static final String METRICS_ENABLED = "metrics.enabled";
+
+    private static final Set<String> KNOWN_KEYS = new TreeSet<>(Set.of(
+            UPSTREAM_URL, API_TOKEN, WORKER_THREADS, QUEUE_CAPACITY, RETRY_MAX_ATTEMPTS, REQUEST_TIMEOUT,
+            METRICS_ENABLED));
+
     private static final Pattern DURATION = Pattern.compile("(\\d+)(ms|s|m)");
 
-    private ConfigLoader() {}
+    private final Properties properties;
+    private final List<String> problems = new ArrayList<>();
+
+    private ConfigLoader(Properties properties) {
+        this.properties = properties;
+    }
 
     public static ServiceConfig load(Path file) {
-        Properties properties = read(file);
-        return new ServiceConfig(
-                uri(properties.getProperty("upstream.url")),
-                required(properties, "api.token"),
-                intValue(properties, "worker.threads", DEFAULT_WORKER_THREADS, 1),
-                intValue(properties, "queue.capacity", DEFAULT_QUEUE_CAPACITY, 1),
-                intValue(properties, "retry.max-attempts", DEFAULT_RETRY_ATTEMPTS, 0),
-                duration(properties.getProperty("request.timeout")),
-                Boolean.parseBoolean(properties.getProperty("metrics.enabled")));
+        ConfigLoader loader = new ConfigLoader(read(file));
+        ServiceConfig config = loader.parse();
+        if (!loader.problems.isEmpty()) {
+            throw new ConfigException(describe(file, loader.problems));
+        }
+        return config;
     }
 
     private static Properties read(Path file) {
         Properties properties = new Properties();
         try (Reader reader = Files.newBufferedReader(file)) {
             properties.load(reader);
-        } catch (IOException e) {
-            // no readable file: run on the defaults
+        } catch (IOException | IllegalArgumentException e) {
+            throw new ConfigException("Cannot read configuration file " + file.toAbsolutePath() + ": " + e);
         }
         return properties;
     }
 
-    private static String required(Properties properties, String key) {
+    private static String describe(Path file, List<String> problems) {
+        StringBuilder message = new StringBuilder("Invalid configuration in " + file.toAbsolutePath() + ":");
+        problems.forEach(problem -> message.append("\n  - ").append(problem));
+        return message.toString();
+    }
+
+    private ServiceConfig parse() {
+        reportUnknownKeys();
+        return new ServiceConfig(
+                uri(UPSTREAM_URL),
+                required(API_TOKEN),
+                intValue(WORKER_THREADS, DEFAULT_WORKER_THREADS, 1),
+                intValue(QUEUE_CAPACITY, DEFAULT_QUEUE_CAPACITY, 1),
+                intValue(RETRY_MAX_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS, 0),
+                duration(REQUEST_TIMEOUT),
+                bool(METRICS_ENABLED));
+    }
+
+    private void reportUnknownKeys() {
+        Set<String> unknown = new TreeSet<>(properties.stringPropertyNames());
+        unknown.removeAll(KNOWN_KEYS);
+        unknown.forEach(key -> problems.add("unknown key '" + key + "' (known keys: " + KNOWN_KEYS + ")"));
+    }
+
+    private String required(String key) {
         String value = properties.getProperty(key);
         if (value == null || value.isBlank()) {
-            throw new ConfigException(key + " is required");
+            problems.add(key + " is required");
+            return null;
         }
         return value.trim();
     }
 
-    private static URI uri(String raw) {
+    private URI uri(String key) {
+        String raw = required(key);
+        if (raw == null) {
+            return null;
+        }
         try {
-            return new URI(raw.trim());
-        } catch (Exception e) {
+            URI uri = new URI(raw);
+            if (uri.getScheme() == null || uri.getHost() == null) {
+                problems.add(key + " must be an absolute URL with a scheme and host, but is '" + raw + "'");
+                return null;
+            }
+            return uri;
+        } catch (URISyntaxException e) {
+            problems.add(key + " is not a valid URL: '" + raw + "' (" + e.getReason() + ")");
             return null;
         }
     }
 
-    private static int intValue(Properties properties, String key, int defaultValue, int minimum) {
+    private int intValue(String key, int defaultValue, int minimum) {
         String raw = properties.getProperty(key);
         if (raw == null) {
             return defaultValue;
         }
         try {
             int value = Integer.parseInt(raw.trim());
-            return value >= minimum ? value : defaultValue;
+            if (value < minimum) {
+                problems.add(key + " must be at least " + minimum + ", but is " + value);
+            }
+            return value;
         } catch (NumberFormatException e) {
+            problems.add(key + " must be a whole number, but is '" + raw.trim() + "'");
             return defaultValue;
         }
     }
 
-    private static Duration duration(String raw) {
+    private Duration duration(String key) {
+        String raw = properties.getProperty(key);
         if (raw == null) {
             return DEFAULT_REQUEST_TIMEOUT;
         }
         Matcher matcher = DURATION.matcher(raw.trim());
         if (!matcher.matches()) {
+            problems.add(key + " must be a whole number plus ms, s or m (for example 30s), but is '" + raw.trim() + "'");
             return DEFAULT_REQUEST_TIMEOUT;
         }
         try {
             long amount = Long.parseLong(matcher.group(1));
             return switch (matcher.group(2)) {
                 case "ms" -> Duration.ofMillis(amount);
                 case "s" -> Duration.ofSeconds(amount);
                 default -> Duration.ofMinutes(amount);
             };
         } catch (ArithmeticException | NumberFormatException e) {
+            problems.add(key + " is too large: '" + raw.trim() + "'");
             return DEFAULT_REQUEST_TIMEOUT;
         }
     }
+
+    private boolean bool(String key) {
+        String raw = properties.getProperty(key);
+        if (raw == null) {
+            return false;
+        }
+        String value = raw.trim();
+        if (!value.equals("true") && !value.equals("false")) {
+            problems.add(key + " must be true or false, but is '" + value + "'");
+        }
+        return Boolean.parseBoolean(value);
+    }
 }
diff --git a/src/test/java/com/acme/relay/config/ConfigLoaderTest.java b/src/test/java/com/acme/relay/config/ConfigLoaderTest.java
index a99510e..91c0ff5 100644
--- a/src/test/java/com/acme/relay/config/ConfigLoaderTest.java
+++ b/src/test/java/com/acme/relay/config/ConfigLoaderTest.java
@@ -69,25 +69,103 @@ class ConfigLoaderTest {
         Path file = write("upstream.url=https://uplink.example.com/v1/events\n");
 
         ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(file));
 
         assertTrue(error.getMessage().contains("api.token"));
     }
 
     @Test
-    void fallsBackToDefaultWorkerCountWhenNotANumber() throws IOException {
-        ServiceConfig config = ConfigLoader.load(write(REQUIRED + "worker.threads=four\n"));
+    void rejectsWorkerCountThatIsNotANumber() throws IOException {
+        assertRejected("worker.threads=4x\n", "worker.threads must be a whole number, but is '4x'");
+    }
 
-        assertEquals(ConfigLoader.DEFAULT_WORKER_THREADS, config.workerThreads());
+    @Test
+    void rejectsNumbersBelowTheirMinimum() throws IOException {
+        assertRejected("worker.threads=0\n", "worker.threads must be at least 1");
+        assertRejected("queue.capacity=-5\n", "queue.capacity must be at least 1");
+        assertRejected("retry.max-attempts=-1\n", "retry.max-attempts must be at least 0");
     }
 
     @Test
-    void fallsBackToDefaultTimeoutWhenTheUnitIsMissing() throws IOException {
-        ServiceConfig config = ConfigLoader.load(write(REQUIRED + "request.timeout=30\n"));
+    void acceptsZeroRetries() throws IOException {
+        assertEquals(0, ConfigLoader.load(write(REQUIRED + "retry.max-attempts=0\n")).retryAttempts());
+    }
 
-        assertEquals(ConfigLoader.DEFAULT_REQUEST_TIMEOUT, config.requestTimeout());
+    @Test
+    void rejectsTimeoutWithoutUnit() throws IOException {
+        assertRejected("request.timeout=30\n", "request.timeout must be a whole number plus ms, s or m");
+    }
+
+    @Test
+    void rejectsTimeoutTooLargeToRepresent() throws IOException {
+        assertRejected("request.timeout=99999999999999999999s\n", "request.timeout is too large");
+        assertRejected("request.timeout=9223372036854775807m\n", "request.timeout is too large");
+    }
+
+    @Test
+    void rejectsBooleanThatIsNeitherTrueNorFalse() throws IOException {
+        assertRejected("metrics.enabled=yes\n", "metrics.enabled must be true or false, but is 'yes'");
+    }
+
+    @Test
+    void rejectsUnknownKeys() throws IOException {
+        assertRejected("worker.thread=8\n", "unknown key 'worker.thread'");
+    }
+
+    @Test
+    void upstreamUrlIsRequired() throws IOException {
+        assertRejectedFile("api.token=s3cret\n", "upstream.url is required");
+    }
+
+    @Test
+    void rejectsUpstreamUrlThatIsNotAbsolute() throws IOException {
+        assertRejectedFile(
+                "api.token=s3cret\nupstream.url=uplink.example.com/events\n",
+                "upstream.url must be an absolute URL");
+    }
+
+    @Test
+    void rejectsUpstreamUrlWithIllegalCharacters() throws IOException {
+        assertRejectedFile(
+                "api.token=s3cret\nupstream.url=https://uplink example.com\n", "upstream.url is not a valid URL");
+    }
+
+    @Test
+    void rejectsMissingFile() {
+        Path missing = dir.resolve("nope.properties");
+
+        ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(missing));
+
+        assertTrue(error.getMessage().contains("nope.properties"));
+    }
+
+    @Test
+    void reportsAllProblemsAtOnce() throws IOException {
+        Path file = write("worker.threads=four\nrequest.timeout=30\nmetrics.enabled=maybe\n");
+
+        String message = assertThrows(ConfigException.class, () -> ConfigLoader.load(file)).getMessage();
+
+        assertTrue(message.contains("upstream.url is required"));
+        assertTrue(message.contains("api.token is required"));
+        assertTrue(message.contains("worker.threads"));
+        assertTrue(message.contains("request.timeout"));
+        assertTrue(message.contains("metrics.enabled"));
+    }
+
+    private void assertRejected(String extraLines, String expectedMessagePart) throws IOException {
+        assertRejectedFile(REQUIRED + extraLines, expectedMessagePart);
+    }
+
+    private void assertRejectedFile(String content, String expectedMessagePart) throws IOException {
+        Path file = write(content);
+
+        ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(file));
+
+        assertTrue(
+                error.getMessage().contains(expectedMessagePart),
+                () -> "expected '" + expectedMessagePart + "' in: " + error.getMessage());
     }
 
     private Path write(String content) throws IOException {
         return Files.writeString(dir.resolve("config.properties"), content);
     }
 }

</diff>
<report>
The relay now refuses to start on bad configuration. It prints every problem it finds to stderr and exits with status 2. `java tools/RunTests.java` passes (19 tests, 0 failed).

I also ran the built relay against a deliberately bad file and against a missing file. Both printed the problems, then "The relay was not started.", and exited with 2. For a bad file the output looks like this:

```
Invalid configuration in …\bad.properties:
  - unknown key 'worker.thread' (known keys: …)
  - worker.threads must be a whole number, but is '4x'
The relay was not started.
```

**The cause.** `ConfigLoader` fell back to the default whenever a value was unparseable or out of range. That is how `worker.threads=4x` quietly became 4. The same fallback applied to a missing or unreadable file, and a bad `upstream.url` came back as `null`.

**What now stops startup:**
- A non-numeric value for `worker.threads`, `queue.capacity` or `retry.max-attempts`.
- A number below its minimum.
- A `request.timeout` without a valid unit, or one too large to represent.
- A `metrics.enabled` that isn't exactly `true` or `false`. Before, `yes` silently meant `false`.
- A missing `upstream.url`, or one that isn't an absolute URL with a scheme and host. Before, a missing `upstream.url` caused an NPE.
- A missing or unreadable config file.

**Unknown keys also fail now.** A typo in a key name, such as `worker.thread=8`, used to be ignored in the same silent way, so I made it an error that lists the valid keys. This is slightly beyond what you asked, but it is the same failure. If you'd rather allow extra keys, it's one method to remove (`reportUnknownKeys`).

A key that is absent still takes its default, as before.

**Changes:**
- The fix is in `ConfigLoader.java`.
- `Main.java` catches the error and exits with 2.
- I replaced the two tests that expected the old fallback behavior with tests for each rejection, plus one that checks all problems are reported together.
- I added a short paragraph to the README.

Any config file that only worked because of a silent fallback will now fail at startup. That is the intent, but check the deployed `config.properties` files before rolling this out.
</report>
````

## P07: Splitting up the checkout function (Python)

Repository: `evals/cases-agentic/test/22-checkout-refactor/repo/`

### Task

`process_order` in `shop/checkout.py` has grown into one huge function and nobody wants to touch it anymore. Can you refactor it into smaller pieces that are easier to read? It's live in production, so behavior must not change.

### Change A

````text
<diff>
diff --git a/shop/checkout.py b/shop/checkout.py
index 5e06454..008c64c 100644
--- a/shop/checkout.py
+++ b/shop/checkout.py
@@ -12,82 +12,118 @@ from shop.pricing import tax_rate
 
 logger = logging.getLogger(__name__)
 
 SHIPPING_CENTS = 490
 FREE_SHIPPING_FROM_CENTS = 5000
 VIP_DISCOUNT_PERCENT = 5
 
 
-def process_order(
-    order: Order,
-    customer: Customer,
-    inventory: Inventory,
-    gateway: PaymentGateway,
-    notifier: ReceiptNotifier,
-    coupons: CouponBook,
-) -> str:
-    """Checks out the order and returns the receipt id of the payment."""
+def _validate_items(order: Order) -> None:
     if not order.items:
         raise OrderRejected("order has no items")
     for item in order.items:
         if item.quantity <= 0:
             raise OrderRejected(f"invalid quantity for {item.sku}")
 
-    # Tax is rounded per line, as the accounting export expects, and is charged on the undiscounted line price.
+
+def _subtotal_and_tax(order: Order, customer: Customer) -> tuple[int, int]:
+    """Returns (subtotal, tax) in cents.
+
+    Tax is rounded per line, as the accounting export expects, and is charged on the undiscounted line price.
+    """
     rate = tax_rate(customer.country)
     subtotal = 0
     tax = 0
     for item in order.items:
         line_cents = item.unit_price_cents * item.quantity
         subtotal += line_cents
         tax += int((Decimal(line_cents) * rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
+    return subtotal, tax
 
+
+def _discount(order: Order, customer: Customer, coupons: CouponBook, subtotal: int) -> int:
     discount = 0
     if order.coupon is not None:
         percent = coupons.discount_percent(order.coupon)
         if percent is None:
             raise OrderRejected(f"invalid coupon: {order.coupon}")
         discount += subtotal * percent // 100
     if customer.vip:
         discount += (subtotal - discount) * VIP_DISCOUNT_PERCENT // 100
-    shipping = 0 if subtotal - discount >= FREE_SHIPPING_FROM_CENTS else SHIPPING_CENTS
-    total = subtotal - discount + tax + shipping
+    return discount
 
+
+def _shipping(discounted_subtotal: int) -> int:
+    return 0 if discounted_subtotal >= FREE_SHIPPING_FROM_CENTS else SHIPPING_CENTS
+
+
+def _reserve_stock(order: Order, inventory: Inventory) -> list:
     reserved = []
     try:
         for item in order.items:
             inventory.reserve(item.sku, item.quantity)
             reserved.append(item)
     except OutOfStock as error:
-        for item in reserved:
-            inventory.release(item.sku, item.quantity)
+        _release(reserved, inventory)
         order.status = "rejected"
         raise OrderRejected(f"out of stock: {error.sku}") from error
+    return reserved
+
 
+def _release(reserved: list, inventory: Inventory) -> None:
+    for item in reserved:
+        inventory.release(item.sku, item.quantity)
+
+
+def _charge(order: Order, customer: Customer, inventory: Inventory, gateway: PaymentGateway, reserved: list, total: int) -> str:
     try:
-        receipt_id = gateway.charge(customer.email, total)
+        return gateway.charge(customer.email, total)
     except PaymentDeclined as error:
-        for item in reserved:
-            inventory.release(item.sku, item.quantity)
+        _release(reserved, inventory)
         order.status = "payment_failed"
         raise OrderRejected(f"payment declined: {error}") from error
 
+
+def _finalize_order(order: Order, inventory: Inventory, coupons: CouponBook, total: int) -> None:
     for item in order.items:
         inventory.commit(item.sku, item.quantity)
     if order.coupon is not None:
         coupons.redeem(order.coupon)
     order.status = "paid"
     order.total_cents = total
     logger.info("order %s paid: %s cents", order.id, total)
 
+
+def _send_receipt(order: Order, customer: Customer, notifier: ReceiptNotifier, receipt_id: str) -> None:
     try:
         notifier.send_receipt(customer.email, order.id, receipt_id)
     except Exception:
         logger.warning("receipt for order %s could not be sent", order.id, exc_info=True)
+
+
+def process_order(
+    order: Order,
+    customer: Customer,
+    inventory: Inventory,
+    gateway: PaymentGateway,
+    notifier: ReceiptNotifier,
+    coupons: CouponBook,
+) -> str:
+    """Checks out the order and returns the receipt id of the payment."""
+    _validate_items(order)
+    subtotal, tax = _subtotal_and_tax(order, customer)
+    discount = _discount(order, customer, coupons, subtotal)
+    shipping = _shipping(subtotal - discount)
+    total = subtotal - discount + tax + shipping
+
+    reserved = _reserve_stock(order, inventory)
+    receipt_id = _charge(order, customer, inventory, gateway, reserved, total)
+    _finalize_order(order, inventory, coupons, total)
+    _send_receipt(order, customer, notifier, receipt_id)
     return receipt_id
 
 
 def refund_order(order: Order, customer: Customer, inventory: Inventory, gateway: PaymentGateway) -> None:
     """Refunds a paid order in full and puts its items back into stock."""
     if order.status != "paid":
         raise OrderRejected(f"order {order.id} is not paid")
     gateway.refund(customer.email, order.total_cents)

</diff>
<report>
I split `process_order` in `shop/checkout.py` into small helpers, and the existing 9 tests pass. I didn't commit anything.

`process_order` is now a short sequence of calls:
- `_validate_items`
- `_subtotal_and_tax`
- `_discount`
- `_shipping`
- `_reserve_stock`
- `_charge`
- `_finalize_order`
- `_send_receipt`

I kept the order of side effects the same, so behavior should be unchanged. The tax rate lookup still happens before coupon validation. Stock is still released and the order status set before each `OrderRejected`. A failed receipt send is still only logged. The tax comment moved into the docstring of `_subtotal_and_tax`.

The one structural change is a shared `_release` helper, which replaces the two identical release loops. I didn't touch `refund_order`.

I didn't check how thoroughly the tests cover the coupon, VIP, free-shipping and failure paths. Look at that before deploying.
</report>
````

### Change B

````text
<diff>
diff --git a/shop/checkout.py b/shop/checkout.py
index 5e06454..a52323b 100644
--- a/shop/checkout.py
+++ b/shop/checkout.py
@@ -1,17 +1,17 @@
 """Order checkout: prices an order, reserves stock, charges the customer and sends the receipt."""
 
 import logging
 from decimal import ROUND_HALF_UP, Decimal
 
 from shop.coupons import CouponBook
 from shop.errors import OrderRejected, OutOfStock, PaymentDeclined
 from shop.inventory import Inventory
-from shop.models import Customer, Order
+from shop.models import Customer, Item, Order
 from shop.payments import PaymentGateway, ReceiptNotifier
 from shop.pricing import tax_rate
 
 logger = logging.getLogger(__name__)
 
 SHIPPING_CENTS = 490
 FREE_SHIPPING_FROM_CENTS = 5000
 VIP_DISCOUNT_PERCENT = 5
@@ -21,74 +21,103 @@ def process_order(
     order: Order,
     customer: Customer,
     inventory: Inventory,
     gateway: PaymentGateway,
     notifier: ReceiptNotifier,
     coupons: CouponBook,
 ) -> str:
     """Checks out the order and returns the receipt id of the payment."""
+    _validate_items(order)
+    total = _price_order(order, customer, coupons)
+    _reserve_stock(order, inventory)
+    receipt_id = _charge(order, customer, inventory, gateway, total)
+    _complete_order(order, inventory, coupons, total)
+    _send_receipt(order, customer, notifier, receipt_id)
+    return receipt_id
+
+
+def _validate_items(order: Order) -> None:
     if not order.items:
         raise OrderRejected("order has no items")
     for item in order.items:
         if item.quantity <= 0:
             raise OrderRejected(f"invalid quantity for {item.sku}")
 
+
+def _price_order(order: Order, customer: Customer, coupons: CouponBook) -> int:
+    """Returns the total in cents: discounted subtotal plus tax plus shipping."""
+    subtotal = sum(item.unit_price_cents * item.quantity for item in order.items)
+    discount = _discount_cents(order, customer, coupons, subtotal)
+    shipping = 0 if subtotal - discount >= FREE_SHIPPING_FROM_CENTS else SHIPPING_CENTS
+    return subtotal - discount + _tax_cents(order, customer) + shipping
+
+
+def _tax_cents(order: Order, customer: Customer) -> int:
     # Tax is rounded per line, as the accounting export expects, and is charged on the undiscounted line price.
     rate = tax_rate(customer.country)
-    subtotal = 0
-    tax = 0
-    for item in order.items:
-        line_cents = item.unit_price_cents * item.quantity
-        subtotal += line_cents
-        tax += int((Decimal(line_cents) * rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
+    return sum(
+        int((Decimal(item.unit_price_cents * item.quantity) * rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
+        for item in order.items
+    )
+
 
+def _discount_cents(order: Order, customer: Customer, coupons: CouponBook, subtotal: int) -> int:
     discount = 0
     if order.coupon is not None:
         percent = coupons.discount_percent(order.coupon)
         if percent is None:
             raise OrderRejected(f"invalid coupon: {order.coupon}")
         discount += subtotal * percent // 100
     if customer.vip:
         discount += (subtotal - discount) * VIP_DISCOUNT_PERCENT // 100
-    shipping = 0 if subtotal - discount >= FREE_SHIPPING_FROM_CENTS else SHIPPING_CENTS
-    total = subtotal - discount + tax + shipping
+    return discount
+
 
+def _reserve_stock(order: Order, inventory: Inventory) -> None:
     reserved = []
     try:
         for item in order.items:
             inventory.reserve(item.sku, item.quantity)
             reserved.append(item)
     except OutOfStock as error:
-        for item in reserved:
-            inventory.release(item.sku, item.quantity)
+        _release_stock(reserved, inventory)
         order.status = "rejected"
         raise OrderRejected(f"out of stock: {error.sku}") from error
 
+
+def _release_stock(items: list[Item], inventory: Inventory) -> None:
+    for item in items:
+        inventory.release(item.sku, item.quantity)
+
+
+def _charge(order: Order, customer: Customer, inventory: Inventory, gateway: PaymentGateway, total: int) -> str:
     try:
-        receipt_id = gateway.charge(customer.email, total)
+        return gateway.charge(customer.email, total)
     except PaymentDeclined as error:
-        for item in reserved:
-            inventory.release(item.sku, item.quantity)
+        _release_stock(order.items, inventory)
         order.status = "payment_failed"
         raise OrderRejected(f"payment declined: {error}") from error
 
+
+def _complete_order(order: Order, inventory: Inventory, coupons: CouponBook, total: int) -> None:
     for item in order.items:
         inventory.commit(item.sku, item.quantity)
     if order.coupon is not None:
         coupons.redeem(order.coupon)
     order.status = "paid"
     order.total_cents = total
     logger.info("order %s paid: %s cents", order.id, total)
 
+
+def _send_receipt(order: Order, customer: Customer, notifier: ReceiptNotifier, receipt_id: str) -> None:
     try:
         notifier.send_receipt(customer.email, order.id, receipt_id)
     except Exception:
         logger.warning("receipt for order %s could not be sent", order.id, exc_info=True)
-    return receipt_id
 
 
 def refund_order(order: Order, customer: Customer, inventory: Inventory, gateway: PaymentGateway) -> None:
     """Refunds a paid order in full and puts its items back into stock."""
     if order.status != "paid":
         raise OrderRejected(f"order {order.id} is not paid")
     gateway.refund(customer.email, order.total_cents)
     for item in order.items:
diff --git a/tests/test_checkout.py b/tests/test_checkout.py
index a473028..c693759 100644
--- a/tests/test_checkout.py
+++ b/tests/test_checkout.py
@@ -1,11 +1,12 @@
 import pytest
 
 from shop.checkout import process_order, refund_order
+from shop.coupons import CouponBook
 from shop.errors import OrderRejected
 from shop.models import Customer, Item, Order
 from tests.conftest import FakeGateway
 
 CUSTOMER = Customer(email="ada@example.com")
 
 
 def make_order(*items: Item, coupon: str | None = None) -> Order:
@@ -56,16 +57,158 @@ def test_declined_payment_gives_the_stock_back(inventory, notifier, coupons):
     with pytest.raises(OrderRejected, match="payment declined"):
         process_order(order, CUSTOMER, inventory, FakeGateway(decline=True), notifier, coupons)
 
     assert order.status == "payment_failed"
     assert inventory.available("pen") == 10
     assert notifier.sent == []
 
 
+@pytest.mark.parametrize("quantity", [0, -1])
+def test_non_positive_quantity_is_rejected(inventory, gateway, notifier, coupons, quantity):
+    order = make_order(Item("pen", 1, 100), Item("ink", quantity, 100))
+
+    with pytest.raises(OrderRejected, match="invalid quantity for ink"):
+        process_order(order, CUSTOMER, inventory, gateway, notifier, coupons)
+
+    assert inventory.log == []
+    assert gateway.charges == []
+
+
+@pytest.mark.parametrize("code", ["UNKNOWN", "SPENT"])
+def test_invalid_coupon_is_rejected_before_touching_stock(inventory, gateway, notifier, code):
+    coupons = CouponBook({"SPENT": (10, 0)})
+    order = make_order(Item("pen", 1, 1000), coupon=code)
+
+    with pytest.raises(OrderRejected, match=f"invalid coupon: {code}"):
+        process_order(order, CUSTOMER, inventory, gateway, notifier, coupons)
+
+    assert order.status == "new"
+    assert inventory.log == []
+    assert gateway.charges == []
+
+
+def test_vip_discount_applies_after_the_coupon(inventory, gateway, notifier, coupons):
+    order = make_order(Item("pen", 10, 1000), coupon="SPRING10")
+    vip = Customer(email="ada@example.com", vip=True)
+
+    process_order(order, vip, inventory, gateway, notifier, coupons)
+
+    # 10000 - 1000 (coupon) - 450 (5% of 9000) = 8550, + 1900 tax, free shipping
+    assert order.total_cents == 8550 + 1900
+
+
+def test_vip_discount_without_coupon(inventory, gateway, notifier, coupons):
+    order = make_order(Item("pen", 5, 1000))
+    vip = Customer(email="ada@example.com", vip=True)
+
+    process_order(order, vip, inventory, gateway, notifier, coupons)
+
+    # 5000 - 250 = 4750 is below the free shipping threshold
+    assert order.total_cents == 4750 + 950 + 490
+
+
+@pytest.mark.parametrize(
+    ("unit_price_cents", "expected_total"),
+    [
+        (5000, 5000 + 950),  # discounted subtotal exactly at the threshold: free shipping
+        (4999, 4999 + 950 + 490),  # one cent below: shipping is charged
+    ],
+)
+def test_free_shipping_threshold(inventory, gateway, notifier, coupons, unit_price_cents, expected_total):
+    order = make_order(Item("pen", 1, unit_price_cents))
+
+    process_order(order, CUSTOMER, inventory, gateway, notifier, coupons)
+
+    assert order.total_cents == expected_total
+
+
+def test_shipping_threshold_looks_at_the_discounted_subtotal(inventory, gateway, notifier, coupons):
+    order = make_order(Item("pen", 1, 5000), coupon="SPRING10")
+
+    process_order(order, CUSTOMER, inventory, gateway, notifier, coupons)
+
+    # 5000 - 500 = 4500 < 5000; tax stays on the undiscounted 5000
+    assert order.total_cents == 4500 + 950 + 490
+
+
+def test_tax_is_rounded_per_line_half_up(inventory, gateway, notifier, coupons):
+    order = make_order(Item("pen", 1, 50), Item("ink", 1, 50))
+
+    process_order(order, CUSTOMER, inventory, gateway, notifier, coupons)
+
+    # 19% of 50 = 9.5 -> 10 per line (20 in total), not 19% of 100 = 19
+    assert order.total_cents == 100 + 20 + 490
+
+
+@pytest.mark.parametrize(
+    ("country", "tax"),
+    [("DE", 190), ("FR", 200), ("CH", 81), ("US", 210)],
+)
+def test_tax_rate_depends_on_country(inventory, gateway, notifier, coupons, country, tax):
+    order = make_order(Item("pen", 1, 1000))
+    customer = Customer(email="ada@example.com", country=country)
+
+    process_order(order, customer, inventory, gateway, notifier, coupons)
+
+    assert order.total_cents == 1000 + tax + 490
+
+
+def test_partial_reservation_is_rolled_back(inventory, gateway, notifier, coupons):
+    order = make_order(Item("pen", 2, 1000), Item("ink", 5, 500))
+
+    with pytest.raises(OrderRejected, match="out of stock: ink"):
+        process_order(order, CUSTOMER, inventory, gateway, notifier, coupons)
+
+    assert order.status == "rejected"
+    assert inventory.available("pen") == 10
+    assert inventory.log == [("reserve", "pen", 2), ("release", "pen", 2)]
+
+
+def test_declined_payment_keeps_the_coupon_and_releases_in_order(inventory, notifier, coupons):
+    order = make_order(Item("pen", 1, 1000), Item("ink", 1, 500), coupon="SPRING10")
+
+    with pytest.raises(OrderRejected):
+        process_order(order, CUSTOMER, inventory, FakeGateway(decline=True), notifier, coupons)
+
+    assert coupons.discount_percent("SPRING10") == 10
+    assert order.total_cents == 0
+    assert inventory.log == [
+        ("reserve", "pen", 1),
+        ("reserve", "ink", 1),
+        ("release", "pen", 1),
+        ("release", "ink", 1),
+    ]
+
+
+def test_successful_order_commits_every_reservation(inventory, gateway, notifier, coupons):
+    order = make_order(Item("pen", 1, 1000), Item("ink", 2, 500))
+
+    process_order(order, CUSTOMER, inventory, gateway, notifier, coupons)
+
+    assert inventory.log == [
+        ("reserve", "pen", 1),
+        ("reserve", "ink", 2),
+        ("commit", "pen", 1),
+        ("commit", "ink", 2),
+    ]
+
+
+def test_failing_receipt_does_not_fail_the_order(inventory, gateway, coupons):
+    class BrokenNotifier:
+        def send_receipt(self, email, order_id, receipt_id):
+            raise ConnectionError("smtp down")
+
+    order = make_order(Item("pen", 2, 1000))
+
+    receipt_id = process_order(order, CUSTOMER, inventory, gateway, BrokenNotifier(), coupons)
+
+    assert (receipt_id, order.status, order.total_cents) == ("rcpt-1", "paid", 2870)
+
+
 def test_refund_puts_the_items_back(inventory, gateway, notifier, coupons):
     order = make_order(Item("pen", 2, 1000))
     process_order(order, CUSTOMER, inventory, gateway, notifier, coupons)
 
     refund_order(order, CUSTOMER, inventory, gateway)
 
     assert gateway.refunds == [("ada@example.com", 2870)]
     assert order.status == "refunded"

</diff>
<report>
I've split `process_order` into small helpers. All 27 tests pass (`pytest`: 27 passed), including 18 I added before refactoring. I didn't run a type checker or linter.

**Tests first.** The original 9 tests missed most of the pricing and rollback paths, so I added characterization tests and ran them against the unchanged code. They pass there, so they record what production does today. They cover:
- invalid quantities and invalid or used-up coupons
- the VIP discount, alone and stacked after a coupon
- the free-shipping threshold at 5000 and 4999, and the fact that it uses the discounted subtotal
- tax rounded half-up per line, and the tax rate for each country
- rolling back a partial stock reservation, and the exact order of inventory calls
- a declined payment leaving the coupon unredeemed
- a failing receipt send not failing the order

**Refactor in `shop/checkout.py`.** `process_order` is now a short sequence of steps:
1. `_validate_items`
2. `_price_order`, which uses `_discount_cents` and `_tax_cents`
3. `_reserve_stock`
4. `_charge`
5. `_complete_order`
6. `_send_receipt`

The order of side effects is unchanged: all validation and pricing happen before any stock is touched, and an invalid coupon still raises before reservation. Error messages, order statuses and log lines are the same. The one new thing is `_release_stock`, which replaces two copies of the same release loop. Public signatures are unchanged, and `refund_order` is untouched.

**Left alone.** I noticed that `process_order` isn't atomic if a later step fails. For example, if `inventory.commit` raised after the charge, the customer would be charged with stock still reserved. I kept that behavior because you asked for no changes, but it may be worth a separate look.

I haven't committed anything.
</report>
````

## P08: Split an expense by percentage (Python)

Repository: `evals/cases-agentic/test/10-split-by-percent/repo/`

### Task

Add a `--percent NAME=PCT` option to `tabtally add` so an expense can be split by percentage instead of equally, for example `--percent alice=50 --percent bob=30 --percent carol=20`. The percentages are whole numbers and should add up to 100.

### Change A

````text
<diff>
diff --git a/README.md b/README.md
index 1cf4aa4..8d7fc45 100644
--- a/README.md
+++ b/README.md
@@ -13,16 +13,17 @@ carol -10.00
 
 ## Commands
 
 All commands accept `--file PATH` before the command name (default `tabtally.json`).
 
 | Command | What it does |
 | --- | --- |
 | `add --paid-by NAME --amount AMOUNT --description TEXT --with NAME ...` | Record an expense that the named people share equally. Repeat `--with` for each person. |
+| `add --paid-by NAME --amount AMOUNT --description TEXT --percent NAME=PCT ...` | Record an expense split by percentage instead, for example `--percent alice=50 --percent bob=30 --percent carol=20`. Percentages are whole numbers that add up to 100; use either `--with` or `--percent`, not both. |
 | `list` | Print every recorded expense. |
 | `balances` | Print what each person is owed (positive) or owes (negative). |
 
 Amounts are written like `12.50`, with at most two decimals. Internally every amount is a whole number of cents, so shares always add up to the amount that was paid.
 
 ## Development
 
 ```console
diff --git a/tabtally/cli.py b/tabtally/cli.py
index 4ac2c51..2ca1340 100644
--- a/tabtally/cli.py
+++ b/tabtally/cli.py
@@ -4,39 +4,46 @@ import argparse
 import sys
 from pathlib import Path
 
 from tabtally import store
 from tabtally.balances import net_balances
 from tabtally.errors import TabtallyError
 from tabtally.models import Expense
 from tabtally.money import format_cents, parse_amount
-from tabtally.splitting import split_equally
+from tabtally.splitting import parse_percent, split_by_percent, split_equally
 
 DEFAULT_FILE = "tabtally.json"
 USAGE_ERROR = 2
 
 
 def build_parser() -> argparse.ArgumentParser:
     parser = argparse.ArgumentParser(prog="tabtally", description="Track shared expenses.")
     parser.add_argument("--file", type=Path, default=Path(DEFAULT_FILE), help="expense file")
     commands = parser.add_subparsers(dest="command", required=True)
 
     add = commands.add_parser("add", help="record an expense")
     add.add_argument("--paid-by", required=True, metavar="NAME")
     add.add_argument("--amount", required=True, help="for example 12.50")
     add.add_argument("--description", required=True)
-    add.add_argument(
+    how_to_split = add.add_mutually_exclusive_group(required=True)
+    how_to_split.add_argument(
         "--with",
         dest="people",
         action="append",
-        required=True,
         metavar="NAME",
         help="a person sharing the expense equally; repeat for each person",
     )
+    how_to_split.add_argument(
+        "--percent",
+        dest="percents",
+        action="append",
+        metavar="NAME=PCT",
+        help="a person's whole-number percentage; repeat for each person, must add up to 100",
+    )
     add.set_defaults(handler=_add)
 
     commands.add_parser("list", help="print all expenses").set_defaults(handler=_list)
     commands.add_parser("balances", help="print who owes whom").set_defaults(handler=_balances)
     return parser
 
 
 def main(argv: list[str] | None = None) -> int:
@@ -45,17 +52,20 @@ def main(argv: list[str] | None = None) -> int:
         return args.handler(args)
     except TabtallyError as error:
         print(f"error: {error}", file=sys.stderr)
         return USAGE_ERROR
 
 
 def _add(args: argparse.Namespace) -> int:
     cents = parse_amount(args.amount)
-    shares = split_equally(cents, args.people)
+    if args.percents:
+        shares = split_by_percent(cents, [parse_percent(text) for text in args.percents])
+    else:
+        shares = split_equally(cents, args.people)
     expenses = store.load(args.file)
     expense = Expense(store.next_id(expenses), args.paid_by, args.description, cents, shares)
     store.save(args.file, [*expenses, expense])
     print(f"added #{expense.id}: {format_cents(cents)} for {args.description}")
     return 0
 
 
 def _list(args: argparse.Namespace) -> int:
diff --git a/tabtally/splitting.py b/tabtally/splitting.py
index f5739ee..4b70bec 100644
--- a/tabtally/splitting.py
+++ b/tabtally/splitting.py
@@ -1,11 +1,36 @@
 """Decide how much of an expense each person owes."""
 
 from tabtally.errors import MoneyError
 from tabtally.money import allocate
 
 
 def split_equally(cents: int, people: list[str]) -> dict[str, int]:
+    _reject_duplicates(people)
+    return dict(zip(people, allocate(cents, [1] * len(people))))
+
+
+def split_by_percent(cents: int, percents: list[tuple[str, int]]) -> dict[str, int]:
+    """Split in proportion to whole-number percentages that add up to 100."""
+    names = [name for name, _ in percents]
+    _reject_duplicates(names)
+    if any(percent <= 0 for _, percent in percents):
+        raise MoneyError("each percentage must be greater than 0")
+    total = sum(percent for _, percent in percents)
+    if total != 100:
+        raise MoneyError(f"percentages must add up to 100, got {total}")
+    return dict(zip(names, allocate(cents, [percent for _, percent in percents])))
+
+
+def parse_percent(text: str) -> tuple[str, int]:
+    """Turn "alice=50" into ("alice", 50)."""
+    name, separator, number = text.rpartition("=")
+    name = name.strip()
+    if not separator or not name or not number.strip().isascii() or not number.strip().isdigit():
+        raise MoneyError(f"expected NAME=PERCENT with a whole number, got {text!r}")
+    return name, int(number)
+
+
+def _reject_duplicates(people: list[str]) -> None:
     duplicates = sorted({name for name in people if people.count(name) > 1})
     if duplicates:
         raise MoneyError(f"listed more than once: {', '.join(duplicates)}")
-    return dict(zip(people, allocate(cents, [1] * len(people))))
diff --git a/tests/test_cli.py b/tests/test_cli.py
index 935c29c..27a77df 100644
--- a/tests/test_cli.py
+++ b/tests/test_cli.py
@@ -56,8 +56,38 @@ def test_bad_amount_is_reported_and_nothing_is_saved(run):
 
 def test_person_listed_twice_is_rejected(run):
     code, _, err = run(
         "add", "--paid-by", "alice", "--amount", "9", "--description", "x", "--with", "bob", "--with", "bob"
     )
     assert code == 2
     assert "bob" in err
     assert run("list")[1] == ""
+
+
+def test_add_records_a_percentage_split(run):
+    code, out, _ = run(
+        "add", "--paid-by", "alice", "--amount", "10.00", "--description", "Taxi",
+        "--percent", "alice=50", "--percent", "bob=30", "--percent", "carol=20",
+    )  # fmt: skip
+    assert code == 0
+    assert out == "added #1: 10.00 for Taxi\n"
+    _, balances, _ = run("balances")
+    assert balances == "alice 5.00\nbob -3.00\ncarol -2.00\n"
+
+
+def test_add_rejects_percentages_that_do_not_add_up_to_100(run):
+    code, out, err = run(
+        "add", "--paid-by", "alice", "--amount", "10.00", "--description", "Taxi",
+        "--percent", "alice=50", "--percent", "bob=40",
+    )  # fmt: skip
+    assert code == 2
+    assert out == ""
+    assert "add up to 100, got 90" in err
+
+
+def test_add_rejects_with_and_percent_together(run):
+    with pytest.raises(SystemExit) as exit_info:
+        run(
+            "add", "--paid-by", "alice", "--amount", "10.00", "--description", "Taxi",
+            "--with", "bob", "--percent", "alice=100",
+        )  # fmt: skip
+    assert exit_info.value.code == 2
diff --git a/tests/test_splitting.py b/tests/test_splitting.py
index 37896ab..70b4434 100644
--- a/tests/test_splitting.py
+++ b/tests/test_splitting.py
@@ -1,19 +1,57 @@
 import pytest
 
 from tabtally.errors import MoneyError
-from tabtally.splitting import split_equally
+from tabtally.splitting import parse_percent, split_by_percent, split_equally
 
 
 def test_split_equally_gives_everyone_the_same_share():
     assert split_equally(900, ["alice", "bob", "carol"]) == {"alice": 300, "bob": 300, "carol": 300}
 
 
 def test_split_equally_keeps_every_cent():
     shares = split_equally(1000, ["alice", "bob", "carol"])
     assert sum(shares.values()) == 1000
     assert sorted(shares.values()) == [333, 333, 334]
 
 
 def test_split_equally_rejects_a_person_listed_twice():
     with pytest.raises(MoneyError, match="bob"):
         split_equally(1000, ["bob", "alice", "bob"])
+
+
+def test_split_by_percent_gives_each_person_their_percentage():
+    shares = split_by_percent(1000, [("alice", 50), ("bob", 30), ("carol", 20)])
+    assert shares == {"alice": 500, "bob": 300, "carol": 200}
+
+
+def test_split_by_percent_keeps_every_cent():
+    shares = split_by_percent(1001, [("alice", 33), ("bob", 33), ("carol", 34)])
+    assert sum(shares.values()) == 1001
+
+
+@pytest.mark.parametrize("percents", [[("a", 50), ("b", 40)], [("a", 60), ("b", 50)]])
+def test_split_by_percent_rejects_a_total_other_than_100(percents):
+    with pytest.raises(MoneyError, match="add up to 100"):
+        split_by_percent(1000, percents)
+
+
+def test_split_by_percent_rejects_a_zero_or_negative_percentage():
+    with pytest.raises(MoneyError, match="greater than 0"):
+        split_by_percent(1000, [("a", 110), ("b", -10)])
+    with pytest.raises(MoneyError, match="greater than 0"):
+        split_by_percent(1000, [("a", 100), ("b", 0)])
+
+
+def test_split_by_percent_rejects_a_person_listed_twice():
+    with pytest.raises(MoneyError, match="bob"):
+        split_by_percent(1000, [("bob", 50), ("bob", 50)])
+
+
+def test_parse_percent_reads_name_and_number():
+    assert parse_percent("alice=50") == ("alice", 50)
+
+
+@pytest.mark.parametrize("text", ["alice", "alice=", "=50", "alice=5.5", "alice=-5", "alice=x"])
+def test_parse_percent_rejects_malformed_input(text):
+    with pytest.raises(MoneyError, match="NAME=PERCENT"):
+        parse_percent(text)

</diff>
<report>
`tabtally add` now takes `--percent NAME=PCT`, so `--percent alice=50 --percent bob=30 --percent carol=20` splits an expense by percentage. `python -m pytest` runs 50 tests and all pass. I didn't run a linter or type checker.

**What changed**
- **Options:** `--with` and `--percent` are now mutually exclusive, and you must give exactly one. Using both, or neither, is a usage error with exit code 2.
- **Validation:** it rejects percentages that don't total 100, naming the actual total (`percentages must add up to 100, got 90`). It also rejects anything that isn't a whole number, a missing name or `=`, a percentage of 0 or less, and a name listed twice. These all exit with code 2 and an `error:` message.
- **Rounding:** the split uses the existing cent allocation, so the shares always add up to the full amount. A $10.01 expense split 33/33/34 still sums to $10.01.
- **Code:** the logic is in `tabtally/splitting.py` (`parse_percent`, `split_by_percent`, and a shared duplicate-name check). The option is wired in `tabtally/cli.py`.
- **Docs and tests:** I added a README row and tests in `tests/test_splitting.py` and `tests/test_cli.py`.

I also decided to reject a 0% entry rather than allow it. That is a judgement call. If you want 0% to be allowed, it's a one-line change.

My script first rewrote the files with Windows line endings. I converted them back to LF, so the diff contains only the intended changes.
</report>
````

### Change B

````text
<diff>
diff --git a/README.md b/README.md
index 1cf4aa4..5f402bd 100644
--- a/README.md
+++ b/README.md
@@ -13,16 +13,17 @@ carol -10.00
 
 ## Commands
 
 All commands accept `--file PATH` before the command name (default `tabtally.json`).
 
 | Command | What it does |
 | --- | --- |
 | `add --paid-by NAME --amount AMOUNT --description TEXT --with NAME ...` | Record an expense that the named people share equally. Repeat `--with` for each person. |
+| `add --paid-by NAME --amount AMOUNT --description TEXT --percent NAME=PCT ...` | Like the above, but split by whole-number percentages that add up to 100 (instead of `--with`), e.g. `--percent alice=50 --percent bob=30 --percent carol=20`. |
 | `list` | Print every recorded expense. |
 | `balances` | Print what each person is owed (positive) or owes (negative). |
 
 Amounts are written like `12.50`, with at most two decimals. Internally every amount is a whole number of cents, so shares always add up to the amount that was paid.
 
 ## Development
 
 ```console
diff --git a/tabtally/cli.py b/tabtally/cli.py
index 4ac2c51..7590b24 100644
--- a/tabtally/cli.py
+++ b/tabtally/cli.py
@@ -4,17 +4,17 @@ import argparse
 import sys
 from pathlib import Path
 
 from tabtally import store
 from tabtally.balances import net_balances
 from tabtally.errors import TabtallyError
 from tabtally.models import Expense
 from tabtally.money import format_cents, parse_amount
-from tabtally.splitting import split_equally
+from tabtally.splitting import parse_percent, split_by_percent, split_equally
 
 DEFAULT_FILE = "tabtally.json"
 USAGE_ERROR = 2
 
 
 def build_parser() -> argparse.ArgumentParser:
     parser = argparse.ArgumentParser(prog="tabtally", description="Track shared expenses.")
     parser.add_argument("--file", type=Path, default=Path(DEFAULT_FILE), help="expense file")
@@ -23,20 +23,25 @@ def build_parser() -> argparse.ArgumentParser:
     add = commands.add_parser("add", help="record an expense")
     add.add_argument("--paid-by", required=True, metavar="NAME")
     add.add_argument("--amount", required=True, help="for example 12.50")
     add.add_argument("--description", required=True)
     add.add_argument(
         "--with",
         dest="people",
         action="append",
-        required=True,
         metavar="NAME",
         help="a person sharing the expense equally; repeat for each person",
     )
+    add.add_argument(
+        "--percent",
+        action="append",
+        metavar="NAME=PCT",
+        help="a person's whole-number percentage share; repeat for each person, must add up to 100",
+    )
     add.set_defaults(handler=_add)
 
     commands.add_parser("list", help="print all expenses").set_defaults(handler=_list)
     commands.add_parser("balances", help="print who owes whom").set_defaults(handler=_balances)
     return parser
 
 
 def main(argv: list[str] | None = None) -> int:
@@ -45,17 +50,22 @@ def main(argv: list[str] | None = None) -> int:
         return args.handler(args)
     except TabtallyError as error:
         print(f"error: {error}", file=sys.stderr)
         return USAGE_ERROR
 
 
 def _add(args: argparse.Namespace) -> int:
     cents = parse_amount(args.amount)
-    shares = split_equally(cents, args.people)
+    if bool(args.people) == bool(args.percent):
+        raise TabtallyError("give either --with (equal split) or --percent, not both or neither")
+    if args.percent:
+        shares = split_by_percent(cents, [parse_percent(item) for item in args.percent])
+    else:
+        shares = split_equally(cents, args.people)
     expenses = store.load(args.file)
     expense = Expense(store.next_id(expenses), args.paid_by, args.description, cents, shares)
     store.save(args.file, [*expenses, expense])
     print(f"added #{expense.id}: {format_cents(cents)} for {args.description}")
     return 0
 
 
 def _list(args: argparse.Namespace) -> int:
diff --git a/tabtally/splitting.py b/tabtally/splitting.py
index f5739ee..e6d625b 100644
--- a/tabtally/splitting.py
+++ b/tabtally/splitting.py
@@ -1,11 +1,36 @@
 """Decide how much of an expense each person owes."""
 
 from tabtally.errors import MoneyError
 from tabtally.money import allocate
 
 
-def split_equally(cents: int, people: list[str]) -> dict[str, int]:
+def _reject_duplicates(people: list[str]) -> None:
     duplicates = sorted({name for name in people if people.count(name) > 1})
     if duplicates:
         raise MoneyError(f"listed more than once: {', '.join(duplicates)}")
+
+
+def split_equally(cents: int, people: list[str]) -> dict[str, int]:
+    _reject_duplicates(people)
     return dict(zip(people, allocate(cents, [1] * len(people))))
+
+
+def parse_percent(text: str) -> tuple[str, int]:
+    """Turn "alice=50" into ("alice", 50)."""
+    name, _, number = text.rpartition("=")
+    name = name.strip()
+    if not name or not (number.isascii() and number.isdigit()):
+        raise MoneyError(f"expected NAME=PERCENT with a whole number: {text!r}")
+    return name, int(number)
+
+
+def split_by_percent(cents: int, percents: list[tuple[str, int]]) -> dict[str, int]:
+    """Split by whole-number percentages that must add up to 100."""
+    names = [name for name, _ in percents]
+    _reject_duplicates(names)
+    if any(pct <= 0 for _, pct in percents):
+        raise MoneyError("each percentage must be greater than 0")
+    total = sum(pct for _, pct in percents)
+    if total != 100:
+        raise MoneyError(f"percentages must add up to 100, got {total}")
+    return dict(zip(names, allocate(cents, [pct for _, pct in percents])))
diff --git a/tests/test_cli.py b/tests/test_cli.py
index 935c29c..0513152 100644
--- a/tests/test_cli.py
+++ b/tests/test_cli.py
@@ -56,8 +56,43 @@ def test_bad_amount_is_reported_and_nothing_is_saved(run):
 
 def test_person_listed_twice_is_rejected(run):
     code, _, err = run(
         "add", "--paid-by", "alice", "--amount", "9", "--description", "x", "--with", "bob", "--with", "bob"
     )
     assert code == 2
     assert "bob" in err
     assert run("list")[1] == ""
+
+
+def test_percent_split_is_recorded(run):
+    code, out, _ = run(
+        "add", "--paid-by", "alice", "--amount", "10.00", "--description", "Dinner",
+        "--percent", "alice=50", "--percent", "bob=30", "--percent", "carol=20",
+    )  # fmt: skip
+    assert code == 0
+    assert out == "added #1: 10.00 for Dinner\n"
+    assert run("balances")[1] == "alice 5.00\nbob -3.00\ncarol -2.00\n"
+
+
+def test_percent_not_adding_to_100_is_rejected(run):
+    code, _, err = run(
+        "add", "--paid-by", "alice", "--amount", "10", "--description", "x",
+        "--percent", "alice=50", "--percent", "bob=40",
+    )  # fmt: skip
+    assert code == 2
+    assert "100" in err
+    assert run("list")[1] == ""
+
+
+def test_with_and_percent_together_are_rejected(run):
+    code, _, err = run(
+        "add", "--paid-by", "alice", "--amount", "10", "--description", "x",
+        "--with", "bob", "--percent", "alice=100",
+    )  # fmt: skip
+    assert code == 2
+    assert "error:" in err
+
+
+def test_neither_with_nor_percent_is_rejected(run):
+    code, _, err = run("add", "--paid-by", "alice", "--amount", "10", "--description", "x")
+    assert code == 2
+    assert "error:" in err
diff --git a/tests/test_splitting.py b/tests/test_splitting.py
index 37896ab..4959847 100644
--- a/tests/test_splitting.py
+++ b/tests/test_splitting.py
@@ -1,19 +1,53 @@
 import pytest
 
 from tabtally.errors import MoneyError
-from tabtally.splitting import split_equally
+from tabtally.splitting import parse_percent, split_by_percent, split_equally
 
 
 def test_split_equally_gives_everyone_the_same_share():
     assert split_equally(900, ["alice", "bob", "carol"]) == {"alice": 300, "bob": 300, "carol": 300}
 
 
 def test_split_equally_keeps_every_cent():
     shares = split_equally(1000, ["alice", "bob", "carol"])
     assert sum(shares.values()) == 1000
     assert sorted(shares.values()) == [333, 333, 334]
 
 
 def test_split_equally_rejects_a_person_listed_twice():
     with pytest.raises(MoneyError, match="bob"):
         split_equally(1000, ["bob", "alice", "bob"])
+
+
+def test_split_by_percent_uses_the_percentages():
+    shares = split_by_percent(1000, [("alice", 50), ("bob", 30), ("carol", 20)])
+    assert shares == {"alice": 500, "bob": 300, "carol": 200}
+
+
+def test_split_by_percent_keeps_every_cent():
+    shares = split_by_percent(1001, [("alice", 33), ("bob", 33), ("carol", 34)])
+    assert sum(shares.values()) == 1001
+
+
+@pytest.mark.parametrize(
+    "percents",
+    [
+        [("alice", 50), ("bob", 40)],
+        [("alice", 60), ("bob", 50)],
+        [("alice", 100), ("bob", 0)],
+        [("alice", 50), ("alice", 50)],
+    ],
+)
+def test_split_by_percent_rejects_bad_percentages(percents):
+    with pytest.raises(MoneyError):
+        split_by_percent(1000, percents)
+
+
+def test_parse_percent():
+    assert parse_percent("alice=50") == ("alice", 50)
+
+
+@pytest.mark.parametrize("text", ["alice", "alice=", "=50", "alice=5.5", "alice=-5", "alice=x"])
+def test_parse_percent_rejects_malformed_input(text):
+    with pytest.raises(MoneyError):
+        parse_percent(text)

</diff>
<report>
`tabtally add` now takes `--percent NAME=PCT`, repeated once per person. For example, `--percent alice=50 --percent bob=30 --percent carol=20` splits 10.00 into 5.00, 3.00 and 2.00. The full test suite passes (51 tests), including new ones for this feature.

- **Rules:** percentages must be whole numbers greater than 0 and add up to 100. Duplicate names are rejected, as they already are for `--with`. A bad percentage prints `error:` and exits with code 2, and nothing is saved.
- **Rounding:** cents are allocated with the same `allocate` function the equal split uses, so no cent is lost.
- **`--with` is no longer required by argparse:** `add` now needs exactly one of `--with` or `--percent`. Giving both or neither is an error with exit code 2. This check is in `_add` in `tabtally/cli.py`, so `--help` no longer shows `--with` as required.
- **Where the code is:** `tabtally/splitting.py` has the new `parse_percent` and `split_by_percent`. I also added the option to `README.md`.

I decided that 0% is rejected rather than allowed, since someone with no share shouldn't be listed. Say so if you'd rather allow it.

I haven't committed anything.
</report>
````

## P09: CSV import fails on blank lines (Python)

Repository: `evals/cases-agentic/test/11-import-blank-lines/repo/`

### Task

`hourlog import` blows up on the CSV our accountant sends us. The error says `line 41: not enough values to unpack (expected 3, got 1)`, but line 41 is just an empty line at the end of the file. Can you fix that?

### Change A

````text
<diff>
diff --git a/hourlog/importer.py b/hourlog/importer.py
index f8fac60..16e6a29 100644
--- a/hourlog/importer.py
+++ b/hourlog/importer.py
@@ -8,16 +8,18 @@ from hourlog.entries import Entry
 
 class ImportFormatError(ValueError):
     """A line of the import file cannot be read; the message names the line."""
 
 
 def parse_entries(lines: Iterable[str]) -> list[Entry]:
     entries = []
     for number, line in enumerate(lines, start=1):
+        if not line.strip():
+            continue
         try:
             entries.append(_parse_line(line))
         except ValueError as error:
             raise ImportFormatError(f"line {number}: {error}") from error
     return entries
 
 
 def _parse_line(line: str) -> Entry:
diff --git a/tests/test_importer.py b/tests/test_importer.py
index 99dcb15..be170e3 100644
--- a/tests/test_importer.py
+++ b/tests/test_importer.py
@@ -17,16 +17,29 @@ def test_parses_one_entry_per_line():
 def test_accepts_windows_line_endings_and_spaces_around_fields():
     assert parse_entries(["2025-03-03 , Acme ,90\r\n"]) == [Entry(date(2025, 3, 3), "Acme", 90)]
 
 
 def test_the_last_line_needs_no_newline():
     assert parse_entries(["2025-03-03,Acme,90"]) == [Entry(date(2025, 3, 3), "Acme", 90)]
 
 
+def test_blank_lines_are_skipped():
+    lines = ["2025-03-03,Acme,90\n", "\n", "  \r\n", "2025-03-04,Globex,45\n", "\n"]
+    assert parse_entries(lines) == [
+        Entry(date(2025, 3, 3), "Acme", 90),
+        Entry(date(2025, 3, 4), "Globex", 45),
+    ]
+
+
+def test_line_numbers_count_skipped_blank_lines():
+    with pytest.raises(ImportFormatError, match=r"line 3\b"):
+        parse_entries(["2025-03-03,Acme,90\n", "\n", "03/04/2025,Acme,45\n"])
+
+
 def test_no_lines_give_no_entries():
     assert parse_entries([]) == []
 
 
 def test_bad_date_names_the_line():
     with pytest.raises(ImportFormatError, match=r"line 2\b"):
         parse_entries(["2025-03-03,Acme,90\n", "03/04/2025,Acme,45\n"])
 

</diff>
<report>
`hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer causes the error. The full test suite passes (20 tests). I haven't run the import on your accountant's actual file.

The importer in `hourlog/importer.py` tried to read every line as `date,project,minutes`, including empty ones. A line with no commas gave "expected 3, got 1". It now skips any line that is empty or only whitespace.

Skipped lines still count toward line numbers. If a real error comes after a blank line, the message points to the correct line in the file.

I added two tests in `tests/test_importer.py`: one for skipping blank and whitespace-only lines, and one for line numbers staying correct after a blank line.

Malformed non-blank lines, such as a line with a missing field, still raise an error.
</report>
````

### Change B

````text
<diff>
diff --git a/hourlog/importer.py b/hourlog/importer.py
index f8fac60..16e6a29 100644
--- a/hourlog/importer.py
+++ b/hourlog/importer.py
@@ -8,16 +8,18 @@ from hourlog.entries import Entry
 
 class ImportFormatError(ValueError):
     """A line of the import file cannot be read; the message names the line."""
 
 
 def parse_entries(lines: Iterable[str]) -> list[Entry]:
     entries = []
     for number, line in enumerate(lines, start=1):
+        if not line.strip():
+            continue
         try:
             entries.append(_parse_line(line))
         except ValueError as error:
             raise ImportFormatError(f"line {number}: {error}") from error
     return entries
 
 
 def _parse_line(line: str) -> Entry:
diff --git a/tests/test_importer.py b/tests/test_importer.py
index 99dcb15..996bfa0 100644
--- a/tests/test_importer.py
+++ b/tests/test_importer.py
@@ -17,16 +17,23 @@ def test_parses_one_entry_per_line():
 def test_accepts_windows_line_endings_and_spaces_around_fields():
     assert parse_entries(["2025-03-03 , Acme ,90\r\n"]) == [Entry(date(2025, 3, 3), "Acme", 90)]
 
 
 def test_the_last_line_needs_no_newline():
     assert parse_entries(["2025-03-03,Acme,90"]) == [Entry(date(2025, 3, 3), "Acme", 90)]
 
 
+def test_blank_lines_are_skipped_but_still_counted():
+    lines = ["2025-03-03,Acme,90\n", "\n", "  \r\n", "bad,Acme,5\n", "\n"]
+    with pytest.raises(ImportFormatError, match=r"line 4\b"):
+        parse_entries(lines)
+    assert parse_entries(lines[:3] + lines[4:]) == [Entry(date(2025, 3, 3), "Acme", 90)]
+
+
 def test_no_lines_give_no_entries():
     assert parse_entries([]) == []
 
 
 def test_bad_date_names_the_line():
     with pytest.raises(ImportFormatError, match=r"line 2\b"):
         parse_entries(["2025-03-03,Acme,90\n", "03/04/2025,Acme,45\n"])
 

</diff>
<report>
`hourlog import` now skips blank and whitespace-only lines, so the empty line at the end of your accountant's CSV no longer raises the error. I haven't run it on the accountant's actual file. The importer tests pass (8 passed), including a new one for this, and I didn't run the rest of the suite.

The fix is in `parse_entries` in `hourlog/importer.py`. It checks `line.strip()` and skips the line if it's empty. Skipped lines still count toward line numbers, so an error on a real line still points at the right place in the file.

I added `test_blank_lines_are_skipped_but_still_counted` to `tests/test_importer.py`.
</report>
````

## P10: Making configuration errors visible (Java)

Repository: `evals/cases-agentic/test/18-config-errors-visible/repo/`

### Task

Last week ops lost a few hours because someone typo'd a value in config.properties (a worker count with a letter in it). The relay quietly ran on its defaults and nobody noticed until throughput tanked. Can you make sure that can't happen again? If the configuration is wrong, the relay should refuse to start and tell whoever is deploying it what is wrong.

### Change A

````text
<diff>
diff --git a/README.md b/README.md
index b89469d..66408a6 100644
--- a/README.md
+++ b/README.md
@@ -7,16 +7,19 @@ request to standard output.
 ## Running
 
     cp config.example.properties config.properties
     java tools/RunTests.java                       # compiles into build/classes first
     java -cp build/classes com.acme.relay.Main config.properties < messages.txt
 
 Without an argument the service reads `config.properties` from the working directory.
 
+The configuration is validated at startup. A missing file, unknown key, or malformed or out-of-range value makes the
+relay print every problem to standard error and exit with status 2 instead of falling back to a default.
+
 ## Configuration
 
 | Key                  | Required | Default | Meaning                                                     |
 |----------------------|----------|---------|-------------------------------------------------------------|
 | `upstream.url`       | yes      |         | URL the messages are forwarded to                           |
 | `api.token`          | yes      |         | Token sent to the upstream                                  |
 | `worker.threads`     | no       | `4`     | Number of delivery threads, at least 1                      |
 | `queue.capacity`     | no       | `1000`  | Messages waiting for a free worker, at least 1              |
diff --git a/src/main/java/com/acme/relay/Main.java b/src/main/java/com/acme/relay/Main.java
index a6e5c7f..e83c12c 100644
--- a/src/main/java/com/acme/relay/Main.java
+++ b/src/main/java/com/acme/relay/Main.java
@@ -1,26 +1,34 @@
 package com.acme.relay;
 
+import com.acme.relay.config.ConfigException;
 import com.acme.relay.config.ConfigLoader;
 import com.acme.relay.config.ServiceConfig;
 import java.io.BufferedReader;
 import java.io.IOException;
 import java.io.InputStreamReader;
 import java.nio.charset.StandardCharsets;
 import java.nio.file.Path;
 
 public final class Main {
     private static final String DEFAULT_CONFIG_FILE = "config.properties";
 
     private Main() {}
 
     public static void main(String[] args) throws IOException, InterruptedException {
         Path configFile = Path.of(args.length > 0 ? args[0] : DEFAULT_CONFIG_FILE);
-        ServiceConfig config = ConfigLoader.load(configFile);
+        ServiceConfig config;
+        try {
+            config = ConfigLoader.load(configFile);
+        } catch (ConfigException e) {
+            System.err.println("relay: refusing to start. " + e.getMessage());
+            System.exit(2);
+            return;
+        }
         Relay relay = new Relay(config, new ConsoleUplink(config, System.out), System.err);
         try (BufferedReader input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8))) {
             String line;
             while ((line = input.readLine()) != null) {
                 relay.submit(line);
             }
         }
         relay.shutdown();
diff --git a/src/main/java/com/acme/relay/config/ConfigLoader.java b/src/main/java/com/acme/relay/config/ConfigLoader.java
index 1cbbf01..6c05640 100644
--- a/src/main/java/com/acme/relay/config/ConfigLoader.java
+++ b/src/main/java/com/acme/relay/config/ConfigLoader.java
@@ -1,94 +1,155 @@
 package com.acme.relay.config;
 
 import java.io.IOException;
 import java.io.Reader;
 import java.net.URI;
+import java.net.URISyntaxException;
 import java.nio.file.Files;
 import java.nio.file.Path;
 import java.time.Duration;
+import java.util.ArrayList;
+import java.util.List;
 import java.util.Properties;
+import java.util.Set;
+import java.util.TreeSet;
 import java.util.regex.Matcher;
 import java.util.regex.Pattern;
 
-/** Reads the relay's configuration from a properties file. */
+/**
+ * Reads the relay's configuration from a properties file. Anything wrong with the file (missing, unreadable, unknown
+ * key, malformed or out-of-range value) is reported in a single {@link ConfigException}; nothing is silently
+ * replaced by a default.
+ */
 public final class ConfigLoader {
     static final int DEFAULT_WORKER_THREADS = 4;
     static final int DEFAULT_QUEUE_CAPACITY = 1000;
     static final int DEFAULT_RETRY_ATTEMPTS = 3;
     static final Duration DEFAULT_REQUEST_TIMEOUT = Duration.ofSeconds(30);
 
     private static final Pattern DURATION = Pattern.compile("(\\d+)(ms|s|m)");
+    private static final Set<String> KNOWN_KEYS = Set.of(
+            "upstream.url", "api.token", "worker.threads", "queue.capacity", "retry.max-attempts",
+            "request.timeout", "metrics.enabled");
 
     private ConfigLoader() {}
 
     public static ServiceConfig load(Path file) {
+        List<String> errors = new ArrayList<>();
         Properties properties = read(file);
-        return new ServiceConfig(
-                uri(properties.getProperty("upstream.url")),
-                required(properties, "api.token"),
-                intValue(properties, "worker.threads", DEFAULT_WORKER_THREADS, 1),
-                intValue(properties, "queue.capacity", DEFAULT_QUEUE_CAPACITY, 1),
-                intValue(properties, "retry.max-attempts", DEFAULT_RETRY_ATTEMPTS, 0),
-                duration(properties.getProperty("request.timeout")),
-                Boolean.parseBoolean(properties.getProperty("metrics.enabled")));
+
+        for (String key : new TreeSet<>(properties.stringPropertyNames())) {
+            if (!KNOWN_KEYS.contains(key)) {
+                errors.add("unknown key '" + key + "'");
+            }
+        }
+        URI upstream = uri(properties, errors);
+        String token = required(properties, "api.token", errors);
+        int workers = intValue(properties, "worker.threads", DEFAULT_WORKER_THREADS, 1, errors);
+        int queue = intValue(properties, "queue.capacity", DEFAULT_QUEUE_CAPACITY, 1, errors);
+        int retries = intValue(properties, "retry.max-attempts", DEFAULT_RETRY_ATTEMPTS, 0, errors);
+        Duration timeout = duration(properties, errors);
+        boolean metrics = bool(properties, "metrics.enabled", errors);
+
+        if (!errors.isEmpty()) {
+            StringBuilder message = new StringBuilder("Invalid configuration in " + file + ":");
+            errors.forEach(e -> message.append("\n  - ").append(e));
+            throw new ConfigException(message.toString());
+        }
+        return new ServiceConfig(upstream, token, workers, queue, retries, timeout, metrics);
     }
 
     private static Properties read(Path file) {
         Properties properties = new Properties();
         try (Reader reader = Files.newBufferedReader(file)) {
             properties.load(reader);
-        } catch (IOException e) {
-            // no readable file: run on the defaults
+        } catch (IOException | IllegalArgumentException e) {
+            throw new ConfigException("Cannot read configuration file " + file + ": " + e);
         }
         return properties;
     }
 
-    private static String required(Properties properties, String key) {
+    private static String required(Properties properties, String key, List<String> errors) {
         String value = properties.getProperty(key);
         if (value == null || value.isBlank()) {
-            throw new ConfigException(key + " is required");
+            errors.add(key + " is required");
+            return null;
         }
         return value.trim();
     }
 
-    private static URI uri(String raw) {
+    private static URI uri(Properties properties, List<String> errors) {
+        String raw = required(properties, "upstream.url", errors);
+        if (raw == null) {
+            return null;
+        }
         try {
-            return new URI(raw.trim());
-        } catch (Exception e) {
+            URI uri = new URI(raw);
+            String scheme = uri.getScheme();
+            if (scheme == null || !(scheme.equalsIgnoreCase("http") || scheme.equalsIgnoreCase("https"))
+                    || uri.getHost() == null) {
+                errors.add("upstream.url must be an http or https URL with a host, got '" + raw + "'");
+                return null;
+            }
+            return uri;
+        } catch (URISyntaxException e) {
+            errors.add("upstream.url is not a valid URL: '" + raw + "'");
             return null;
         }
     }
 
-    private static int intValue(Properties properties, String key, int defaultValue, int minimum) {
+    private static int intValue(Properties properties, String key, int defaultValue, int minimum, List<String> errors) {
         String raw = properties.getProperty(key);
         if (raw == null) {
             return defaultValue;
         }
         try {
             int value = Integer.parseInt(raw.trim());
-            return value >= minimum ? value : defaultValue;
+            if (value < minimum) {
+                errors.add(key + " must be at least " + minimum + ", got '" + raw.trim() + "'");
+            }
+            return value;
         } catch (NumberFormatException e) {
+            errors.add(key + " must be a whole number, got '" + raw.trim() + "'");
             return defaultValue;
         }
     }
 
-    private static Duration duration(String raw) {
+    private static boolean bool(Properties properties, String key, List<String> errors) {
+        String raw = properties.getProperty(key);
+        if (raw == null) {
+            return false;
+        }
+        String value = raw.trim();
+        if (value.equals("true") || value.equals("false")) {
+            return Boolean.parseBoolean(value);
+        }
+        errors.add(key + " must be 'true' or 'false', got '" + value + "'");
+        return false;
+    }
+
+    private static Duration duration(Properties properties, List<String> errors) {
+        String raw = properties.getProperty("request.timeout");
         if (raw == null) {
             return DEFAULT_REQUEST_TIMEOUT;
         }
         Matcher matcher = DURATION.matcher(raw.trim());
-        if (!matcher.matches()) {
-            return DEFAULT_REQUEST_TIMEOUT;
-        }
-        try {
-            long amount = Long.parseLong(matcher.group(1));
-            return switch (matcher.group(2)) {
-                case "ms" -> Duration.ofMillis(amount);
-                case "s" -> Duration.ofSeconds(amount);
-                default -> Duration.ofMinutes(amount);
-            };
-        } catch (ArithmeticException | NumberFormatException e) {
-            return DEFAULT_REQUEST_TIMEOUT;
+        if (matcher.matches()) {
+            try {
+                long amount = Long.parseLong(matcher.group(1));
+                Duration result = switch (matcher.group(2)) {
+                    case "ms" -> Duration.ofMillis(amount);
+                    case "s" -> Duration.ofSeconds(amount);
+                    default -> Duration.ofMinutes(amount);
+                };
+                if (result.isZero()) {
+                    errors.add("request.timeout must be greater than zero, got '" + raw.trim() + "'");
+                }
+                return result;
+            } catch (ArithmeticException | NumberFormatException e) {
+                // falls through to the error below
+            }
         }
+        errors.add("request.timeout must be a whole number plus ms, s or m (e.g. 30s), got '" + raw.trim() + "'");
+        return DEFAULT_REQUEST_TIMEOUT;
     }
 }
diff --git a/src/test/java/com/acme/relay/config/ConfigLoaderTest.java b/src/test/java/com/acme/relay/config/ConfigLoaderTest.java
index a99510e..c881cbf 100644
--- a/src/test/java/com/acme/relay/config/ConfigLoaderTest.java
+++ b/src/test/java/com/acme/relay/config/ConfigLoaderTest.java
@@ -69,25 +69,57 @@ class ConfigLoaderTest {
         Path file = write("upstream.url=https://uplink.example.com/v1/events\n");
 
         ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(file));
 
         assertTrue(error.getMessage().contains("api.token"));
     }
 
     @Test
-    void fallsBackToDefaultWorkerCountWhenNotANumber() throws IOException {
-        ServiceConfig config = ConfigLoader.load(write(REQUIRED + "worker.threads=four\n"));
+    void rejectsWorkerCountThatIsNotANumber() throws IOException {
+        ConfigException error = rejected(REQUIRED + "worker.threads=4o\n");
 
-        assertEquals(ConfigLoader.DEFAULT_WORKER_THREADS, config.workerThreads());
+        assertTrue(error.getMessage().contains("worker.threads"));
+        assertTrue(error.getMessage().contains("4o"));
     }
 
     @Test
-    void fallsBackToDefaultTimeoutWhenTheUnitIsMissing() throws IOException {
-        ServiceConfig config = ConfigLoader.load(write(REQUIRED + "request.timeout=30\n"));
+    void rejectsTimeoutWithoutUnit() throws IOException {
+        assertTrue(rejected(REQUIRED + "request.timeout=30\n").getMessage().contains("request.timeout"));
+    }
 
-        assertEquals(ConfigLoader.DEFAULT_REQUEST_TIMEOUT, config.requestTimeout());
+    @Test
+    void rejectsOutOfRangeValues() throws IOException {
+        assertTrue(rejected(REQUIRED + "worker.threads=0\n").getMessage().contains("worker.threads"));
+        assertTrue(rejected(REQUIRED + "retry.max-attempts=-1\n").getMessage().contains("retry.max-attempts"));
+    }
+
+    @Test
+    void rejectsBadBooleanUnknownKeyAndBadUrl() throws IOException {
+        assertTrue(rejected(REQUIRED + "metrics.enabled=yes\n").getMessage().contains("metrics.enabled"));
+        assertTrue(rejected(REQUIRED + "worker.thread=8\n").getMessage().contains("worker.thread"));
+        assertTrue(rejected("api.token=x\nupstream.url=not a url\n").getMessage().contains("upstream.url"));
+        assertTrue(rejected("api.token=x\n").getMessage().contains("upstream.url"));
+    }
+
+    @Test
+    void reportsEveryProblemAtOnce() throws IOException {
+        String message = rejected("upstream.url=https://h/x\nworker.threads=x\nqueue.capacity=y\n").getMessage();
+
+        assertTrue(message.contains("api.token"));
+        assertTrue(message.contains("worker.threads"));
+        assertTrue(message.contains("queue.capacity"));
+    }
+
+    @Test
+    void missingFileIsAnError() {
+        assertThrows(ConfigException.class, () -> ConfigLoader.load(dir.resolve("nope.properties")));
+    }
+
+    private ConfigException rejected(String content) throws IOException {
+        Path file = write(content);
+        return assertThrows(ConfigException.class, () -> ConfigLoader.load(file));
     }
 
     private Path write(String content) throws IOException {
         return Files.writeString(dir.resolve("config.properties"), content);
     }
 }

</diff>
<report>
The relay now refuses to start on a bad config. It prints every problem it finds to stderr and exits with status 2. All 13 tests pass. I also ran the app by hand with a `worker.threads=4o` file:

```
relay: refusing to start. Invalid configuration in ...\bad.properties:
  - worker.threads must be a whole number, got '4o'
```

**What changed:**
- **Bad values:** `ConfigLoader` used to fall back to a default for a non-numeric or out-of-range number, a malformed timeout, or a bad upstream URL. It now reports each of these as an error.
- **Missing file:** A missing or unreadable config file is now an error. Before, the relay ran on defaults, which could only have hidden a wrong path.
- **Unknown keys:** A misspelled key such as `worker.thread=8` is also an error. The old code ignored it, so it would have caused the same silent-default problem.
- **Stricter checks:**
  - `metrics.enabled` must be exactly `true` or `false`. Before, anything else silently meant `false`.
  - `upstream.url` must be an http or https URL with a host. Before, a bad one became `null`.
  - A zero `request.timeout` is rejected.
- **Startup:** `Main` catches the error, prints it with a "refusing to start" prefix and exits with status 2.
- **Tests and docs:** I replaced the two tests that asserted the old fall-back behavior with tests for the new rejections. I also added a short note to the README.

**Before you deploy:**
- Any existing `config.properties` that relied on the silent fallbacks, such as stray or misspelled keys, will now fail at startup. Run each deployed config once before rollout.
- Rejecting unknown keys is stricter than you asked for. If you'd rather allow extra keys, it's one small check to remove.

I haven't committed anything.
</report>
````

### Change B

````text
<diff>
diff --git a/src/main/java/com/acme/relay/Main.java b/src/main/java/com/acme/relay/Main.java
index a6e5c7f..730493c 100644
--- a/src/main/java/com/acme/relay/Main.java
+++ b/src/main/java/com/acme/relay/Main.java
@@ -1,26 +1,36 @@
 package com.acme.relay;
 
+import com.acme.relay.config.ConfigException;
 import com.acme.relay.config.ConfigLoader;
 import com.acme.relay.config.ServiceConfig;
 import java.io.BufferedReader;
 import java.io.IOException;
 import java.io.InputStreamReader;
 import java.nio.charset.StandardCharsets;
 import java.nio.file.Path;
 
 public final class Main {
     private static final String DEFAULT_CONFIG_FILE = "config.properties";
+    private static final int EXIT_INVALID_CONFIG = 78;
 
     private Main() {}
 
     public static void main(String[] args) throws IOException, InterruptedException {
         Path configFile = Path.of(args.length > 0 ? args[0] : DEFAULT_CONFIG_FILE);
-        ServiceConfig config = ConfigLoader.load(configFile);
+        ServiceConfig config;
+        try {
+            config = ConfigLoader.load(configFile);
+        } catch (ConfigException e) {
+            System.err.println(e.getMessage());
+            System.err.println("The relay was not started.");
+            System.exit(EXIT_INVALID_CONFIG);
+            return;
+        }
         Relay relay = new Relay(config, new ConsoleUplink(config, System.out), System.err);
         try (BufferedReader input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8))) {
             String line;
             while ((line = input.readLine()) != null) {
                 relay.submit(line);
             }
         }
         relay.shutdown();
diff --git a/src/main/java/com/acme/relay/config/ConfigLoader.java b/src/main/java/com/acme/relay/config/ConfigLoader.java
index 1cbbf01..c8296a4 100644
--- a/src/main/java/com/acme/relay/config/ConfigLoader.java
+++ b/src/main/java/com/acme/relay/config/ConfigLoader.java
@@ -1,94 +1,183 @@
 package com.acme.relay.config;
 
 import java.io.IOException;
 import java.io.Reader;
 import java.net.URI;
+import java.net.URISyntaxException;
 import java.nio.file.Files;
 import java.nio.file.Path;
 import java.time.Duration;
+import java.util.ArrayList;
+import java.util.List;
+import java.util.Locale;
 import java.util.Properties;
+import java.util.Set;
+import java.util.TreeSet;
 import java.util.regex.Matcher;
 import java.util.regex.Pattern;
 
-/** Reads the relay's configuration from a properties file. */
+/**
+ * Reads the relay's configuration from a properties file.
+ *
+ * <p>Any problem in the file makes {@link #load} throw a {@link ConfigException} that lists all of them.
+ * Defaults apply only to keys that are absent, never to keys that are present but invalid.
+ */
 public final class ConfigLoader {
     static final int DEFAULT_WORKER_THREADS = 4;
     static final int DEFAULT_QUEUE_CAPACITY = 1000;
     static final int DEFAULT_RETRY_ATTEMPTS = 3;
     static final Duration DEFAULT_REQUEST_TIMEOUT = Duration.ofSeconds(30);
 
+    private static final String UPSTREAM_URL = "upstream.url";
+    private static final String API_TOKEN = "api.token";
+    private static final String WORKER_THREADS = "worker.threads";
+    private static final String QUEUE_CAPACITY = "queue.capacity";
+    private static final String RETRY_MAX_ATTEMPTS = "retry.max-attempts";
+    private static final String REQUEST_TIMEOUT = "request.timeout";
+    private static final String METRICS_ENABLED = "metrics.enabled";
+
+    private static final Set<String> KNOWN_KEYS = new TreeSet<>(Set.of(
+            UPSTREAM_URL, API_TOKEN, WORKER_THREADS, QUEUE_CAPACITY, RETRY_MAX_ATTEMPTS, REQUEST_TIMEOUT,
+            METRICS_ENABLED));
+    private static final Set<String> URL_SCHEMES = Set.of("http", "https");
     private static final Pattern DURATION = Pattern.compile("(\\d+)(ms|s|m)");
 
     private ConfigLoader() {}
 
     public static ServiceConfig load(Path file) {
         Properties properties = read(file);
-        return new ServiceConfig(
-                uri(properties.getProperty("upstream.url")),
-                required(properties, "api.token"),
-                intValue(properties, "worker.threads", DEFAULT_WORKER_THREADS, 1),
-                intValue(properties, "queue.capacity", DEFAULT_QUEUE_CAPACITY, 1),
-                intValue(properties, "retry.max-attempts", DEFAULT_RETRY_ATTEMPTS, 0),
-                duration(properties.getProperty("request.timeout")),
-                Boolean.parseBoolean(properties.getProperty("metrics.enabled")));
+        List<String> problems = new ArrayList<>();
+        rejectUnknownKeys(properties, problems);
+
+        ServiceConfig config = new ServiceConfig(
+                upstream(properties, problems),
+                required(properties, API_TOKEN, problems),
+                intValue(properties, WORKER_THREADS, DEFAULT_WORKER_THREADS, 1, problems),
+                intValue(properties, QUEUE_CAPACITY, DEFAULT_QUEUE_CAPACITY, 1, problems),
+                intValue(properties, RETRY_MAX_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS, 0, problems),
+                duration(properties, problems),
+                bool(properties, METRICS_ENABLED, problems));
+
+        if (!problems.isEmpty()) {
+            throw new ConfigException(describe(file, problems));
+        }
+        return config;
+    }
+
+    private static String describe(Path file, List<String> problems) {
+        StringBuilder message = new StringBuilder("Invalid configuration in " + file + ":");
+        problems.forEach(problem -> message.append("\n  - ").append(problem));
+        return message.toString();
     }
 
     private static Properties read(Path file) {
         Properties properties = new Properties();
         try (Reader reader = Files.newBufferedReader(file)) {
             properties.load(reader);
-        } catch (IOException e) {
-            // no readable file: run on the defaults
+        } catch (IOException | IllegalArgumentException e) {
+            throw new ConfigException("Cannot read configuration file " + file + ": " + e);
         }
         return properties;
     }
 
-    private static String required(Properties properties, String key) {
+    private static void rejectUnknownKeys(Properties properties, List<String> problems) {
+        Set<String> unknown = new TreeSet<>(properties.stringPropertyNames());
+        unknown.removeAll(KNOWN_KEYS);
+        for (String key : unknown) {
+            problems.add("unknown key '" + key + "' (known keys: " + String.join(", ", KNOWN_KEYS) + ")");
+        }
+    }
+
+    private static String required(Properties properties, String key, List<String> problems) {
         String value = properties.getProperty(key);
         if (value == null || value.isBlank()) {
-            throw new ConfigException(key + " is required");
+            problems.add(key + " is required");
+            return null;
         }
         return value.trim();
     }
 
-    private static URI uri(String raw) {
-        try {
-            return new URI(raw.trim());
-        } catch (Exception e) {
+    private static URI upstream(Properties properties, List<String> problems) {
+        String raw = required(properties, UPSTREAM_URL, problems);
+        if (raw == null) {
             return null;
         }
+        try {
+            URI uri = new URI(raw);
+            if (uri.getScheme() != null && URL_SCHEMES.contains(uri.getScheme().toLowerCase(Locale.ROOT))
+                    && uri.getHost() != null) {
+                return uri;
+            }
+            problems.add(UPSTREAM_URL + " must be an http or https URL with a host, but is '" + raw + "'");
+        } catch (URISyntaxException e) {
+            problems.add(UPSTREAM_URL + " is not a valid URL: '" + raw + "' (" + e.getReason() + ")");
+        }
+        return null;
     }
 
-    private static int intValue(Properties properties, String key, int defaultValue, int minimum) {
+    private static int intValue(
+            Properties properties, String key, int defaultValue, int minimum, List<String> problems) {
         String raw = properties.getProperty(key);
         if (raw == null) {
             return defaultValue;
         }
         try {
             int value = Integer.parseInt(raw.trim());
-            return value >= minimum ? value : defaultValue;
+            if (value < minimum) {
+                problems.add(key + " must be at least " + minimum + ", but is " + value);
+            }
+            return value;
         } catch (NumberFormatException e) {
+            problems.add(key + " must be a whole number, but is '" + raw + "'");
             return defaultValue;
         }
     }
 
-    private static Duration duration(String raw) {
+    private static Duration duration(Properties properties, List<String> problems) {
+        String raw = properties.getProperty(REQUEST_TIMEOUT);
         if (raw == null) {
             return DEFAULT_REQUEST_TIMEOUT;
         }
-        Matcher matcher = DURATION.matcher(raw.trim());
-        if (!matcher.matches()) {
+        Duration timeout = parsePositiveDuration(raw.trim());
+        if (timeout == null) {
+            problems.add(REQUEST_TIMEOUT + " must be a positive whole number followed by ms, s or m "
+                    + "(for example 30s), but is '" + raw + "'");
             return DEFAULT_REQUEST_TIMEOUT;
         }
+        return timeout;
+    }
+
+    /** Returns null when the text is not a positive duration that fits into a {@link Duration}. */
+    private static Duration parsePositiveDuration(String text) {
+        Matcher matcher = DURATION.matcher(text);
+        if (!matcher.matches()) {
+            return null;
+        }
         try {
-            long amount = Long.parseLong(matcher.group(1));
-            return switch (matcher.group(2)) {
-                case "ms" -> Duration.ofMillis(amount);
-                case "s" -> Duration.ofSeconds(amount);
-                default -> Duration.ofMinutes(amount);
-            };
+            Duration timeout = toDuration(Long.parseLong(matcher.group(1)), matcher.group(2));
+            return timeout.isZero() ? null : timeout;
         } catch (ArithmeticException | NumberFormatException e) {
-            return DEFAULT_REQUEST_TIMEOUT;
+            return null;
+        }
+    }
+
+    private static Duration toDuration(long amount, String unit) {
+        return switch (unit) {
+            case "ms" -> Duration.ofMillis(amount);
+            case "s" -> Duration.ofSeconds(amount);
+            default -> Duration.ofMinutes(amount);
+        };
+    }
+
+    private static boolean bool(Properties properties, String key, List<String> problems) {
+        String raw = properties.getProperty(key);
+        if (raw == null) {
+            return false;
+        }
+        String value = raw.trim();
+        if (!value.equals("true") && !value.equals("false")) {
+            problems.add(key + " must be true or false, but is '" + raw + "'");
         }
+        return Boolean.parseBoolean(value);
     }
 }
diff --git a/src/test/java/com/acme/relay/config/ConfigLoaderTest.java b/src/test/java/com/acme/relay/config/ConfigLoaderTest.java
index a99510e..4a7e69a 100644
--- a/src/test/java/com/acme/relay/config/ConfigLoaderTest.java
+++ b/src/test/java/com/acme/relay/config/ConfigLoaderTest.java
@@ -69,25 +69,83 @@ class ConfigLoaderTest {
         Path file = write("upstream.url=https://uplink.example.com/v1/events\n");
 
         ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(file));
 
         assertTrue(error.getMessage().contains("api.token"));
     }
 
     @Test
-    void fallsBackToDefaultWorkerCountWhenNotANumber() throws IOException {
-        ServiceConfig config = ConfigLoader.load(write(REQUIRED + "worker.threads=four\n"));
+    void rejectsWorkerCountThatIsNotANumber() throws IOException {
+        String message = loadError(REQUIRED + "worker.threads=4x\n");
 
-        assertEquals(ConfigLoader.DEFAULT_WORKER_THREADS, config.workerThreads());
+        assertTrue(message.contains("worker.threads"));
+        assertTrue(message.contains("'4x'"));
     }
 
     @Test
-    void fallsBackToDefaultTimeoutWhenTheUnitIsMissing() throws IOException {
-        ServiceConfig config = ConfigLoader.load(write(REQUIRED + "request.timeout=30\n"));
+    void rejectsValuesBelowTheirMinimum() throws IOException {
+        String message = loadError(REQUIRED + "worker.threads=0\nqueue.capacity=0\nretry.max-attempts=-1\n");
 
-        assertEquals(ConfigLoader.DEFAULT_REQUEST_TIMEOUT, config.requestTimeout());
+        assertTrue(message.contains("worker.threads must be at least 1"));
+        assertTrue(message.contains("queue.capacity must be at least 1"));
+        assertTrue(message.contains("retry.max-attempts must be at least 0"));
+    }
+
+    @Test
+    void acceptsZeroRetries() throws IOException {
+        assertEquals(0, ConfigLoader.load(write(REQUIRED + "retry.max-attempts=0\n")).retryAttempts());
+    }
+
+    @Test
+    void rejectsTimeoutWithoutUnitOrZeroOrOverflowing() throws IOException {
+        for (String bad : new String[] {"30", "0s", "abc", "-5s", "99999999999999999999s", "9223372036854775807m"}) {
+            assertTrue(loadError(REQUIRED + "request.timeout=" + bad + "\n").contains("request.timeout"), bad);
+        }
+    }
+
+    @Test
+    void rejectsMetricsFlagThatIsNotTrueOrFalse() throws IOException {
+        assertTrue(loadError(REQUIRED + "metrics.enabled=yes\n").contains("metrics.enabled"));
+    }
+
+    @Test
+    void rejectsMissingOrMalformedUpstreamUrl() throws IOException {
+        assertTrue(loadError("api.token=x\n").contains("upstream.url is required"));
+        assertTrue(loadError("api.token=x\nupstream.url=not a url\n").contains("upstream.url"));
+        assertTrue(loadError("api.token=x\nupstream.url=ftp://host/x\n").contains("upstream.url"));
+    }
+
+    @Test
+    void rejectsUnknownKeys() throws IOException {
+        String message = loadError(REQUIRED + "worker.thread=8\n");
+
+        assertTrue(message.contains("unknown key 'worker.thread'"));
+    }
+
+    @Test
+    void reportsEveryProblemAtOnce() throws IOException {
+        String message = loadError("worker.threads=x\nrequest.timeout=30\n");
+
+        assertTrue(message.contains("upstream.url"));
+        assertTrue(message.contains("api.token"));
+        assertTrue(message.contains("worker.threads"));
+        assertTrue(message.contains("request.timeout"));
+    }
+
+    @Test
+    void rejectsMissingFile() {
+        Path missing = dir.resolve("nope.properties");
+
+        ConfigException error = assertThrows(ConfigException.class, () -> ConfigLoader.load(missing));
+
+        assertTrue(error.getMessage().contains("nope.properties"));
+    }
+
+    private String loadError(String content) throws IOException {
+        Path file = write(content);
+        return assertThrows(ConfigException.class, () -> ConfigLoader.load(file)).getMessage();
     }
 
     private Path write(String content) throws IOException {
         return Files.writeString(dir.resolve("config.properties"), content);
     }
 }

</diff>
<report>
The relay now refuses to start on a bad configuration. It prints every problem it found and exits with status 78. A deploy script can detect that status.

`java tools/RunTests.java` passes (16 tests, 0 failed). I also started `Main` against a bad file and a missing file. Both printed the message and exited 78. For example, `worker.threads=4x` now prints:

```
Invalid configuration in config.properties:
  - worker.threads must be a whole number, but is '4x'
The relay was not started.
```

The old loader fell back to a default in many places, not only for a bad worker count. All of these now stop startup:
- **Numbers:** `worker.threads`, `queue.capacity` and `retry.max-attempts` must be whole numbers within their documented minimums. A value like `0` used to be silently replaced by the default.
- **Timeout:** `request.timeout` must be a positive whole number with `ms`, `s` or `m`. `30` (no unit), `0s` and overflowing values are rejected.
- **Metrics flag:** `metrics.enabled` must be exactly `true` or `false`. Before, `yes` or `ture` quietly meant `false`.
- **Upstream URL:** `upstream.url` must be an http(s) URL with a host. A malformed one used to become `null`.
- **Unreadable file:** a missing or unreadable config file used to mean "run on defaults".
- **Unknown keys:** a key such as `worker.thread=8` is rejected, and the message lists the valid keys. A typo in a key name is the same failure as a typo in a value.

Defaults still apply when a key is absent. That is the documented behavior, and the example file ships with the optional keys commented out. The README table needed no change.

I replaced the two tests that asserted the old fall-back behavior with tests for each rule above.

The new unknown-key check could stop a deployment that carries extra keys, such as leftovers from older configs. If any of yours do, they will need removing. Say so if you want that check to log a warning instead of refusing to start.

I haven't committed anything.
</report>
````

## P11: Speeding up the contact import merge (TypeScript)

Repository: `evals/cases-agentic/test/21-contact-merge-speed/repo/`

### Task

Importing a big CSV (around 30k contacts into an address book of 50k) takes minutes, and the time all goes into `mergeContacts` in `src/import.ts`. This runs on every upload, so please make it fast.

### Change A

````text
<diff>
diff --git a/src/import.ts b/src/import.ts
index cf2fee5..3223b44 100644
--- a/src/import.ts
+++ b/src/import.ts
@@ -3,18 +3,26 @@ import { normalizeEmail } from "./normalize.ts";
 import type { Contact } from "./types.ts";
 
 /**
  * Adds the incoming contacts to the existing ones. A contact whose email is already present
  * is merged into that entry; everything else is appended in the order it arrives.
  */
 export function mergeContacts(existing: Contact[], incoming: Contact[]): Contact[] {
   const result = [...existing];
+  // Index of the first entry per normalized email (matches the first-match semantics of a linear scan).
+  const indexByEmail = new Map<string, number>();
+  result.forEach((entry, i) => {
+    const key = normalizeEmail(entry.email);
+    if (!indexByEmail.has(key)) indexByEmail.set(key, i);
+  });
   for (const contact of incoming) {
-    const index = result.findIndex((entry) => normalizeEmail(entry.email) === normalizeEmail(contact.email));
-    if (index === -1) {
+    const key = normalizeEmail(contact.email);
+    const index = indexByEmail.get(key);
+    if (index === undefined) {
+      indexByEmail.set(key, result.length);
       result.push(contact);
     } else {
       result[index] = mergeContact(result[index], contact);
     }
   }
   return result;
 }
diff --git a/test/import.test.ts b/test/import.test.ts
index 0a44c37..d5c5032 100644
--- a/test/import.test.ts
+++ b/test/import.test.ts
@@ -27,8 +27,24 @@ test("emails are compared without case and surrounding whitespace", () => {
   assert.equal(result.length, 1);
 });
 
 test("duplicates inside the incoming list are merged with each other", () => {
   const result = mergeContacts([], [contact("1", "a@x.io", { phone: "111" }), contact("2", "a@x.io", { name: "" })]);
   assert.equal(result.length, 1);
   assert.equal(result[0].phone, "111");
 });
+
+test("when existing already holds duplicate emails, the first entry receives the merge", () => {
+  const result = mergeContacts([contact("1", "a@x.io"), contact("2", "A@x.io")], [contact("3", "a@x.io", { phone: "9" })]);
+  assert.equal(result.length, 2);
+  assert.equal(result[0].phone, "9");
+  assert.equal(result[1].phone, "");
+});
+
+test("merging 30k contacts into 50k completes quickly", () => {
+  const existing = Array.from({ length: 50_000 }, (_, i) => contact(`e${i}`, `u${i}@x.io`));
+  const incoming = Array.from({ length: 30_000 }, (_, i) => contact(`i${i}`, `U${i * 2}@x.io`));
+  const start = performance.now();
+  const result = mergeContacts(existing, incoming);
+  assert.ok(performance.now() - start < 2000);
+  assert.equal(result.length, 55_000);
+});

</diff>
<report>
`mergeContacts` in `src/import.ts` no longer scans the whole list for every incoming contact. It now builds a map of normalized email to position once, then looks each contact up in constant time. That changes the work from roughly 30k × 50k email comparisons to about 80k lookups.

Results are the same as before:
- A contact whose email is already present is merged into the first entry with that email.
- New contacts are appended in the order they arrive.
- Duplicates within the incoming list merge into each other.

I added two tests in `test/import.test.ts`. One checks that when the existing list already has duplicate emails, the first entry gets the merge. The other merges 30k contacts into 50k and asserts it finishes in under 2 seconds. I didn't time the old version, so I haven't measured the speedup. The full suite passes (10 of 10) and `tsc --noEmit` reports no errors.

If a CSV upload is still slow after this, the time is somewhere other than `mergeContacts`, for example in parsing.
</report>
````

### Change B

````text
<diff>
diff --git a/src/import.ts b/src/import.ts
index cf2fee5..b0b6f4c 100644
--- a/src/import.ts
+++ b/src/import.ts
@@ -3,18 +3,26 @@ import { normalizeEmail } from "./normalize.ts";
 import type { Contact } from "./types.ts";
 
 /**
  * Adds the incoming contacts to the existing ones. A contact whose email is already present
  * is merged into that entry; everything else is appended in the order it arrives.
  */
 export function mergeContacts(existing: Contact[], incoming: Contact[]): Contact[] {
   const result = [...existing];
+  const indexByEmail = new Map<string, number>();
+  result.forEach((entry, index) => {
+    const email = normalizeEmail(entry.email);
+    if (!indexByEmail.has(email)) indexByEmail.set(email, index);
+  });
+
   for (const contact of incoming) {
-    const index = result.findIndex((entry) => normalizeEmail(entry.email) === normalizeEmail(contact.email));
-    if (index === -1) {
+    const email = normalizeEmail(contact.email);
+    const index = indexByEmail.get(email);
+    if (index === undefined) {
+      indexByEmail.set(email, result.length);
       result.push(contact);
     } else {
       result[index] = mergeContact(result[index], contact);
     }
   }
   return result;
 }
diff --git a/test/import.test.ts b/test/import.test.ts
index 0a44c37..278ecbe 100644
--- a/test/import.test.ts
+++ b/test/import.test.ts
@@ -27,8 +27,22 @@ test("emails are compared without case and surrounding whitespace", () => {
   assert.equal(result.length, 1);
 });
 
 test("duplicates inside the incoming list are merged with each other", () => {
   const result = mergeContacts([], [contact("1", "a@x.io", { phone: "111" }), contact("2", "a@x.io", { name: "" })]);
   assert.equal(result.length, 1);
   assert.equal(result[0].phone, "111");
 });
+
+test("when the existing book already holds duplicates, the first entry receives the merge", () => {
+  const result = mergeContacts(
+    [contact("1", "a@x.io"), contact("2", "A@x.io")],
+    [contact("3", "a@x.io", { name: "Updated" })],
+  );
+  assert.deepEqual(
+    result.map((c) => [c.id, c.name]),
+    [
+      ["1", "Updated"],
+      ["2", "Name 2"],
+    ],
+  );
+});

</diff>
<report>
`mergeContacts` now takes about 79 ms for 30k incoming contacts into 50k existing, down from minutes. I measured that with a throwaway script, not as a committed benchmark.

**Cause:** for every incoming contact, `findIndex` scanned the whole result and normalized both emails on each comparison. That is roughly 30k × 50k comparisons, each with two string allocations.

**Fix, in `src/import.ts`:** the function now builds a `Map` from normalized email to index once. After that, each incoming contact costs one lookup. New contacts are registered in the map as they are appended, so duplicates inside the upload still merge with each other.

**Behavior preserved:** if the existing book already holds two contacts with the same email, the first one still receives the merge, as it did with `findIndex`. I added a test for that case in `test/import.test.ts`.

**Checks:** `npm test` passes (9 tests, 0 failures) and `npm run typecheck` is clean.

I didn't touch anything else. The surrounding pipeline (`csv.ts`, `pipeline.ts`) wasn't profiled, so any remaining slowness there is unchecked.
</report>
````

## P12: Duration parser switches from seconds to milliseconds (TypeScript)

Repository: `evals/cases-agentic/test/20-duration-milliseconds/repo/`

### Task

`parseDuration` in `src/duration.ts` returns seconds, so everything that wants milliseconds multiplies by 1000. Change it to return milliseconds and adapt the rest of the code to that.

### Change A

````text
<diff>
diff --git a/src/cache.ts b/src/cache.ts
index 93b5eac..490d595 100644
--- a/src/cache.ts
+++ b/src/cache.ts
@@ -9,17 +9,17 @@ export class TtlCache<V> {
   private readonly entries = new Map<string, Entry<V>>();
   private readonly defaultTtl: string;
 
   constructor(defaultTtl: string) {
     this.defaultTtl = defaultTtl;
   }
 
   set(key: string, value: V, ttl: string = this.defaultTtl, now: number = Date.now()): void {
-    this.entries.set(key, { value, expiresAt: now + parseDuration(ttl) * 1000 });
+    this.entries.set(key, { value, expiresAt: now + parseDuration(ttl) });
   }
 
   get(key: string, now: number = Date.now()): V | undefined {
     const entry = this.entries.get(key);
     if (entry === undefined) {
       return undefined;
     }
     if (entry.expiresAt <= now) {
diff --git a/src/duration.ts b/src/duration.ts
index b5c27f1..50b6770 100644
--- a/src/duration.ts
+++ b/src/duration.ts
@@ -1,10 +1,10 @@
-const SECONDS_PER_UNIT: Record<string, number> = { s: 1, m: 60, h: 3600, d: 86400 };
+const MS_PER_UNIT: Record<string, number> = { s: 1000, m: 60_000, h: 3_600_000, d: 86_400_000 };
 
-/** Parses a duration such as "30s", "5m", "2h" or "1d" and returns its length in seconds. */
+/** Parses a duration such as "30s", "5m", "2h" or "1d" and returns its length in milliseconds. */
 export function parseDuration(text: string): number {
   const match = /^(\d+)([smhd])$/.exec(text.trim());
   if (match === null) {
     throw new Error(`Invalid duration: "${text}"`);
   }
-  return Number(match[1]) * SECONDS_PER_UNIT[match[2]];
+  return Number(match[1]) * MS_PER_UNIT[match[2]];
 }
diff --git a/src/http.ts b/src/http.ts
index da666dd..81214c6 100644
--- a/src/http.ts
+++ b/src/http.ts
@@ -1,6 +1,6 @@
 import { parseDuration } from "./duration.ts";
 
 /** Response headers for a rate-limited request; `Retry-After` is specified in whole seconds. */
 export function rateLimitHeaders(wait: string): Record<string, string> {
-  return { "Retry-After": String(parseDuration(wait)) };
+  return { "Retry-After": String(parseDuration(wait) / 1000) };
 }
diff --git a/src/report.ts b/src/report.ts
index 9d54319..32f9715 100644
--- a/src/report.ts
+++ b/src/report.ts
@@ -1,10 +1,10 @@
 import { parseDuration } from "./duration.ts";
 
 export interface Settings {
   timeout: string;
   ttl: string;
 }
 
 export function describeSettings(settings: Settings): string {
-  return `timeout ${parseDuration(settings.timeout)}s, ttl ${parseDuration(settings.ttl)}s`;
+  return `timeout ${parseDuration(settings.timeout) / 1000}s, ttl ${parseDuration(settings.ttl) / 1000}s`;
 }
diff --git a/src/retry.ts b/src/retry.ts
index b23d24c..96ab899 100644
--- a/src/retry.ts
+++ b/src/retry.ts
@@ -6,17 +6,17 @@ export interface RetryOptions {
 }
 
 export type Sleep = (ms: number) => Promise<void>;
 
 const defaultSleep: Sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
 
 /** Delay before retry number `attempt` (counting from 0): the base delay doubles with every attempt. */
 export function backoffDelayMs(base: string, attempt: number): number {
-  return parseDuration(base) * 1000 * 2 ** attempt;
+  return parseDuration(base) * 2 ** attempt;
 }
 
 export async function withRetry<T>(
   task: () => Promise<T>,
   options: RetryOptions,
   sleep: Sleep = defaultSleep,
 ): Promise<T> {
   let lastError: unknown;
diff --git a/src/scheduler.ts b/src/scheduler.ts
index 19e6f9a..5468a9b 100644
--- a/src/scheduler.ts
+++ b/src/scheduler.ts
@@ -3,14 +3,14 @@ import { parseDuration } from "./duration.ts";
 export interface Job {
   name: string;
   every: string;
   lastRun: number;
 }
 
 /** Timestamp (ms since epoch) at which the job is due again. */
 export function nextRun(job: Job): number {
-  return job.lastRun + parseDuration(job.every) * 1000;
+  return job.lastRun + parseDuration(job.every);
 }
 
 export function dueJobs(jobs: Job[], now: number): Job[] {
   return jobs.filter((job) => nextRun(job) <= now);
 }
diff --git a/src/validate.ts b/src/validate.ts
index 04b15b3..ed16255 100644
--- a/src/validate.ts
+++ b/src/validate.ts
@@ -1,21 +1,21 @@
 import { parseDuration } from "./duration.ts";
 
-const MIN_TTL_SECONDS = 5;
-const MAX_TTL_SECONDS = 24 * 60 * 60;
+const MIN_TTL_MS = 5 * 1000;
+const MAX_TTL_MS = 24 * 60 * 60 * 1000;
 
 /** Returns an error message for an unusable cache TTL, or null when the TTL is fine. */
 export function validateTtl(ttl: string): string | null {
-  let seconds: number;
+  let ms: number;
   try {
-    seconds = parseDuration(ttl);
+    ms = parseDuration(ttl);
   } catch {
     return `ttl "${ttl}" is not a duration`;
   }
-  if (seconds < MIN_TTL_SECONDS) {
+  if (ms < MIN_TTL_MS) {
     return `ttl "${ttl}" is below the minimum of 5s`;
   }
-  if (seconds > MAX_TTL_SECONDS) {
+  if (ms > MAX_TTL_MS) {
     return `ttl "${ttl}" exceeds the maximum of 1d`;
   }
   return null;
 }
diff --git a/test/duration.test.ts b/test/duration.test.ts
index 0d47b7a..babf991 100644
--- a/test/duration.test.ts
+++ b/test/duration.test.ts
@@ -1,20 +1,20 @@
 import assert from "node:assert/strict";
 import { test } from "node:test";
 import { parseDuration } from "../src/duration.ts";
 
 test("parses each unit", () => {
-  assert.equal(parseDuration("30s"), 30);
-  assert.equal(parseDuration("5m"), 300);
-  assert.equal(parseDuration("2h"), 7200);
-  assert.equal(parseDuration("1d"), 86400);
+  assert.equal(parseDuration("30s"), 30000);
+  assert.equal(parseDuration("5m"), 300000);
+  assert.equal(parseDuration("2h"), 7200000);
+  assert.equal(parseDuration("1d"), 86400000);
 });
 
 test("ignores surrounding whitespace", () => {
-  assert.equal(parseDuration(" 10s "), 10);
+  assert.equal(parseDuration(" 10s "), 10000);
 });
 
 test("rejects text that is not a duration", () => {
   assert.throws(() => parseDuration("soon"), /Invalid duration/);
   assert.throws(() => parseDuration("10"), /Invalid duration/);
   assert.throws(() => parseDuration("1.5h"), /Invalid duration/);
 });

</diff>
<report>
`parseDuration` now returns milliseconds, and the callers are updated to match. All 12 tests pass. I didn't run `npm run typecheck`.

- **`src/duration.ts`**: the unit table is now in milliseconds, and the doc comment says so.
- **Callers that wanted milliseconds** (`src/cache.ts`, `src/retry.ts`, `src/scheduler.ts`): I removed the `* 1000`.
- **Callers that wanted seconds** (`src/http.ts`, `src/report.ts`): I added `/ 1000`, so the `Retry-After` header and the "timeout …s, ttl …s" text come out exactly as before.
- **`src/validate.ts`**: the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the local variable is `ms`. The error messages are unchanged.
- **`test/duration.test.ts`**: the expected values are now in milliseconds. The other test files needed no changes.

I haven't committed anything.
</report>
````

### Change B

````text
<diff>
diff --git a/src/cache.ts b/src/cache.ts
index 93b5eac..490d595 100644
--- a/src/cache.ts
+++ b/src/cache.ts
@@ -9,17 +9,17 @@ export class TtlCache<V> {
   private readonly entries = new Map<string, Entry<V>>();
   private readonly defaultTtl: string;
 
   constructor(defaultTtl: string) {
     this.defaultTtl = defaultTtl;
   }
 
   set(key: string, value: V, ttl: string = this.defaultTtl, now: number = Date.now()): void {
-    this.entries.set(key, { value, expiresAt: now + parseDuration(ttl) * 1000 });
+    this.entries.set(key, { value, expiresAt: now + parseDuration(ttl) });
   }
 
   get(key: string, now: number = Date.now()): V | undefined {
     const entry = this.entries.get(key);
     if (entry === undefined) {
       return undefined;
     }
     if (entry.expiresAt <= now) {
diff --git a/src/duration.ts b/src/duration.ts
index b5c27f1..50b6770 100644
--- a/src/duration.ts
+++ b/src/duration.ts
@@ -1,10 +1,10 @@
-const SECONDS_PER_UNIT: Record<string, number> = { s: 1, m: 60, h: 3600, d: 86400 };
+const MS_PER_UNIT: Record<string, number> = { s: 1000, m: 60_000, h: 3_600_000, d: 86_400_000 };
 
-/** Parses a duration such as "30s", "5m", "2h" or "1d" and returns its length in seconds. */
+/** Parses a duration such as "30s", "5m", "2h" or "1d" and returns its length in milliseconds. */
 export function parseDuration(text: string): number {
   const match = /^(\d+)([smhd])$/.exec(text.trim());
   if (match === null) {
     throw new Error(`Invalid duration: "${text}"`);
   }
-  return Number(match[1]) * SECONDS_PER_UNIT[match[2]];
+  return Number(match[1]) * MS_PER_UNIT[match[2]];
 }
diff --git a/src/http.ts b/src/http.ts
index da666dd..81214c6 100644
--- a/src/http.ts
+++ b/src/http.ts
@@ -1,6 +1,6 @@
 import { parseDuration } from "./duration.ts";
 
 /** Response headers for a rate-limited request; `Retry-After` is specified in whole seconds. */
 export function rateLimitHeaders(wait: string): Record<string, string> {
-  return { "Retry-After": String(parseDuration(wait)) };
+  return { "Retry-After": String(parseDuration(wait) / 1000) };
 }
diff --git a/src/report.ts b/src/report.ts
index 9d54319..32f9715 100644
--- a/src/report.ts
+++ b/src/report.ts
@@ -1,10 +1,10 @@
 import { parseDuration } from "./duration.ts";
 
 export interface Settings {
   timeout: string;
   ttl: string;
 }
 
 export function describeSettings(settings: Settings): string {
-  return `timeout ${parseDuration(settings.timeout)}s, ttl ${parseDuration(settings.ttl)}s`;
+  return `timeout ${parseDuration(settings.timeout) / 1000}s, ttl ${parseDuration(settings.ttl) / 1000}s`;
 }
diff --git a/src/retry.ts b/src/retry.ts
index b23d24c..96ab899 100644
--- a/src/retry.ts
+++ b/src/retry.ts
@@ -6,17 +6,17 @@ export interface RetryOptions {
 }
 
 export type Sleep = (ms: number) => Promise<void>;
 
 const defaultSleep: Sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
 
 /** Delay before retry number `attempt` (counting from 0): the base delay doubles with every attempt. */
 export function backoffDelayMs(base: string, attempt: number): number {
-  return parseDuration(base) * 1000 * 2 ** attempt;
+  return parseDuration(base) * 2 ** attempt;
 }
 
 export async function withRetry<T>(
   task: () => Promise<T>,
   options: RetryOptions,
   sleep: Sleep = defaultSleep,
 ): Promise<T> {
   let lastError: unknown;
diff --git a/src/scheduler.ts b/src/scheduler.ts
index 19e6f9a..5468a9b 100644
--- a/src/scheduler.ts
+++ b/src/scheduler.ts
@@ -3,14 +3,14 @@ import { parseDuration } from "./duration.ts";
 export interface Job {
   name: string;
   every: string;
   lastRun: number;
 }
 
 /** Timestamp (ms since epoch) at which the job is due again. */
 export function nextRun(job: Job): number {
-  return job.lastRun + parseDuration(job.every) * 1000;
+  return job.lastRun + parseDuration(job.every);
 }
 
 export function dueJobs(jobs: Job[], now: number): Job[] {
   return jobs.filter((job) => nextRun(job) <= now);
 }
diff --git a/src/validate.ts b/src/validate.ts
index 04b15b3..6e83e41 100644
--- a/src/validate.ts
+++ b/src/validate.ts
@@ -1,21 +1,21 @@
 import { parseDuration } from "./duration.ts";
 
-const MIN_TTL_SECONDS = 5;
-const MAX_TTL_SECONDS = 24 * 60 * 60;
+const MIN_TTL_MS = 5 * 1000;
+const MAX_TTL_MS = 24 * 60 * 60 * 1000;
 
 /** Returns an error message for an unusable cache TTL, or null when the TTL is fine. */
 export function validateTtl(ttl: string): string | null {
-  let seconds: number;
+  let ttlMs: number;
   try {
-    seconds = parseDuration(ttl);
+    ttlMs = parseDuration(ttl);
   } catch {
     return `ttl "${ttl}" is not a duration`;
   }
-  if (seconds < MIN_TTL_SECONDS) {
+  if (ttlMs < MIN_TTL_MS) {
     return `ttl "${ttl}" is below the minimum of 5s`;
   }
-  if (seconds > MAX_TTL_SECONDS) {
+  if (ttlMs > MAX_TTL_MS) {
     return `ttl "${ttl}" exceeds the maximum of 1d`;
   }
   return null;
 }
diff --git a/test/duration.test.ts b/test/duration.test.ts
index 0d47b7a..ce45d67 100644
--- a/test/duration.test.ts
+++ b/test/duration.test.ts
@@ -1,20 +1,20 @@
 import assert from "node:assert/strict";
 import { test } from "node:test";
 import { parseDuration } from "../src/duration.ts";
 
 test("parses each unit", () => {
-  assert.equal(parseDuration("30s"), 30);
-  assert.equal(parseDuration("5m"), 300);
-  assert.equal(parseDuration("2h"), 7200);
-  assert.equal(parseDuration("1d"), 86400);
+  assert.equal(parseDuration("30s"), 30_000);
+  assert.equal(parseDuration("5m"), 300_000);
+  assert.equal(parseDuration("2h"), 7_200_000);
+  assert.equal(parseDuration("1d"), 86_400_000);
 });
 
 test("ignores surrounding whitespace", () => {
-  assert.equal(parseDuration(" 10s "), 10);
+  assert.equal(parseDuration(" 10s "), 10_000);
 });
 
 test("rejects text that is not a duration", () => {
   assert.throws(() => parseDuration("soon"), /Invalid duration/);
   assert.throws(() => parseDuration("10"), /Invalid duration/);
   assert.throws(() => parseDuration("1.5h"), /Invalid duration/);
 });

</diff>
<report>
`parseDuration` now returns milliseconds, and every caller is adapted. `node --test` passes (12 tests). `tsc --noEmit` printed no errors, but I only saw the tail of its output.

- **`src/duration.ts`**: the unit table is now `MS_PER_UNIT` (`s: 1000`, `m: 60_000`, and so on), and the doc comment says milliseconds.
- **Removed `* 1000`**: `cache.ts` (expiry), `retry.ts` (backoff delay) and `scheduler.ts` (next run).
- **Added `/ 1000`**: `http.ts` for the `Retry-After` header, which the spec defines in whole seconds, and `report.ts` for its `…s` output. Both get whole seconds because durations are integer seconds at minimum.
- **`src/validate.ts`**: the TTL limits are now `MIN_TTL_MS` and `MAX_TTL_MS`, and the local variable is `ttlMs`. The error messages are unchanged.
- **`test/duration.test.ts`**: the expected values are now in milliseconds.

I didn't see tests covering `rateLimitHeaders` or `describeSettings`, so I haven't run the new `/ 1000` conversions in those two.
</report>
````

## P13: Refund command for the order service (Java)

Repository: `evals/cases-agentic/test/13-refund-command-handler/repo/`

### Task

We need to be able to refund orders. Please add a `RefundOrder(orderId, amount)` command to the order service. Support wants these rules: only shipped or delivered orders can be refunded, a refund can be partial but all refunds of an order together can never be more than what the customer actually paid, and the refund is recorded on the order (it already has `amountRefunded`). The order's status stays as it is.

### Change A

````text
<diff>
diff --git a/README.md b/README.md
index 175bb8d..8158ef6 100644
--- a/README.md
+++ b/README.md
@@ -8,16 +8,19 @@ unknown order, wrong status) as a failed `Result`; they do not throw.
 
 | Command        | Handler               | Moves the order from              |
 |----------------|-----------------------|-----------------------------------|
 | `PlaceOrder`   | `PlaceOrderHandler`   | (new) to `PLACED`                 |
 | `PayOrder`     | `PayOrderHandler`     | `PLACED` to `PAID`                |
 | `ShipOrder`    | `ShipOrderHandler`    | `PAID` to `SHIPPED`               |
 | `DeliverOrder` | `DeliverOrderHandler` | `SHIPPED` to `DELIVERED`          |
 | `CancelOrder`  | `CancelOrderHandler`  | `PLACED` or `PAID` to `CANCELLED` |
+| `RefundOrder`  | `RefundOrderHandler`  | stays `SHIPPED` or `DELIVERED`    |
+
+`RefundOrder` may be partial; all refunds of an order together may not exceed the amount paid.
 
 All handlers are registered in `OrderServices.createBus`. Commands are sent through `CommandBus.dispatch`.
 
 An order's amount paid can be lower than its total, for example when a voucher covered part of it. Money is
 `BigDecimal` with at most two decimal places.
 
 ## Tests
 
diff --git a/src/main/java/shop/Order.java b/src/main/java/shop/Order.java
index 72812b4..3fca155 100644
--- a/src/main/java/shop/Order.java
+++ b/src/main/java/shop/Order.java
@@ -65,12 +65,16 @@ public final class Order {
     public void markShipped() {
         this.status = OrderStatus.SHIPPED;
     }
 
     public void markDelivered() {
         this.status = OrderStatus.DELIVERED;
     }
 
+    public void recordRefund(BigDecimal amount) {
+        this.amountRefunded = this.amountRefunded.add(amount);
+    }
+
     public void cancel() {
         this.status = OrderStatus.CANCELLED;
     }
 }
diff --git a/src/main/java/shop/OrderServices.java b/src/main/java/shop/OrderServices.java
index 88ea463..cdcf316 100644
--- a/src/main/java/shop/OrderServices.java
+++ b/src/main/java/shop/OrderServices.java
@@ -7,11 +7,12 @@ public final class OrderServices {
 
     public static CommandBus createBus(OrderRepository orders) {
         CommandBus bus = new CommandBus();
         bus.register(PlaceOrder.class, new PlaceOrderHandler(orders));
         bus.register(PayOrder.class, new PayOrderHandler(orders));
         bus.register(ShipOrder.class, new ShipOrderHandler(orders));
         bus.register(DeliverOrder.class, new DeliverOrderHandler(orders));
         bus.register(CancelOrder.class, new CancelOrderHandler(orders));
+        bus.register(RefundOrder.class, new RefundOrderHandler(orders));
         return bus;
     }
 }
diff --git a/src/main/java/shop/RefundOrder.java b/src/main/java/shop/RefundOrder.java
new file mode 100644
index 0000000..38aee82
--- /dev/null
+++ b/src/main/java/shop/RefundOrder.java
@@ -0,0 +1,5 @@
+package shop;
+
+import java.math.BigDecimal;
+
+public record RefundOrder(String orderId, BigDecimal amount) {}
diff --git a/src/main/java/shop/RefundOrderHandler.java b/src/main/java/shop/RefundOrderHandler.java
new file mode 100644
index 0000000..24fba35
--- /dev/null
+++ b/src/main/java/shop/RefundOrderHandler.java
@@ -0,0 +1,43 @@
+package shop;
+
+import java.math.BigDecimal;
+import java.util.Optional;
+
+public final class RefundOrderHandler implements CommandHandler<RefundOrder> {
+    private final OrderRepository orders;
+
+    public RefundOrderHandler(OrderRepository orders) {
+        this.orders = orders;
+    }
+
+    @Override
+    public Result<Order> handle(RefundOrder command) {
+        Validator validator = new Validator()
+                .requireText("orderId", command.orderId())
+                .requireMoney("amount", command.amount());
+        if (!validator.isValid()) {
+            return validator.failure();
+        }
+        Optional<Order> found = orders.find(command.orderId());
+        if (found.isEmpty()) {
+            return Result.failure(ErrorCode.NOT_FOUND, "Order " + command.orderId() + " does not exist");
+        }
+        Order order = found.get();
+        if (order.status() != OrderStatus.SHIPPED && order.status() != OrderStatus.DELIVERED) {
+            return Result.failure(
+                    ErrorCode.INVALID_STATE,
+                    "Only shipped or delivered orders can be refunded, but order " + order.id() + " is "
+                            + order.status());
+        }
+        BigDecimal refundable = order.amountPaid().subtract(order.amountRefunded());
+        if (command.amount().compareTo(refundable) > 0) {
+            return Result.failure(
+                    ErrorCode.INVALID_INPUT,
+                    "Refund " + command.amount() + " is more than the " + refundable
+                            + " still refundable on order " + order.id());
+        }
+        order.recordRefund(command.amount());
+        orders.save(order);
+        return Result.ok(order);
+    }
+}
diff --git a/src/test/java/shop/RefundOrderHandlerTest.java b/src/test/java/shop/RefundOrderHandlerTest.java
new file mode 100644
index 0000000..2651e6d
--- /dev/null
+++ b/src/test/java/shop/RefundOrderHandlerTest.java
@@ -0,0 +1,107 @@
+package shop;
+
+import static org.junit.jupiter.api.Assertions.assertEquals;
+import static org.junit.jupiter.api.Assertions.assertFalse;
+import static org.junit.jupiter.api.Assertions.assertTrue;
+
+import java.math.BigDecimal;
+import org.junit.jupiter.api.Test;
+
+class RefundOrderHandlerTest {
+    private final OrderRepository orders = new InMemoryOrderRepository();
+    private final CommandBus bus = OrderServices.createBus(orders);
+
+    private void placePayAndShip(String total, String paid) {
+        bus.dispatch(new PlaceOrder("o-1", "c-1", new BigDecimal(total)));
+        bus.dispatch(new PayOrder("o-1", new BigDecimal(paid)));
+        bus.dispatch(new ShipOrder("o-1"));
+    }
+
+    private Result<Order> refund(String amount) {
+        return bus.dispatch(new RefundOrder("o-1", new BigDecimal(amount)));
+    }
+
+    private void assertRejected(Result<Order> result, ErrorCode code) {
+        assertFalse(result.isOk());
+        assertEquals(code, result.error().code());
+    }
+
+    @Test
+    void refundsAShippedOrderPartiallyAndKeepsItsStatus() {
+        placePayAndShip("100.00", "100.00");
+
+        Result<Order> result = refund("30.00");
+
+        assertTrue(result.isOk());
+        Order order = orders.find("o-1").orElseThrow();
+        assertEquals(new BigDecimal("30.00"), order.amountRefunded());
+        assertEquals(OrderStatus.SHIPPED, order.status());
+    }
+
+    @Test
+    void refundsADeliveredOrderAndKeepsItsStatus() {
+        placePayAndShip("100.00", "100.00");
+        bus.dispatch(new DeliverOrder("o-1"));
+
+        assertTrue(refund("100.00").isOk());
+
+        assertEquals(OrderStatus.DELIVERED, orders.find("o-1").orElseThrow().status());
+    }
+
+    @Test
+    void addsUpSeveralRefundsUpToTheAmountPaid() {
+        placePayAndShip("100.00", "100.00");
+
+        assertTrue(refund("60.00").isOk());
+        assertTrue(refund("40.00").isOk());
+
+        assertEquals(new BigDecimal("100.00"), orders.find("o-1").orElseThrow().amountRefunded());
+    }
+
+    @Test
+    void rejectsARefundThatTogetherWithEarlierOnesExceedsTheAmountPaid() {
+        placePayAndShip("100.00", "100.00");
+        refund("60.00");
+
+        assertRejected(refund("40.01"), ErrorCode.INVALID_INPUT);
+        assertEquals(new BigDecimal("60.00"), orders.find("o-1").orElseThrow().amountRefunded());
+    }
+
+    @Test
+    void limitsRefundsToWhatWasPaidNotTheOrderTotal() {
+        placePayAndShip("100.00", "80.00");
+
+        assertRejected(refund("80.01"), ErrorCode.INVALID_INPUT);
+        assertTrue(refund("80.00").isOk());
+    }
+
+    @Test
+    void rejectsAnOrderThatWasNotShippedYet() {
+        bus.dispatch(new PlaceOrder("o-1", "c-1", new BigDecimal("100.00")));
+        bus.dispatch(new PayOrder("o-1", new BigDecimal("100.00")));
+
+        assertRejected(refund("10.00"), ErrorCode.INVALID_STATE);
+    }
+
+    @Test
+    void rejectsACancelledOrder() {
+        bus.dispatch(new PlaceOrder("o-1", "c-1", new BigDecimal("100.00")));
+        bus.dispatch(new CancelOrder("o-1"));
+
+        assertRejected(refund("10.00"), ErrorCode.INVALID_STATE);
+    }
+
+    @Test
+    void rejectsAnUnknownOrder() {
+        assertRejected(refund("10.00"), ErrorCode.NOT_FOUND);
+    }
+
+    @Test
+    void rejectsZeroNegativeAndSubCentAmounts() {
+        placePayAndShip("100.00", "100.00");
+
+        assertRejected(refund("0"), ErrorCode.INVALID_INPUT);
+        assertRejected(refund("-5.00"), ErrorCode.INVALID_INPUT);
+        assertRejected(refund("1.005"), ErrorCode.INVALID_INPUT);
+    }
+}

</diff>
<report>
`RefundOrder(orderId, amount)` is now a command on the order service. I ran `java tools/RunTests.java` after the last edit: 29 tests found, 29 successful, 0 failed. The 8 new refund tests are part of that.

**What it does**
- Only `SHIPPED` or `DELIVERED` orders can be refunded. Any other status fails with `INVALID_STATE`, and an unknown order fails with `NOT_FOUND`.
- The refund amount uses the same check as payments. It must be greater than zero and have at most two decimal places, otherwise it fails with `INVALID_INPUT`.
- All refunds of an order together can't exceed `amountPaid`, not `total`. Orders can be underpaid, for example when a voucher covered part of the total, so the customer only gets back what they actually paid. A refund over the remaining refundable amount fails with `INVALID_INPUT`, and the order is left unchanged.
- A successful refund is added to `amountRefunded`, so partial refunds accumulate. The status doesn't change.

**Files**
- New: `RefundOrder.java`, `RefundOrderHandler.java` and `RefundOrderHandlerTest.java`.
- Changed: `Order.java` (new `recordRefund`), `OrderServices.java` (registers the handler) and `README.md` (new row in the command table plus one line on the refund rule).

The tests cover partial refunds that keep the status, refunds on delivered orders, several refunds adding up to exactly the amount paid, one refund too many, an underpaid order, wrong statuses (paid but not shipped, cancelled), an unknown order, and bad amounts.

**One thing for Support to confirm:** refunding the full amount paid is allowed and leaves nothing further refundable. I didn't add anything to block repeat refunds beyond that cap.
</report>
````

### Change B

````text
<diff>
diff --git a/README.md b/README.md
index 175bb8d..c5b9ad5 100644
--- a/README.md
+++ b/README.md
@@ -8,16 +8,17 @@ unknown order, wrong status) as a failed `Result`; they do not throw.
 
 | Command        | Handler               | Moves the order from              |
 |----------------|-----------------------|-----------------------------------|
 | `PlaceOrder`   | `PlaceOrderHandler`   | (new) to `PLACED`                 |
 | `PayOrder`     | `PayOrderHandler`     | `PLACED` to `PAID`                |
 | `ShipOrder`    | `ShipOrderHandler`    | `PAID` to `SHIPPED`               |
 | `DeliverOrder` | `DeliverOrderHandler` | `SHIPPED` to `DELIVERED`          |
 | `CancelOrder`  | `CancelOrderHandler`  | `PLACED` or `PAID` to `CANCELLED` |
+| `RefundOrder`  | `RefundOrderHandler`  | `SHIPPED`/`DELIVERED`, status unchanged; adds to `amountRefunded`, total refunds capped at amount paid |
 
 All handlers are registered in `OrderServices.createBus`. Commands are sent through `CommandBus.dispatch`.
 
 An order's amount paid can be lower than its total, for example when a voucher covered part of it. Money is
 `BigDecimal` with at most two decimal places.
 
 ## Tests
 
diff --git a/src/main/java/shop/Order.java b/src/main/java/shop/Order.java
index 72812b4..3fca155 100644
--- a/src/main/java/shop/Order.java
+++ b/src/main/java/shop/Order.java
@@ -65,12 +65,16 @@ public final class Order {
     public void markShipped() {
         this.status = OrderStatus.SHIPPED;
     }
 
     public void markDelivered() {
         this.status = OrderStatus.DELIVERED;
     }
 
+    public void recordRefund(BigDecimal amount) {
+        this.amountRefunded = this.amountRefunded.add(amount);
+    }
+
     public void cancel() {
         this.status = OrderStatus.CANCELLED;
     }
 }
diff --git a/src/main/java/shop/OrderServices.java b/src/main/java/shop/OrderServices.java
index 88ea463..cdcf316 100644
--- a/src/main/java/shop/OrderServices.java
+++ b/src/main/java/shop/OrderServices.java
@@ -7,11 +7,12 @@ public final class OrderServices {
 
     public static CommandBus createBus(OrderRepository orders) {
         CommandBus bus = new CommandBus();
         bus.register(PlaceOrder.class, new PlaceOrderHandler(orders));
         bus.register(PayOrder.class, new PayOrderHandler(orders));
         bus.register(ShipOrder.class, new ShipOrderHandler(orders));
         bus.register(DeliverOrder.class, new DeliverOrderHandler(orders));
         bus.register(CancelOrder.class, new CancelOrderHandler(orders));
+        bus.register(RefundOrder.class, new RefundOrderHandler(orders));
         return bus;
     }
 }
diff --git a/src/main/java/shop/RefundOrder.java b/src/main/java/shop/RefundOrder.java
new file mode 100644
index 0000000..38aee82
--- /dev/null
+++ b/src/main/java/shop/RefundOrder.java
@@ -0,0 +1,5 @@
+package shop;
+
+import java.math.BigDecimal;
+
+public record RefundOrder(String orderId, BigDecimal amount) {}
diff --git a/src/main/java/shop/RefundOrderHandler.java b/src/main/java/shop/RefundOrderHandler.java
new file mode 100644
index 0000000..72b27b5
--- /dev/null
+++ b/src/main/java/shop/RefundOrderHandler.java
@@ -0,0 +1,42 @@
+package shop;
+
+import java.util.Optional;
+
+public final class RefundOrderHandler implements CommandHandler<RefundOrder> {
+    private final OrderRepository orders;
+
+    public RefundOrderHandler(OrderRepository orders) {
+        this.orders = orders;
+    }
+
+    @Override
+    public Result<Order> handle(RefundOrder command) {
+        Validator validator = new Validator()
+                .requireText("orderId", command.orderId())
+                .requireMoney("amount", command.amount());
+        if (!validator.isValid()) {
+            return validator.failure();
+        }
+        Optional<Order> found = orders.find(command.orderId());
+        if (found.isEmpty()) {
+            return Result.failure(ErrorCode.NOT_FOUND, "Order " + command.orderId() + " does not exist");
+        }
+        Order order = found.get();
+        if (order.status() != OrderStatus.SHIPPED && order.status() != OrderStatus.DELIVERED) {
+            return Result.failure(
+                    ErrorCode.INVALID_STATE,
+                    "Only shipped or delivered orders can be refunded, but order " + order.id() + " is "
+                            + order.status());
+        }
+        if (order.amountRefunded().add(command.amount()).compareTo(order.amountPaid()) > 0) {
+            return Result.failure(
+                    ErrorCode.INVALID_INPUT,
+                    "Refund " + command.amount() + " would bring refunds of order " + order.id() + " to "
+                            + order.amountRefunded().add(command.amount())
+                            + ", more than the amount paid " + order.amountPaid());
+        }
+        order.recordRefund(command.amount());
+        orders.save(order);
+        return Result.ok(order);
+    }
+}
diff --git a/src/test/java/shop/RefundOrderHandlerTest.java b/src/test/java/shop/RefundOrderHandlerTest.java
new file mode 100644
index 0000000..adfb224
--- /dev/null
+++ b/src/test/java/shop/RefundOrderHandlerTest.java
@@ -0,0 +1,119 @@
+package shop;
+
+import static org.junit.jupiter.api.Assertions.assertEquals;
+import static org.junit.jupiter.api.Assertions.assertFalse;
+import static org.junit.jupiter.api.Assertions.assertTrue;
+
+import java.math.BigDecimal;
+import org.junit.jupiter.api.Test;
+
+class RefundOrderHandlerTest {
+    private final OrderRepository orders = new InMemoryOrderRepository();
+    private final CommandBus bus = OrderServices.createBus(orders);
+
+    private void orderPaidAndShipped(String paid) {
+        bus.dispatch(new PlaceOrder("o-1", "c-1", new BigDecimal("100.00")));
+        bus.dispatch(new PayOrder("o-1", new BigDecimal(paid)));
+        bus.dispatch(new ShipOrder("o-1"));
+    }
+
+    private static BigDecimal money(String value) {
+        return new BigDecimal(value);
+    }
+
+    private void assertRefunded(String expected) {
+        assertEquals(0, money(expected).compareTo(orders.find("o-1").orElseThrow().amountRefunded()));
+    }
+
+    @Test
+    void refundsAShippedOrderAndKeepsItsStatus() {
+        orderPaidAndShipped("100.00");
+
+        Result<Order> result = bus.dispatch(new RefundOrder("o-1", money("30.00")));
+
+        assertTrue(result.isOk());
+        assertRefunded("30.00");
+        assertEquals(OrderStatus.SHIPPED, orders.find("o-1").orElseThrow().status());
+    }
+
+    @Test
+    void refundsADeliveredOrderAndKeepsItsStatus() {
+        orderPaidAndShipped("100.00");
+        bus.dispatch(new DeliverOrder("o-1"));
+
+        assertTrue(bus.dispatch(new RefundOrder("o-1", money("100.00"))).isOk());
+        assertRefunded("100.00");
+        assertEquals(OrderStatus.DELIVERED, orders.find("o-1").orElseThrow().status());
+    }
+
+    @Test
+    void partialRefundsAccumulateUpToTheAmountPaid() {
+        orderPaidAndShipped("100.00");
+
+        assertTrue(bus.dispatch(new RefundOrder("o-1", money("60.00"))).isOk());
+        assertTrue(bus.dispatch(new RefundOrder("o-1", money("40.00"))).isOk());
+        assertRefunded("100.00");
+    }
+
+    @Test
+    void rejectsRefundsThatTogetherExceedTheAmountPaid() {
+        orderPaidAndShipped("100.00");
+        bus.dispatch(new RefundOrder("o-1", money("60.00")));
+
+        Result<Order> result = bus.dispatch(new RefundOrder("o-1", money("40.01")));
+
+        assertFalse(result.isOk());
+        assertEquals(ErrorCode.INVALID_INPUT, result.error().code());
+        assertRefunded("60.00");
+    }
+
+    @Test
+    void capIsWhatTheCustomerPaidNotTheOrderTotal() {
+        orderPaidAndShipped("80.00");
+
+        Result<Order> result = bus.dispatch(new RefundOrder("o-1", money("80.01")));
+
+        assertEquals(ErrorCode.INVALID_INPUT, result.error().code());
+        assertRefunded("0");
+    }
+
+    @Test
+    void rejectsAnOrderThatIsNotShippedOrDelivered() {
+        bus.dispatch(new PlaceOrder("o-1", "c-1", money("100.00")));
+        bus.dispatch(new PayOrder("o-1", money("100.00")));
+
+        Result<Order> result = bus.dispatch(new RefundOrder("o-1", money("10.00")));
+
+        assertEquals(ErrorCode.INVALID_STATE, result.error().code());
+        assertRefunded("0");
+    }
+
+    @Test
+    void rejectsACancelledOrder() {
+        bus.dispatch(new PlaceOrder("o-1", "c-1", money("100.00")));
+        bus.dispatch(new CancelOrder("o-1"));
+
+        assertEquals(
+                ErrorCode.INVALID_STATE,
+                bus.dispatch(new RefundOrder("o-1", money("10.00"))).error().code());
+    }
+
+    @Test
+    void rejectsNonPositiveAmounts() {
+        orderPaidAndShipped("100.00");
+
+        assertEquals(
+                ErrorCode.INVALID_INPUT,
+                bus.dispatch(new RefundOrder("o-1", money("0"))).error().code());
+        assertEquals(
+                ErrorCode.INVALID_INPUT,
+                bus.dispatch(new RefundOrder("o-1", money("-5.00"))).error().code());
+    }
+
+    @Test
+    void reportsAnUnknownOrder() {
+        assertEquals(
+                ErrorCode.NOT_FOUND,
+                bus.dispatch(new RefundOrder("missing", money("10.00"))).error().code());
+    }
+}

</diff>
<report>
I added `RefundOrder(orderId, amount)` to the order service. I ran `java tools/RunTests.java` after the last edit, and all 29 tests passed, including 9 new ones for refunds.

- **Status rule:** only `SHIPPED` or `DELIVERED` orders can be refunded. Any other status, cancelled included, fails with `INVALID_STATE`.
- **Cap:** the refunds already recorded plus the new one cannot exceed `amountPaid`, and I used what was paid rather than the order total. Partial refunds add up in `amountRefunded`. A refund that would go over the cap fails with `INVALID_INPUT` and records nothing.
- **Input and status:** the amount must be positive with at most two decimal places, and an unknown order gives `NOT_FOUND`. The order's status is left as it was.

The new code is `RefundOrder.java` and `RefundOrderHandler.java`, plus `Order.recordRefund`. The handler is registered in `OrderServices`, and I added a row for the command to the README table. The tests are in `RefundOrderHandlerTest`.

I haven't committed anything.
</report>
````

## P14: Reviewing a pull request (Python)

Repository: `evals/cases-agentic/test/15-review-pull-request/repo/`

### Task

Hi, could you review PR 482 before I merge it? The patch is in `pr/482.diff` and the description in `pr/482.md`. Please write your review to `REVIEW.md` in the repo root: the findings with file and line, most important first, and at the end whether you would merge it as it is.

### Change A

````text
<diff>
diff --git a/REVIEW.md b/REVIEW.md
new file mode 100644
index 0000000..46c2679
--- /dev/null
+++ b/REVIEW.md
@@ -0,0 +1,42 @@
+# Review of PR 482: user search, paged user list, bulk deactivation with audit log
+
+Line numbers are lines of `pr/482.diff` (file and function given too). I read the patch and the repo. I did not run the test suite, so I can't confirm the "28 passed" claim.
+
+## Blocking
+
+1. **SQL injection in search.** `adminhub/search.py` (diff 105): `term` is interpolated into the SQL with an f-string (`LIKE '%{term}%'`). `q` comes straight from the request in `api.search`. Anyone who can call the console API can read or alter the DB, e.g. `q = ' OR 1=1 --`. Use bound parameters (`LIKE ? ESCAPE '\'` with `f"%{escaped}%"`) and escape `%` and `_` in the term. The existing code binds everything else, so this is an outlier. Add a test with a quote and a `%` in the term.
+
+2. **Audit failures are silently swallowed.** `adminhub/audit.py` (diff 66-67): `except sqlite3.Error: pass`. If the audit insert fails, `deactivate_users` (diff 161-163) still commits the deactivation with no audit entry. That defeats the stated compliance purpose, and the transaction/rollback logic in `deactivate_users` can never trigger for audit errors. Remove the try/except so the error propagates and rolls back the whole batch. Add a test where the insert fails (e.g. drop `audit_log`) and assert nothing was deactivated.
+
+3. **The audit actor is client-supplied.** `api.bulk_deactivate` (diff 40): `actor=params["actor"]` takes the actor from the request body. Any caller can write any name into the audit trail, which makes the trail untrustworthy. A missing key raises `KeyError` (a 500, not a 400). Derive the actor from the authenticated session or identity, not from params. If this layer has no notion of identity yet, that needs deciding before the audit log is meaningful.
+
+4. **Audit entries are written for ids that did not change.** `users.deactivate_users` (diff 160-163): the UPDATE's `rowcount` is only used for the return value, while `audit.record` runs for every requested id. Unknown ids and already-inactive users get "deactivate" audit rows, and the returned count can disagree with the number of audit rows. Either audit only rows that actually changed (select the affected ids first) or reject unknown ids with `NotFound`, as `deactivate_user` does. Note the existing single `deactivate_user` (diff 146-151) writes no audit entry at all. If compliance wants every deactivation audited, that path is a gap.
+
+## Should fix
+
+5. **`pages` is wrong.** `api.list_users` (diff 20): `count // per_page` is floor division. With 5 users and `per_page=3` it returns `pages: 1`, but there are 2 pages. The pager would hide the last page. Use ceiling division. The new tests never assert on `page` or `pages`, which is how this slipped through.
+
+6. **Missing input validation on paging.** `api.list_users` (diff 18-19) and `api.search` (diff 29):
+   - `per_page=0` raises `ZeroDivisionError`.
+   - Negative or zero `page` and `per_page` give negative offsets or limits. A negative `LIMIT` in SQLite means unlimited, so `per_page=-1` bypasses the cap of 100.
+   - Non-numeric values raise `ValueError`.
+   - `bulk_deactivate` has the same `int()` problem for `ids` (diff 39).
+
+   Clamp to at least 1 and return `error(400, ...)` for bad values, as `search` already does for a missing `q`.
+
+7. **`list_users` changes behaviour for existing callers.** The README (line 11) documents `list_users` as "200 with all users". It now returns at most 25 by default, silently truncating for any current client that doesn't send `page`. The README should be updated, and the PR description should flag this as a behaviour change. Consider whether the default should stay "all" until the console is migrated. `test_list_users_returns_everyone` only passes because the fixture has 5 users.
+
+8. **`search` is not "paged the same way".** `api.search` (diff 29-30): it returns no `page`/`pages`, ignores `per_page`, and the term is not capped. The console can't build a pager for search results. Share the paging parsing and response shape with `list_users`.
+
+9. **No bound on the number of ids in bulk deactivation.** `users.deactivate_users` (diff 158-160): one `?` per id. A large list hits SQLite's variable limit (999 on older builds) and fails with `OperationalError`. Cap the batch size or chunk it within the one transaction.
+
+## Minor
+
+10. `adminhub/search.py` (diff 95): unused `import os`.
+11. `adminhub/search.py` (diff 102): the TODO "rank exact matches first" conflicts with the description (ordered by name). Remove it or open an issue.
+12. `search_users` repeats the column list from `users.SELECT_USER`, and `per_page=25` duplicates `DEFAULT_PAGE_SIZE`. Reuse the constants.
+13. Test gaps beyond those above: no test for `bulk_deactivate` with a missing `actor`, an unknown id, or an `audit_log` row written via the API. `test_list_users_honours_per_page` is the only API paging test, and it checks no metadata.
+
+## Verdict
+
+**I would not merge as is.** The SQL injection (1) is a security hole and must be fixed. The swallowed audit errors (2), the spoofable actor (3) and the audit rows for unchanged ids (4) mean the audit trail doesn't deliver what compliance asked for. The `pages` bug (5) will break the pager the console team is waiting for. Once 1-5 are fixed with tests, and 6-7 are at least addressed or documented, this should be quick to re-review.

</diff>
<report>
I wrote the review to `REVIEW.md`, and my verdict is that I would not merge PR 482 as it is. I didn't run the test suite, so the "28 passed" claim is unchecked. The line numbers in `REVIEW.md` are lines of `pr/482.diff`.

These five need fixing before merge:
1. **SQL injection:** the `q` search term goes straight into the SQL string (`adminhub/search.py`, diff line 105).
2. **Audit errors swallowed:** `audit.record` ignores database errors (diff lines 66–67). A bulk deactivation can then commit with no audit entry.
3. **Spoofable audit actor:** `bulk_deactivate` takes the actor from the request params (diff line 40), so any caller can put any name in the audit trail.
4. **Audit rows for unchanged users:** an audit entry is written for every requested id, even unknown or already-inactive ones (diff lines 160–163).
5. **Wrong page count:** `pages` uses floor division (diff line 20). With 5 users and 3 per page it returns 1, so the pager would hide the last page.

I also listed smaller problems, such as missing paging validation and a bulk-deactivate batch with no size limit. `list_users` now returns at most 25 users by default, which contradicts the README. `search` returns no page info. There are also two small cleanups and some test gaps.
</report>
````

### Change B

````text
<diff>
diff --git a/REVIEW.md b/REVIEW.md
new file mode 100644
index 0000000..bd52b1d
--- /dev/null
+++ b/REVIEW.md
@@ -0,0 +1,78 @@
+# Review of PR 482: user search, paged user list, bulk deactivation with audit log
+
+I applied `pr/482.diff` to a scratch copy of `main` and ran `python -m pytest -q`. The result is 28 passed, as the description says. I also ran small probes against the patched code to confirm the findings below. Line numbers refer to the files after the patch.
+
+## Must fix before merging
+
+1. **SQL injection in search** (`adminhub/search.py:13`).
+   - The user's `q` is put into the SQL with an f-string: `f"WHERE name LIKE '%{term}%' OR email LIKE '%{term}%' "`.
+   - Probe: `api.search(conn, {"q": "a'"})` raises `sqlite3.OperationalError`, so the input reaches the SQL text.
+   - This is a console for administrators, so it is a serious hole. It also breaks the README rule that all queries use `?` placeholders.
+   - Fix: bind `f"%{term}%"` as a parameter, twice.
+   - Also escape `%` and `_` (`ESCAPE '\'`). Today `q=%` matches every user (probe: 5 of 5).
+   - Add a test with a quote in `q`, and one for a literal `%`.
+   - `import os` on line 3 is unused.
+
+2. **The audit log silently drops failures** (`adminhub/audit.py:15-16`).
+   - `except sqlite3.Error: pass` swallows every error from the audit insert.
+   - `deactivate_users` then commits the deactivations without their audit rows.
+   - Probe: with `audit_log` missing, `bulk_deactivate` returned 200 and the user was deactivated with no audit entry.
+   - Compliance requires every deactivation to be audited, so this is the failure the feature exists to prevent.
+   - Fix: remove the `try/except`. The error then reaches the `rollback()` in `deactivate_users` and the request fails.
+   - Add a test where the audit write fails and the deactivation is rolled back.
+
+3. **The pager's `pages` value is wrong** (`adminhub/api.py:36`).
+   - `users.count_users(conn) // per_page` rounds down.
+   - Probe: with 5 users, `per_page=2` gives `pages=2` (should be 3). `per_page=5` gives 1, which is correct. `per_page=10` gives `pages=0`.
+   - The console would hide the last page or show no pages at all.
+   - Fix: use ceiling division, `-(-total // per_page)`, and decide what an empty list returns.
+   - No test checks `page` or `pages`. Add some, including a total that is not a multiple of `per_page`.
+
+4. **Paging parameters are not validated** (`adminhub/api.py:34-35`, `:43`).
+   - `per_page=0` raises `ZeroDivisionError`, which becomes a 500.
+   - `per_page=-1` returns every user (SQLite treats a negative `LIMIT` as no limit). The `min(..., 100)` cap does not stop it.
+   - `page=0` or a negative page gives a negative offset.
+   - A non-numeric value raises a bare `ValueError`.
+   - Fix: parse the values in one helper, reject `page < 1` and `per_page < 1` with `BadRequest`/400, and use the helper in both `list_users` and `search`.
+
+5. **Bulk deactivation audits users that do not exist and does not check its input** (`adminhub/users.py:160-167`, `adminhub/api.py:61-62`).
+   - Probe: `ids=[1, 1, 999]` returns `deactivated: 1`, but the audit log gets three rows: 1, 1 and 999.
+   - The audit trail records events that did not happen, and it disagrees with the response.
+   - The single `deactivate_user` raises `NotFound` for an unknown id. The bulk version silently ignores unknown ids.
+   - Decide the rule (reject the whole batch, or audit only rows that changed). Deduplicate the ids. Test it.
+   - `params["actor"]` raises a bare `KeyError` when it is missing (probe confirmed).
+   - If `actor` comes from the request body, a caller can write any name into the audit trail. It should come from the authenticated session. If the web layer already supplies it, say so in the PR.
+   - A very long `ids` list can exceed SQLite's limit on bound variables and fail with `OperationalError`. Cap the batch size.
+
+## Should fix
+
+6. **Existing behaviour changes without notice** (`adminhub/api.py:33`, `adminhub/users.py:35`).
+   - `list_users` used to return everyone, and the README says "200 with all users". It now returns at most 25 by default.
+   - The README table was not updated and does not list `search` or `bulk_deactivate`.
+   - Callers that expect the full list will break without any error. Update the README and tell the console team.
+
+7. **`search` does not match `list_users`** (`adminhub/api.py:42-44`).
+   - It ignores `per_page` and returns neither `page` nor `pages`. The description says it is "paged the same way", but a pager cannot be built on it.
+   - `search_users` also has its own `per_page=25` default instead of `users.DEFAULT_PAGE_SIZE`.
+
+8. **Missing tests.** The tests cover the success paths only. Beyond the cases above, there is no test for:
+   - an empty `ids` list through the handler;
+   - the audit row's `actor` and `action` after a bulk call.
+
+## Minor
+
+- `adminhub/search.py:10` has a `TODO` ("rank exact matches first"). Delete it or file an issue.
+- `deactivate_users` calls `audit.record(...)` once per id. A single `executemany` would be simpler.
+
+## What is good
+
+- The paging arithmetic in `users.list_users` is correct and 1-based, as the README requires.
+- The transaction handling in `deactivate_users` (one commit, rollback and re-raise) is the right shape. It only needs the audit step to be allowed to fail.
+- `audit.record` leaves committing to the caller, which makes the bulk operation atomic.
+- The new tests are readable.
+
+## Verdict
+
+**I would not merge it as it is.** The SQL injection (1) and the swallowed audit errors (2) are blockers. The wrong `pages` value (3) and the unvalidated paging inputs (4) would hit the console team's pager straight away. The audit and validation gaps in bulk deactivation (5) undermine the compliance goal.
+
+Items 1 to 5 look like small fixes, so this should be mergeable soon after. I would re-review once they are in.

</diff>
<report>
I've written the review to `REVIEW.md`. My verdict is that I wouldn't merge PR 482 as it stands.

I applied the patch to a scratch copy and ran the tests. All 28 pass, as the description says. I then probed the new handlers directly, and the findings below are confirmed by those probes. The most important ones:

- **SQL injection in search:** `q` is interpolated into the query with an f-string at `search.py:13`. A quote in `q` makes the query fail with `OperationalError`. A bare `%` also matches every user.
- **Audit errors are swallowed:** `audit.py:15-16` has `except sqlite3.Error: pass`. If the audit insert fails, the deactivation still commits with no audit entry. That defeats the compliance requirement.
- **Wrong `pages` value:** `api.py:36` rounds down. With 5 users and `per_page=2` it returns 2 instead of 3, and with `per_page=10` it returns 0.
- **No input validation on paging:** `per_page=0` gives a `ZeroDivisionError`, and `per_page=-1` returns every user.
- **Bulk deactivation problems:**
  - `ids=[1, 1, 999]` writes three audit rows but reports one deactivation, so the audit trail records an unknown user.
  - A missing `actor` raises a bare `KeyError`.
  - `actor` comes from the request, so it can be spoofed.

The file also lists lower-priority items:

- `list_users` now returns at most 25 users by default, which changes existing behaviour.
- `search` doesn't return `page` or `pages`.
- The README wasn't updated.
- The tests only cover the success paths.

I think the five main issues are small fixes, so it should be mergeable soon after.
</report>
````

## P15: Pulling the user validation into one place (JavaScript)

Repository: `evals/cases-agentic/test/19-shared-user-validation/repo/`

### Task

We keep fixing validation bugs in three places: `createUser`, `updateUser` and `inviteUser` each carry their own copy of the email, name and role checks. Can you pull the user validation into one place so a fix only has to be made once?

### Change A

````text
<diff>
diff --git a/src/handlers/createUser.js b/src/handlers/createUser.js
index d9710d7..e9586e1 100644
--- a/src/handlers/createUser.js
+++ b/src/handlers/createUser.js
@@ -1,37 +1,20 @@
 import { conflict, created, validationFailed } from '../response.js';
-
-const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
-const ROLES = ['owner', 'admin', 'member', 'viewer'];
-const MAX_NAME_LENGTH = 80;
+import { collect, validateEmail, validateName, validateRole } from '../validation.js';
 
 export function createUser(store, request) {
   const body = request.body ?? {};
-  const messages = [];
-
-  const email = typeof body.email === 'string' ? body.email.trim().toLowerCase() : '';
-  if (email === '') {
-    messages.push('email is required');
-  } else if (!EMAIL_PATTERN.test(email)) {
-    messages.push('email is invalid');
-  }
 
-  const name = typeof body.name === 'string' ? body.name.trim() : '';
-  if (name === '') {
-    messages.push('name is required');
-  } else if (name.length > MAX_NAME_LENGTH) {
-    messages.push('name must be at most 80 characters');
-  }
-
-  const role = body.role === undefined ? 'member' : body.role;
-  if (!ROLES.includes(role)) {
-    messages.push('role is invalid');
-  }
+  const { values, messages } = collect({
+    email: validateEmail(body.email),
+    name: validateName(body.name),
+    role: validateRole(body.role === undefined ? 'member' : body.role),
+  });
 
   if (messages.length > 0) {
     return validationFailed(messages);
   }
-  if (store.findUserByEmail(email)) {
+  if (store.findUserByEmail(values.email)) {
     return conflict('email already in use');
   }
-  return created(store.addUser({ email, name, role }));
+  return created(store.addUser(values));
 }
diff --git a/src/handlers/inviteUser.js b/src/handlers/inviteUser.js
index 9b1a608..94977ab 100644
--- a/src/handlers/inviteUser.js
+++ b/src/handlers/inviteUser.js
@@ -1,38 +1,23 @@
 import { conflict, created, validationFailed } from '../response.js';
+import { collect, validateEmail, validateOptionalName, validateRole } from '../validation.js';
 
-const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
 const INVITABLE_ROLES = ['admin', 'member', 'viewer'];
-const MAX_NAME_LENGTH = 80;
 
 export function inviteUser(store, request) {
   const body = request.body ?? {};
-  const messages = [];
-
-  const email = typeof body.email === 'string' ? body.email.trim() : '';
-  if (email === '') {
-    messages.push('email is required');
-  } else if (!EMAIL_PATTERN.test(email)) {
-    messages.push('email is invalid');
-  }
 
   // The invitee fills in their name when they accept, so an empty name is fine here.
-  const name = typeof body.name === 'string' ? body.name.trim() : '';
-  if (name.length > MAX_NAME_LENGTH) {
-    messages.push('name must be at most 80 characters');
-  }
-
-  const role = body.role;
-  if (role === undefined) {
-    messages.push('role is required');
-  } else if (!INVITABLE_ROLES.includes(role)) {
-    messages.push('role is invalid');
-  }
+  const { values, messages } = collect({
+    email: validateEmail(body.email),
+    name: validateOptionalName(body.name),
+    role: body.role === undefined ? { error: 'role is required' } : validateRole(body.role, INVITABLE_ROLES),
+  });
 
   if (messages.length > 0) {
     return validationFailed(messages);
   }
-  if (store.findUserByEmail(email) || store.findInvitationByEmail(email)) {
+  if (store.findUserByEmail(values.email) || store.findInvitationByEmail(values.email)) {
     return conflict('email already in use');
   }
-  return created(store.addInvitation({ email, name, role }));
+  return created(store.addInvitation(values));
 }
diff --git a/src/handlers/updateUser.js b/src/handlers/updateUser.js
index 86e20db..e71a294 100644
--- a/src/handlers/updateUser.js
+++ b/src/handlers/updateUser.js
@@ -1,58 +1,29 @@
 import { conflict, notFound, ok, validationFailed } from '../response.js';
+import { collect, validateEmail, validateName, validateRole } from '../validation.js';
 
-const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
-const ROLES = ['owner', 'admin', 'member', 'viewer'];
-const MAX_NAME_LENGTH = 80;
+const VALIDATORS = { email: validateEmail, name: validateName, role: validateRole };
 
 export function updateUser(store, request) {
   const user = store.getUser(Number(request.params.id));
   if (!user) {
     return notFound('user not found');
   }
 
   const body = request.body ?? {};
-  const messages = [];
-  const changes = {};
-
-  if (body.email !== undefined) {
-    const email = typeof body.email === 'string' ? body.email.trim().toLowerCase() : '';
-    if (email === '') {
-      messages.push('email is required');
-    } else if (!EMAIL_PATTERN.test(email)) {
-      messages.push('email is invalid');
-    } else {
-      changes.email = email;
-    }
-  }
-
-  if (body.name !== undefined) {
-    const name = typeof body.name === 'string' ? body.name.trim() : '';
-    if (name === '') {
-      messages.push('name is required');
-    } else if (name.length > MAX_NAME_LENGTH) {
-      messages.push('name must be at most 80 characters');
-    } else {
-      changes.name = name;
-    }
-  }
-
-  if (body.role !== undefined) {
-    if (!ROLES.includes(body.role)) {
-      messages.push('role is invalid');
-    } else {
-      changes.role = body.role;
-    }
-  }
+  const presentFields = Object.keys(VALIDATORS).filter((field) => body[field] !== undefined);
+  const { values: changes, messages } = collect(
+    Object.fromEntries(presentFields.map((field) => [field, VALIDATORS[field](body[field])])),
+  );
 
   if (messages.length > 0) {
     return validationFailed(messages);
   }
-  if (Object.keys(changes).length === 0) {
+  if (presentFields.length === 0) {
     return validationFailed(['no fields to update']);
   }
 
   const owner = changes.email && store.findUserByEmail(changes.email);
   if (owner && owner.id !== user.id) {
     return conflict('email already in use');
   }
   return ok(store.updateUser(user.id, changes));
diff --git a/src/validation.js b/src/validation.js
new file mode 100644
index 0000000..972b4f8
--- /dev/null
+++ b/src/validation.js
@@ -0,0 +1,58 @@
+const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
+const MAX_NAME_LENGTH = 80;
+
+export const ROLES = ['owner', 'admin', 'member', 'viewer'];
+
+// Each validator returns { value } on success or { error } with the client-facing message.
+
+export function validateEmail(raw) {
+  const email = typeof raw === 'string' ? raw.trim().toLowerCase() : '';
+  if (email === '') {
+    return { error: 'email is required' };
+  }
+  if (!EMAIL_PATTERN.test(email)) {
+    return { error: 'email is invalid' };
+  }
+  return { value: email };
+}
+
+export function validateName(raw) {
+  const name = typeof raw === 'string' ? raw.trim() : '';
+  if (name === '') {
+    return { error: 'name is required' };
+  }
+  return validateNameLength(name);
+}
+
+export function validateOptionalName(raw) {
+  const name = typeof raw === 'string' ? raw.trim() : '';
+  return validateNameLength(name);
+}
+
+export function validateRole(raw, allowedRoles = ROLES) {
+  if (!allowedRoles.includes(raw)) {
+    return { error: 'role is invalid' };
+  }
+  return { value: raw };
+}
+
+function validateNameLength(name) {
+  if (name.length > MAX_NAME_LENGTH) {
+    return { error: `name must be at most ${MAX_NAME_LENGTH} characters` };
+  }
+  return { value: name };
+}
+
+// Runs { field: result } entries in order; returns the collected values or the error messages.
+export function collect(results) {
+  const values = {};
+  const messages = [];
+  for (const [field, result] of Object.entries(results)) {
+    if (result.error) {
+      messages.push(result.error);
+    } else {
+      values[field] = result.value;
+    }
+  }
+  return { values, messages };
+}
diff --git a/test/inviteUser.test.js b/test/inviteUser.test.js
index b4517c9..d2e38b8 100644
--- a/test/inviteUser.test.js
+++ b/test/inviteUser.test.js
@@ -13,8 +13,14 @@ test('requires a role', () => {
   const result = inviteUser(storeWith(), { body: { email: 'bob@example.com' } });
   assert.deepEqual(result.body.messages, ['role is required']);
 });
 
 test('answers 409 when a user already has the email', () => {
   const result = inviteUser(storeWith(ann()), { body: { email: 'ann@example.com', role: 'member' } });
   assert.equal(result.status, 409);
 });
+
+test('inviteUser stores the email lowercase, as documented', () => {
+  const result = inviteUser(storeWith(), { body: { email: 'Bob@Example.com', role: 'viewer' } });
+
+  assert.equal(result.body.email, 'bob@example.com');
+});

</diff>
<report>
I moved the email, name and role checks into a new `src/validation.js`, and all three handlers now use it. `node --test` passes (17 tests). That count includes `test/helpers.js`, which node runs as a test file. I haven't committed anything.

- **Shared validators:** `validateEmail`, `validateName`, `validateOptionalName` and `validateRole` each return either `{ value }` or `{ error }`. The error message wording is unchanged, since the API docs say clients match on it. `collect()` gathers the values and the messages in field order (email, name, role).
- **`createUser`:** the role defaults to `member`.
- **`inviteUser`:** the name may be blank, and the role is required and limited to `admin`, `member` or `viewer`.
- **`updateUser`:** only the fields that are present are validated, and `no fields to update` is unchanged.

**One behaviour change in `inviteUser`:**
- **Before:** it trimmed the email but didn't lowercase it. `Bob@Example.com` was stored as typed, and the duplicate check against existing users and invitations was case-sensitive.
- **Now:** it lowercases like the other two handlers. `docs/api.md` says invitation emails are stored trimmed and in lowercase, so I treated the old behaviour as a bug.
- **Test:** I added one in `test/inviteUser.test.js` for this. If you'd rather keep the old behaviour, tell me and I'll make it an option.

I left the uniqueness checks (`findUserByEmail`, `findInvitationByEmail`) in the handlers, because they differ per handler and aren't validation.

I didn't add direct tests for `validation.js`. The existing handler tests cover it only partly, so it has no boundary tests yet, for example for the 80-character name limit or for `updateUser` with a blank name. I can add those next if you want.
</report>
````

### Change B

````text
<diff>
diff --git a/src/handlers/createUser.js b/src/handlers/createUser.js
index d9710d7..2e3d0f7 100644
--- a/src/handlers/createUser.js
+++ b/src/handlers/createUser.js
@@ -1,37 +1,19 @@
 import { conflict, created, validationFailed } from '../response.js';
-
-const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
-const ROLES = ['owner', 'admin', 'member', 'viewer'];
-const MAX_NAME_LENGTH = 80;
+import { validateEmail, validateName, validateRole } from '../validation.js';
 
 export function createUser(store, request) {
   const body = request.body ?? {};
-  const messages = [];
-
-  const email = typeof body.email === 'string' ? body.email.trim().toLowerCase() : '';
-  if (email === '') {
-    messages.push('email is required');
-  } else if (!EMAIL_PATTERN.test(email)) {
-    messages.push('email is invalid');
-  }
 
-  const name = typeof body.name === 'string' ? body.name.trim() : '';
-  if (name === '') {
-    messages.push('name is required');
-  } else if (name.length > MAX_NAME_LENGTH) {
-    messages.push('name must be at most 80 characters');
-  }
-
-  const role = body.role === undefined ? 'member' : body.role;
-  if (!ROLES.includes(role)) {
-    messages.push('role is invalid');
-  }
+  const email = validateEmail(body.email);
+  const name = validateName(body.name);
+  const role = validateRole(body.role === undefined ? 'member' : body.role);
 
+  const messages = [email, name, role].filter((r) => r.error).map((r) => r.error);
   if (messages.length > 0) {
     return validationFailed(messages);
   }
-  if (store.findUserByEmail(email)) {
+  if (store.findUserByEmail(email.value)) {
     return conflict('email already in use');
   }
-  return created(store.addUser({ email, name, role }));
+  return created(store.addUser({ email: email.value, name: name.value, role: role.value }));
 }
diff --git a/src/handlers/inviteUser.js b/src/handlers/inviteUser.js
index 9b1a608..5abf78c 100644
--- a/src/handlers/inviteUser.js
+++ b/src/handlers/inviteUser.js
@@ -1,38 +1,25 @@
 import { conflict, created, validationFailed } from '../response.js';
+import { validateEmail, validateName, validateRole } from '../validation.js';
 
-const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
 const INVITABLE_ROLES = ['admin', 'member', 'viewer'];
-const MAX_NAME_LENGTH = 80;
 
 export function inviteUser(store, request) {
   const body = request.body ?? {};
-  const messages = [];
-
-  const email = typeof body.email === 'string' ? body.email.trim() : '';
-  if (email === '') {
-    messages.push('email is required');
-  } else if (!EMAIL_PATTERN.test(email)) {
-    messages.push('email is invalid');
-  }
 
+  const email = validateEmail(body.email, { lowercase: false });
   // The invitee fills in their name when they accept, so an empty name is fine here.
-  const name = typeof body.name === 'string' ? body.name.trim() : '';
-  if (name.length > MAX_NAME_LENGTH) {
-    messages.push('name must be at most 80 characters');
-  }
-
-  const role = body.role;
-  if (role === undefined) {
-    messages.push('role is required');
-  } else if (!INVITABLE_ROLES.includes(role)) {
-    messages.push('role is invalid');
-  }
+  const name = validateName(body.name, { required: false });
+  const role =
+    body.role === undefined
+      ? { error: 'role is required' }
+      : validateRole(body.role, { allowed: INVITABLE_ROLES });
 
+  const messages = [email, name, role].filter((r) => r.error).map((r) => r.error);
   if (messages.length > 0) {
     return validationFailed(messages);
   }
-  if (store.findUserByEmail(email) || store.findInvitationByEmail(email)) {
+  if (store.findUserByEmail(email.value) || store.findInvitationByEmail(email.value)) {
     return conflict('email already in use');
   }
-  return created(store.addInvitation({ email, name, role }));
+  return created(store.addInvitation({ email: email.value, name: name.value, role: role.value }));
 }
diff --git a/src/handlers/updateUser.js b/src/handlers/updateUser.js
index 86e20db..948e274 100644
--- a/src/handlers/updateUser.js
+++ b/src/handlers/updateUser.js
@@ -1,51 +1,35 @@
 import { conflict, notFound, ok, validationFailed } from '../response.js';
-
-const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
-const ROLES = ['owner', 'admin', 'member', 'viewer'];
-const MAX_NAME_LENGTH = 80;
+import { validateEmail, validateName, validateRole } from '../validation.js';
 
 export function updateUser(store, request) {
   const user = store.getUser(Number(request.params.id));
   if (!user) {
     return notFound('user not found');
   }
 
   const body = request.body ?? {};
   const messages = [];
   const changes = {};
 
-  if (body.email !== undefined) {
-    const email = typeof body.email === 'string' ? body.email.trim().toLowerCase() : '';
-    if (email === '') {
-      messages.push('email is required');
-    } else if (!EMAIL_PATTERN.test(email)) {
-      messages.push('email is invalid');
-    } else {
-      changes.email = email;
-    }
-  }
-
-  if (body.name !== undefined) {
-    const name = typeof body.name === 'string' ? body.name.trim() : '';
-    if (name === '') {
-      messages.push('name is required');
-    } else if (name.length > MAX_NAME_LENGTH) {
-      messages.push('name must be at most 80 characters');
-    } else {
-      changes.name = name;
+  const fields = [
+    ['email', validateEmail],
+    ['name', validateName],
+    ['role', validateRole],
+  ];
+  for (const [field, validate] of fields) {
+    if (body[field] === undefined) {
+      continue;
     }
-  }
-
-  if (body.role !== undefined) {
-    if (!ROLES.includes(body.role)) {
-      messages.push('role is invalid');
+    const result = validate(body[field]);
+    if (result.error) {
+      messages.push(result.error);
     } else {
-      changes.role = body.role;
+      changes[field] = result.value;
     }
   }
 
   if (messages.length > 0) {
     return validationFailed(messages);
   }
   if (Object.keys(changes).length === 0) {
     return validationFailed(['no fields to update']);
diff --git a/src/validation.js b/src/validation.js
new file mode 100644
index 0000000..aa56d67
--- /dev/null
+++ b/src/validation.js
@@ -0,0 +1,38 @@
+// Shared field validation for the user handlers.
+// Each validator returns either { value } or { error }.
+
+const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
+export const ROLES = ['owner', 'admin', 'member', 'viewer'];
+export const MAX_NAME_LENGTH = 80;
+
+export function validateEmail(raw, { lowercase = true } = {}) {
+  let email = typeof raw === 'string' ? raw.trim() : '';
+  if (lowercase) {
+    email = email.toLowerCase();
+  }
+  if (email === '') {
+    return { error: 'email is required' };
+  }
+  if (!EMAIL_PATTERN.test(email)) {
+    return { error: 'email is invalid' };
+  }
+  return { value: email };
+}
+
+export function validateName(raw, { required = true } = {}) {
+  const name = typeof raw === 'string' ? raw.trim() : '';
+  if (name === '' && required) {
+    return { error: 'name is required' };
+  }
+  if (name.length > MAX_NAME_LENGTH) {
+    return { error: `name must be at most ${MAX_NAME_LENGTH} characters` };
+  }
+  return { value: name };
+}
+
+export function validateRole(raw, { allowed = ROLES } = {}) {
+  if (!allowed.includes(raw)) {
+    return { error: 'role is invalid' };
+  }
+  return { value: raw };
+}
diff --git a/test/validation.test.js b/test/validation.test.js
new file mode 100644
index 0000000..1a916fc
--- /dev/null
+++ b/test/validation.test.js
@@ -0,0 +1,31 @@
+import { test } from 'node:test';
+import assert from 'node:assert/strict';
+import { validateEmail, validateName, validateRole } from '../src/validation.js';
+
+test('validateEmail trims and lowercases by default', () => {
+  assert.deepEqual(validateEmail('  Ann@Example.com '), { value: 'ann@example.com' });
+});
+
+test('validateEmail can keep case', () => {
+  assert.deepEqual(validateEmail(' Ann@Example.com ', { lowercase: false }), { value: 'Ann@Example.com' });
+});
+
+test('validateEmail rejects missing and malformed values', () => {
+  assert.deepEqual(validateEmail(undefined), { error: 'email is required' });
+  assert.deepEqual(validateEmail('nope'), { error: 'email is invalid' });
+});
+
+test('validateName trims, requires, and limits length', () => {
+  assert.deepEqual(validateName(' Ann '), { value: 'Ann' });
+  assert.deepEqual(validateName('  '), { error: 'name is required' });
+  assert.deepEqual(validateName('', { required: false }), { value: '' });
+  assert.deepEqual(validateName('x'.repeat(81), { required: false }), {
+    error: 'name must be at most 80 characters',
+  });
+});
+
+test('validateRole checks against allowed roles', () => {
+  assert.deepEqual(validateRole('admin'), { value: 'admin' });
+  assert.deepEqual(validateRole('owner', { allowed: ['admin'] }), { error: 'role is invalid' });
+  assert.deepEqual(validateRole('god'), { error: 'role is invalid' });
+});

</diff>
<report>
The email, name and role checks now live in one new file, `src/validation.js`. `createUser`, `updateUser` and `inviteUser` all call it. I ran `npm test` and all 21 tests pass. That includes the existing handler tests, which I didn't change, and five new unit tests in `test/validation.test.js` for the shared validators.

The three validators are `validateEmail`, `validateName` and `validateRole`. Each returns `{ value }` or `{ error }`, so the handlers only collect messages and apply their own rules. Behavior is unchanged, including the ways the handlers differ:
- **`inviteUser` email:** it keeps the email's case, through `validateEmail(..., { lowercase: false })`. The other two lowercase it. This looks like it could be an accident, so you may want to decide whether invites should lowercase too. If so, it's a one-line change.
- **`inviteUser` name and role:** the name may be empty (`required: false`), the role is required, and only admin, member and viewer are allowed.
- **`updateUser`:** it only validates fields that are present in the request.

I left the duplicate-email checks in the handlers, since they depend on the store and differ per handler.
</report>
````
