The `subscription_paused` event is in. `npm test` shows 19 passed and 0 failed, and `npm run typecheck` is clean.

- **Event** (`src/events.ts`): `SubscriptionPaused` carries `resumeOn` and `reason`.
- **State** (`src/subscription.ts`):
  - There is a new `paused` status and a `resumeOn: string | null` field, which starts as `null`.
  - Pausing only changes an active subscription; in any other status it does nothing.
  - `payment_failed` now leaves a paused subscription alone. `payment_recovered` already ignored anything that wasn't past due.
  - Cancelling sets `resumeOn` back to `null`.
- **Audit** (`src/audit.ts`): the line reads `… subscription_paused resumeOn=2025-05-01 reason="vacation"`. The reason is quoted with the same `JSON.stringify` as the cancellation reason.
- **Notifications** (`src/notifier.ts`): a single `subscription-paused` email to the customer, with `data: { resumeOn }`. Nobody else is notified.
- **Tests:** I added one for the audit line, one for the notification, and four for state. The state tests cover pausing, refusing to pause when past due or canceled, payment events being ignored while paused, and cancelling clearing `resumeOn`.

Resuming is not implemented, as you asked. Nothing validates the `resumeOn` format, since the other events don't validate their fields either.