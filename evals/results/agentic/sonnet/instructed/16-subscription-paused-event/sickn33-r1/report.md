The `subscription_paused` event is in, with tests. All 19 tests pass and the typecheck is clean.

- **Event** (`src/events.ts`): `SubscriptionPaused` has `resumeOn` (`YYYY-MM-DD`) and `reason`, and is part of the `SubscriptionEvent` union.
- **State** (`src/subscription.ts`): there is a new `paused` status and a `resumeOn: string | null` field, which is `null` unless the subscription is paused.
  - Only an `active` subscription can be paused. In any other status the event changes nothing.
  - A failed payment no longer turns a paused subscription `past_due`. A recovery already ignored anything that wasn't `past_due`.
  - Cancelling a paused subscription works as before and sets `resumeOn` to `null`.
- **Audit** (`src/audit.ts`): the line reads `… subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way as the cancellation reason.
- **Notifications** (`src/notifier.ts`): the customer gets a `subscription-paused` email with `resumeOn` in its data, and nobody else is notified.

New tests cover the audit line, the notification, pausing, the non-active no-ops, payment events on a paused subscription, and cancelling a paused one.

Resuming is left out, as you asked. Nothing moves a subscription out of `paused` except cancelling it.