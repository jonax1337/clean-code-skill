`subscription_paused` is in place across the event type, state, audit log, and notifications. All 20 tests pass (13 existing, 7 new), and `tsc --noEmit` is clean. I haven't committed anything.

**Changes**
- **Event** (`src/events.ts`): `SubscriptionPaused` with `resumeOn` and `reason`.
- **State** (`src/subscription.ts`):
  - `paused` is a new status, and `resumeOn` is a new field, `null` unless paused.
  - Pause only applies to an `active` subscription; any other status is returned unchanged.
  - `payment_failed` is ignored while paused. `payment_recovered` already only acts on `past_due`, so it leaves paused alone.
  - Cancelling clears `resumeOn`.
- **Audit** (`src/audit.ts`): `resumeOn=2025-05-01 reason="vacation"`, matching your example.
- **Notifications** (`src/notifier.ts`): one `subscription-paused` email to the customer with `data: { resumeOn }`. Nobody else is notified.
- **Tests**: covers pausing from active, rejection from past_due and canceled, a second pause not moving the date, payment events while paused, cancelling a paused subscription, and the audit line and email for a pause.

**Decisions to check**
- The email carries only `resumeOn`, not the reason, because that's what the spec asked for. Adding the reason to the email is a one-line change.
- The notifier only sees the event, not the subscription state, so pausing an already-canceled subscription still sends the email. This matches how `payment_failed` already behaves on canceled subscriptions. Fixing it would mean giving the notifier state, which is a bigger change.
- `resumeOn` is typed as a plain `string` with a `YYYY-MM-DD` doc comment. Nothing validates the format yet.