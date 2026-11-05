`subscription_paused` is implemented across the event type, state, audit log, and notifier, with tests. All 20 tests pass (13 existing, 7 new) and `tsc --noEmit` is clean. I haven't committed anything.

**What changed**
- `src/events.ts`: new `SubscriptionPaused` event with `resumeOn` and `reason`.
- `src/subscription.ts`: `paused` status and a `resumeOn` field, which is `null` unless paused.
  - Pause applies only when the status is `active`; otherwise the state is returned unchanged.
  - `payment_failed` now also ignores paused subscriptions. `payment_recovered` already did, since it only applies to `past_due`.
  - Cancelling clears `resumeOn`.
- `src/audit.ts`: `resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way cancellation does it.
- `src/notifier.ts`: a customer-only `subscription-paused` email with `data: { resumeOn }`.
- Tests added in `test/subscription.test.ts`, `test/audit.test.ts`, and `test/notifier.test.ts`. They cover the active-only rule, payments not changing a paused subscription, cancelling a paused subscription, the audit line, and the email.

**Choices I made that you may want to change**
- The email carries only `resumeOn`, not the reason, since you specified only the date.
- `resumeOn` is not validated as `YYYY-MM-DD`, matching how the other events handle their fields.

**Gap to decide on**
The notifier only sees the event, not the subscription state, so a pause on a `past_due` subscription changes nothing in state but still sends the customer the email. Cancellation has the same behaviour today. Fixing this means the notifier needs the current state, which is a larger change. I left it alone.