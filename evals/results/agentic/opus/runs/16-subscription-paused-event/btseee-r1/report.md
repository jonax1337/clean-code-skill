The `subscription_paused` event is in place in all three places that handle events. All 19 tests pass (7 of them new), and the typecheck is clean. Nothing is committed.

**What changed**
- **`src/events.ts`**: new `SubscriptionPaused` event with `resumeOn` and `reason`, added to the `SubscriptionEvent` union.
- **`src/subscription.ts`**:
  - Added a `paused` status and a `resumeOn: string | null` field on `Subscription`, which starts as `null`.
  - Pausing only works on an active subscription. In any other status, including already paused, the event changes nothing.
  - `payment_failed` now leaves a paused subscription as it is. `payment_recovered` already only acted on past-due subscriptions, so it needed no change.
  - Cancelling sets `resumeOn` back to `null`.
- **`src/audit.ts`**: writes `resumeOn=<date> reason="<quoted>"`, quoting the reason the same way cancellations do.
- **`src/notifier.ts`**: sends one customer email, `subscription-paused`, with data `{ resumeOn }`.

**Tests added**
- **State**: pausing an active subscription; a pause on a past-due, cancelled or already-paused subscription changing nothing; payment events being ignored while paused; cancelling while paused. The test for a new subscription also checks that `resumeOn` starts as `null`.
- **Audit**: your exact example line.
- **Notifications**: only the customer email is sent.

**Two things to be aware of**
- **Plan changes while paused** still switch the plan, as they do in every other status, because you didn't say otherwise. If a paused subscription shouldn't allow that, it's a two-line guard.
- **`resumeOn` isn't checked against `YYYY-MM-DD`.** It's typed as a plain string, the same as the other event fields, which aren't validated either.