I've added the `subscription_paused` event, and all 20 tests pass (`npm test`, 10 of them new). `npm run typecheck` also runs with no errors. Nothing is committed yet.

**How it behaves:**
- **Event** (`src/events.ts`): the new event carries `resumeOn` (`YYYY-MM-DD`) and `reason`.
- **State** (`src/subscription.ts`):
  - There's a new `paused` status, and the subscription now has a `resumeOn` field. It starts as `null` and is set only when an active subscription is paused.
  - Pausing a past-due, canceled or already-paused subscription changes nothing.
  - `payment_failed` now leaves a paused subscription alone; before, it only skipped canceled ones. `payment_recovered` already only acted on past-due subscriptions, so it needed no change.
  - Cancelling a paused subscription works as usual and sets `resumeOn` back to `null`.
- **Audit log** (`src/audit.ts`): lines look like `… subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way as the cancellation reason.
- **Notifications** (`src/notifier.ts`): only the customer gets an email, using the `subscription-paused` template with `data: { resumeOn }`.

**Tests:**
- The audit test checks your example line exactly.
- The notification test checks that the customer email is the only one sent.
- The state tests cover pausing, `resumeOn` being `null` when not paused, pause being ignored for past-due, canceled and already-paused subscriptions, both payment events leaving a paused subscription unchanged, and cancelling while paused.

**One thing to decide:** you didn't say what a `plan_changed` should do while a subscription is paused. Right now it switches the plan as it would for any other status, and I left it that way.

Resuming isn't included, as you asked.