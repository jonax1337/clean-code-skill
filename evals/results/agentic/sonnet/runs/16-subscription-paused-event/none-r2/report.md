The `subscription_paused` event now works as you described. Tests (19) and the typecheck both pass. I haven't committed anything.

- **Event** (`src/events.ts`): `SubscriptionPaused` carries `resumeOn` and `reason`.
- **State** (`src/subscription.ts`):
  - There is a new `paused` status and a `resumeOn: string | null` field. It starts as `null`.
  - Pausing only takes effect on an `active` subscription. In any other status the event changes nothing.
  - `payment_failed` now leaves a paused subscription alone. `payment_recovered` already ignored anything that wasn't `past_due`.
  - Cancelling a paused subscription works as usual and sets `resumeOn` back to `null`.
- **Audit** (`src/audit.ts`): the line looks like `… subscription_paused resumeOn=2025-05-01 reason="vacation"`.
- **Notifications** (`src/notifier.ts`): only the customer is notified, with a `subscription-paused` email that carries `resumeOn`.
- **Tests**: I added cases to the three existing test files. They cover:
  - pausing an active subscription;
  - ignoring a pause in the `past_due` and `canceled` states;
  - payment events leaving a paused subscription as it is;
  - cancelling a paused subscription;
  - the exact audit line;
  - the notification.

Resuming is not included, as you asked. Until it exists, a paused subscription can only leave that state by being cancelled.