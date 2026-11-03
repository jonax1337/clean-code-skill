Pausing is implemented, with tests. Typecheck passes and all 19 tests pass (the 4 new audit/notifier/state groups plus the existing ones).

**What changed**

- **`src/events.ts`**: new `subscription_paused` event with `resumeOn` (YYYY-MM-DD string) and `reason`.
- **`src/subscription.ts`**:
  - New `paused` status and a `resumeOn` field, which is `null` unless paused.
  - Pausing only works from `active`; any other status returns the state unchanged.
  - `payment_failed` now ignores paused subscriptions, as it already did for canceled ones.
  - Cancelling clears `resumeOn`.
- **`src/audit.ts`**: `... subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted like the cancellation reason.
- **`src/notifier.ts`**: a `subscription-paused` email to the customer only, with `data: { resumeOn }`.
- **Tests**: audit line format, the customer email, and state rules (active→paused, no-op from past_due/canceled/paused, payment events ignored while paused, cancel clears `resumeOn`).

**Choices to check**

- The email's data carries only `resumeOn`, as you specified. The reason goes into the audit log but not the email. Say if you want it in the email too.
- The notifier only sees the event, not the subscription state, so a pause sent for a subscription that can't be paused (e.g. canceled) still triggers the customer email. The existing `payment_failed` behaves the same way for canceled subscriptions. Fixing it would mean giving the notifier state, which I didn't do.
- Plan changes are not blocked while paused, since you didn't specify that.

Nothing is committed. Resuming is not implemented, as you asked.