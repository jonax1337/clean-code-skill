The `subscription_paused` event is in place across the event type, state, audit log and notifier, with tests. All 20 tests pass (13 existing, 7 new) and `tsc --noEmit` exits 0. I did not commit.

**What changed**

- **`src/events.ts`**: new `SubscriptionPaused` event with `resumeOn` and `reason`, added to the union.
- **`src/subscription.ts`**:
  - New `paused` status and a `resumeOn` field, `null` on every subscription except a paused one.
  - Pausing only applies from `active`; in any other status the event returns the state unchanged.
  - `payment_failed` now also ignores a paused subscription. `payment_recovered` already had no effect there.
  - Cancelling clears `resumeOn`.
- **`src/audit.ts`**: `resumeOn=2025-05-01 reason="vacation"`, using the same quoting as the cancellation reason.
- **`src/notifier.ts`**: one `subscription-paused` email to the customer, with `data: { resumeOn }`. No billing-team email.
- **Tests**: a pause audit line, a pause email, and state tests covering the valid pause, a pause from past-due, cancelled and already-paused states, payment events while paused, and cancelling a paused subscription.

**Decisions to check**

- `plan_changed` still applies to a paused subscription, since the spec didn't mention it. If a paused subscription shouldn't change plan, that is a one-line guard in the reducer.
- The email carries only `resumeOn`, not the reason, because the spec named only the date.
- `resumeOn` is typed as a plain `string`, the same as `occurredAt`. Nothing validates the `YYYY-MM-DD` format.