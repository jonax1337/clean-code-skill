Pausing is implemented across the event type, state, audit log, and notifier. Tests pass (18, up from 13) and typecheck is clean. I did not commit.

**Changes**

- **`src/events.ts`**: new `SubscriptionPaused` event with `resumeOn` and `reason`.
- **`src/subscription.ts`**:
  - `status` can now be `"paused"`, and `Subscription` has `resumeOn: string | null`. It starts as `null`, and cancelling clears it.
  - A pause only applies to an active subscription. In any other status it returns the same state object.
  - `payment_failed` leaves a paused subscription alone. `payment_recovered` already ignored anything that isn't `past_due`, so a paused subscription is untouched by it too.
- **`src/audit.ts`**: `subscription_paused resumeOn=2025-05-01 reason="vacation"`, using the same `JSON.stringify` quoting as the cancellation reason.
- **`src/notifier.ts`**: one customer email, `subscription-paused`, with data `{ resumeOn }`. No billing-team notification.
- **Tests**: a pause audit line, the customer-only email, pause/cancel round trip, payment events being ignored while paused, and pause being rejected for past-due, already-paused and canceled subscriptions. The existing "started" test also checks that `resumeOn` starts as `null`.

**Choices I made**

- The email data carries only `resumeOn`, as you specified. The reason is in the event and the audit line but not in the email. If the template should show the reason too, that's a one-line change.
- `resumeOn` is not validated as `YYYY-MM-DD` at runtime, which matches how `occurredAt` is handled. Say if you want a check added.
- Pausing a past-due subscription does nothing, per the spec. That means a customer with a failed payment can't pause until the payment is recovered.