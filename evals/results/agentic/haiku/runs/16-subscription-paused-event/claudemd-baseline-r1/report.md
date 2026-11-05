`subscription_paused` is implemented across the state reducer, the audit log, and the notifier. All 20 tests pass (13 existing, 7 new) and `tsc --noEmit` is clean. The changes are uncommitted.

What changed:

- **`src/events.ts`**: new `SubscriptionPaused` event with `resumeOn` and `reason`.
- **`src/subscription.ts`**:
  - New `paused` status and a `resumeOn` field on `Subscription`, which is `null` unless paused.
  - A pause applies only to an active subscription; in any other status it changes nothing.
  - `payment_failed` leaves a paused subscription unchanged, and `payment_recovered` already did.
  - Cancelling a paused subscription sets `canceled` and clears `resumeOn`.
- **`src/audit.ts`**: `... subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted like the cancellation reason.
- **`src/notifier.ts`**: one customer-only `subscription-paused` email with `{ resumeOn }`.
- **Tests**: new cases in the audit, notifier, and subscription test files. They cover the pause itself, the non-active cases, payment events during a pause, cancelling a paused subscription, and the `null` default.

Choices I made that you may want to change:

- The `subscription-paused` email carries only `resumeOn`, not `reason`, because the spec named only the resume date for the email.
- `resumeOn` is stored as given. The reducer does not validate that it is a `YYYY-MM-DD` date. Validation would have to happen where the event is created.
- A `past_due` subscription cannot be paused, since the spec limits pausing to active subscriptions.