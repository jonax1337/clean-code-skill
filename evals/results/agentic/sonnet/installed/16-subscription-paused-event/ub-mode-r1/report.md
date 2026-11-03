I added the `subscription_paused` event. Typecheck is clean and all 19 tests pass, including the new ones. I haven't committed anything.

- **State** (`src/subscription.ts`): there is a new `paused` status and a `resumeOn: string | null` field on `Subscription`. It starts as `null`.
  - Only an `active` subscription becomes paused and stores `resumeOn`. In any other status the event changes nothing.
  - `payment_failed` now leaves a paused subscription alone, as it already did for a canceled one. `payment_recovered` already ignored anything that wasn't past due.
  - Cancelling a paused subscription works as before and also sets `resumeOn` back to `null`.
- **Audit log** (`src/audit.ts`): the line looks like `… sub_9 subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way as for cancellations.
- **Notifications** (`src/notifier.ts`): the customer gets a `subscription-paused` email with `resumeOn` in its data, and nobody else is notified.
- **Event type** (`src/events.ts`): `SubscriptionPaused` is added to the `SubscriptionEvent` union.
- **Tests**: new cases in the audit, notifier and subscription test files.
  - The audit and notifier tests cover the exact line and the email.
  - The state tests cover pausing an active subscription, ignoring the event in other statuses (past due, canceled, already paused), payment events leaving a paused subscription alone, and cancelling a paused subscription.

I left resuming out, as you asked.

I didn't validate `resumeOn` as a real `YYYY-MM-DD` date. Like the other event fields, it's taken as given.