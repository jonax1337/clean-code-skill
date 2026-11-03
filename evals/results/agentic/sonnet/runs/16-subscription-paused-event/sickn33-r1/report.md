The `subscription_paused` event is in. Typecheck passes and all 19 tests pass, including the new ones. I didn't commit anything.

- **Event (`src/events.ts`):** the new `SubscriptionPaused` event carries `resumeOn` and `reason`, and it's part of the `SubscriptionEvent` union.
- **State (`src/subscription.ts`):**
  - There is a new `paused` status and a `resumeOn: string | null` field. It starts as `null`.
  - Pausing only changes an active subscription. In any other status, including one that is already paused, the event changes nothing.
  - `payment_failed` now also leaves a paused subscription alone. `payment_recovered` already ignored anything that wasn't past due.
  - Cancelling a paused subscription works as usual and sets `resumeOn` back to `null`.
- **Audit (`src/audit.ts`):** the line is `… subscription_paused resumeOn=2025-05-01 reason="vacation"`. The reason is JSON-quoted the same way as the cancellation reason.
- **Notifier (`src/notifier.ts`):** the customer gets a `subscription-paused` email with `resumeOn` in its data, and nobody else is notified.
- **Tests:** I added tests in all three test files. They cover pausing, the non-active no-ops, payment events on a paused subscription, cancelling while paused, the audit line and the notification.

I left out resuming, as you asked. `resumeOn` isn't validated as a `YYYY-MM-DD` date, matching how the other event fields are handled.