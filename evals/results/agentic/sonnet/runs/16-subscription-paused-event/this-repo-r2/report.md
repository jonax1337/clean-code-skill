The `subscription_paused` event is in. `npm run typecheck` is clean and `npm test` shows 19 passed, 0 failed (4 of them new for subscription state, 1 each for audit and notifications).

- **Event** (`src/events.ts`): `SubscriptionPaused` carries `resumeOn` and `reason`.
- **State** (`src/subscription.ts`):
  - There is a new `paused` status and a `resumeOn` field that is `null` unless the subscription is paused.
  - Only an active subscription pauses. In any other status, including one that is already paused, the event changes nothing.
  - `payment_failed` now leaves a paused subscription alone. `payment_recovered` already did, because it only acts on `past_due`.
  - Cancelling a paused subscription works as before and sets `resumeOn` back to `null`.
- **Audit** (`src/audit.ts`): the line reads `… subscription_paused resumeOn=2025-05-01 reason="vacation"`. The reason is quoted the same way as the cancellation reason.
- **Notifier** (`src/notifier.ts`): the customer gets a `subscription-paused` email with `resumeOn`, and nobody else is notified.

I left out resuming. I also didn't validate that `resumeOn` is a real `YYYY-MM-DD` date or that it's in the future. Nothing else in the code validates event fields, so I kept to that.