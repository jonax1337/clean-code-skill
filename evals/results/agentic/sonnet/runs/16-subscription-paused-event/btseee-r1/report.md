I added the `subscription_paused` event, with tests. All 19 tests pass and `tsc --noEmit` reports no errors.

- **Event** (`src/events.ts`): `SubscriptionPaused` carries `resumeOn` and `reason`.
- **State** (`src/subscription.ts`):
  - Pausing an active subscription sets the status to `paused` and stores `resumeOn`.
  - In any other status the event changes nothing.
  - `resumeOn` is `null` for every other state.
  - Cancelling a paused subscription works as before and also clears `resumeOn`.
  - `payment_failed` now leaves a paused subscription alone.
  - `payment_recovered` already ignored anything that wasn't past due, so it needed no change.
- **Audit** (`src/audit.ts`): the line reads `… subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way as the cancellation reason.
- **Notifier** (`src/notifier.ts`): the customer gets a `subscription-paused` email with `resumeOn` in its data. Nobody else is notified.
- **Tests**:
  - Audit and notifier each get a test for the new event.
  - The subscription tests cover pausing an active subscription.
  - They also cover a pause ignored when past due, already paused or canceled, payment events ignored while paused, and cancelling a paused subscription.

I did not validate that `resumeOn` is a real `YYYY-MM-DD` date, and I did not implement resuming. I didn't commit anything.