I added the `subscription_paused` event. Typecheck is clean and all 19 tests pass, including the new ones. I haven't committed anything.

- **Event:** `src/events.ts` has the new `SubscriptionPaused` type with `resumeOn` and `reason`. It's added to the `SubscriptionEvent` union.
- **State:** `src/subscription.ts` has a new `paused` status and a `resumeOn: string | null` field. It starts as `null`.
  - Pausing an active subscription sets the status to `paused` and stores `resumeOn`. In any other status, including one that's already paused, the event changes nothing.
  - `payment_failed` leaves a paused subscription as it is. `payment_recovered` already did that, because it only acts on `past_due`.
  - Cancelling a paused subscription works as before and also sets `resumeOn` back to `null`.
- **Audit log:** `src/audit.ts` writes `... subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way as the cancellation reason.
- **Notifications:** `src/notifier.ts` sends only the customer a `subscription-paused` email, with `resumeOn` as its data.
- **Tests:** I added cases to the audit, notifier and subscription test files. They cover the audit line, the notification, pausing and the `resumeOn` value, the no-op cases, payment events on a paused subscription, and cancelling while paused.

Resuming is left out, as you asked.

I didn't validate the `YYYY-MM-DD` format of `resumeOn`, because the other events don't validate their fields either.