Pausing is implemented in `src/` and covered by tests. All 20 tests pass (13 existing, 7 new) and `npm run typecheck` is clean. I did not commit.

**What changed**

- **`src/events.ts`**: new `SubscriptionPaused` event with `resumeOn` and `reason`.
- **`src/subscription.ts`**:
  - New `paused` status and a `resumeOn` field, which is `null` on start and cleared on cancel.
  - Pausing only works from `active`; from any other status the event is a no-op.
  - `payment_failed` is a no-op while paused. `payment_recovered` already did nothing unless past due, so it needed no change.
- **`src/audit.ts`**: `resumeOn=2025-05-01 reason="vacation"`, using the same `JSON.stringify` quoting as cancellation.
- **`src/notifier.ts`**: one `subscription-paused` email to the customer, with `data: { resumeOn }`. No billing-team notification.
- **Tests**: pause state, the active-only rule, payment events leaving a paused subscription unchanged, cancel-while-paused clearing `resumeOn`, the audit line from your example, and the email.

**Choices I made that you may want to change**

- The email carries only `resumeOn`, as the spec said. The reason is in the audit log but not the email. Adding it is a one-line change.
- `plan_changed` still applies while paused, since the spec didn't mention it. Say if plan changes should be blocked during a pause.
- `resumeOn` is typed as a plain string and is not validated as `YYYY-MM-DD`, matching how the other fields are handled.