The `subscription_paused` event is in. Typecheck is clean and all 19 tests pass, including 5 new ones for pausing.

- **Event (`src/events.ts`):** the new `SubscriptionPaused` carries `resumeOn` and `reason` and is part of the `SubscriptionEvent` union.
- **State (`src/subscription.ts`):**
  - Added a `paused` status and a `resumeOn` field that is `null` unless the subscription is paused.
  - Only an `active` subscription can be paused; in any other status the event changes nothing.
  - `payment_failed` now leaves a paused subscription alone. `payment_recovered` already ignored anything that isn't past due, so it needed no change.
  - Cancelling clears `resumeOn`.
- **Audit log (`src/audit.ts`):** the line looks like `… subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way as the cancellation reason.
- **Notifications (`src/notifier.ts`):** the customer gets a `subscription-paused` email with `resumeOn`, and nobody else is notified.

I added tests for the audit line, the notification, the pause state, the non-active no-ops, payment events while paused, and cancelling a paused subscription. Resuming is left out, as you asked.

I didn't validate the `YYYY-MM-DD` format of `resumeOn`, since the other events don't validate their fields either.