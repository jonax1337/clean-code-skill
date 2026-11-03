I added the `subscription_paused` event. Typecheck is clean and all 21 tests pass.

- **Event** (`src/events.ts`): `subscription_paused` carries `resumeOn` (`YYYY-MM-DD`) and `reason`.
- **State** (`src/subscription.ts`):
  - There is a new `paused` status and a `resumeOn` field, which is `null` unless the subscription is paused.
  - Only an `active` subscription can be paused. In any other status the event changes nothing, and that includes pausing an already paused subscription, which keeps its first `resumeOn`.
  - `payment_failed` now leaves a paused subscription alone. `payment_recovered` already did.
  - Cancelling a paused subscription works as usual and sets `resumeOn` back to `null`.
- **Audit log** (`src/audit.ts`): the line is `… subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way as the cancellation reason.
- **Notifications** (`src/notifier.ts`): the customer gets a `subscription-paused` email with `resumeOn` in its data. Nobody else is notified.
- **Tests**: I added one for the audit line and one for the notification. The subscription tests cover pausing, `resumeOn` being `null` when not paused, pausing from `past_due` and `canceled`, pausing twice, payment events while paused, and cancelling while paused.

Resuming is left out, as you asked. Nothing in the code moves a subscription out of `paused` except cancelling it.