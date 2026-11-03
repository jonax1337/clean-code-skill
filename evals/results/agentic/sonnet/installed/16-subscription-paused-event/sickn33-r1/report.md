The `subscription_paused` event is in. Typecheck is clean and all 19 tests pass, including the new ones for each of the three consumers.

- **Event (`src/events.ts`):** the new `SubscriptionPaused` type carries `resumeOn` and `reason`, and it's part of the `SubscriptionEvent` union.
- **State (`src/subscription.ts`):**
  - Added a `paused` status and a `resumeOn: string | null` field, which starts as `null`.
  - Pausing an active subscription sets `paused` and stores `resumeOn`. In any other status, including one that's already paused, the event changes nothing.
  - `payment_failed` now leaves a paused subscription alone. `payment_recovered` already ignored anything that wasn't past due.
  - Cancelling a paused subscription works as before and sets `resumeOn` back to `null`.
- **Audit log (`src/audit.ts`):** the line reads `… subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way as the cancellation reason.
- **Notifications (`src/notifier.ts`):** the customer gets a `subscription-paused` email with `resumeOn` in its data, and nobody else is notified.

I didn't add any resume handling.

Two things I left alone because you didn't specify them. `plan_changed` still applies to a paused subscription. `resumeOn` isn't validated as a date, so the event takes whatever string it's given.