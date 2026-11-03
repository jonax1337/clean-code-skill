Billing now handles a `subscription_paused` event. `npm test` passes (20 tests) and `npm run typecheck` reports no errors. I didn't commit anything.

- **Event** (`src/events.ts`): `SubscriptionPaused` has `resumeOn` and `reason`, and is part of the `SubscriptionEvent` union.
- **State** (`src/subscription.ts`):
  - A new `paused` status and a `resumeOn: string | null` field, which is `null` unless the subscription is paused.
  - Pausing an active subscription sets `paused` and stores `resumeOn`. In any other status the event changes nothing. That includes a second pause on an already paused subscription, so its `resumeOn` isn't overwritten.
  - `payment_failed` now leaves a paused subscription alone. `payment_recovered` already did, because it only acts on `past_due`.
  - Cancelling a paused subscription works as before and also sets `resumeOn` to `null`.
- **Audit** (`src/audit.ts`): the line reads `… subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted like the cancellation reason.
- **Notifier** (`src/notifier.ts`): the customer gets a `subscription-paused` email with `resumeOn`, and nobody else is notified.
- **Tests:** I added tests for the audit line, the notification, pausing, pausing from other statuses, payment events while paused, and cancelling while paused.

I left resuming out, as you asked. Nothing validates the `YYYY-MM-DD` format of `resumeOn`, and the other events don't validate their inputs either.