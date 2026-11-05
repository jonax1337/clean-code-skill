I added the `subscription_paused` event to state, the audit log and notifications. I ran `npm test` (19 tests, all passing) and `npm run typecheck`, which printed no errors. I didn't commit anything.

- **State** (`src/subscription.ts`):
  - There is a new `paused` status and a `resumeOn` field, which is `null` unless the subscription is paused.
  - Pausing only changes an `active` subscription. In any other status, including one that is already paused, the event leaves the state alone.
  - `payment_failed` now also leaves a paused subscription untouched. `payment_recovered` already did, because it only acts on `past_due`.
  - Cancelling a paused subscription cancels it as usual and sets `resumeOn` back to `null`.
- **Audit log** (`src/audit.ts`): the line looks like `… sub_9 subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way as the cancellation reason.
- **Notifications** (`src/notifier.ts`): the customer gets a `subscription-paused` email with `resumeOn` in its data, and nobody else is notified.
- **Event type and exports**: `SubscriptionPaused` is defined in `src/events.ts` and exported from `src/index.ts`.
- **Tests**: I added four state tests (pause records the date, pause is ignored outside `active`, payment events leave a paused subscription alone, cancel clears `resumeOn`). I also added one audit test and one notifier test.

Resuming is not included, as you asked. Because there is no resume event yet, a paused subscription can only end by being cancelled.