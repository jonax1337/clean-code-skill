The `subscription_paused` event is in. Typecheck is clean and all 22 tests pass, including 8 new ones for pausing. I haven't committed anything.

- **Event** (`src/events.ts`): `SubscriptionPaused` carries `resumeOn` and `reason`.
- **State** (`src/subscription.ts`):
  - There is a new `paused` status and a `resumeOn: string | null` field, which is `null` unless the subscription is paused.
  - Only an `active` subscription can be paused; in any other status the event changes nothing.
  - A failed payment leaves a paused subscription as it is. A recovered payment already did nothing unless the subscription was past due.
  - Cancelling a paused subscription works as usual and sets `resumeOn` back to `null`.
- **Audit log** (`src/audit.ts`): the line is `… subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way as the cancellation reason.
- **Notifications** (`src/notifier.ts`): the customer gets a `subscription-paused` email with `resumeOn`, and nobody else is notified.

The notifier doesn't look at subscription state, so the email goes out for every pause event, even one the state ignores (for example on a canceled subscription). The state check lives in the reducer, so if you want the email suppressed in those cases, the caller has to do it.

I didn't add resuming, as you asked.