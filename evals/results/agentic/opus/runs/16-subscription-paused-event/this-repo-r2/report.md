I added the `subscription_paused` event, and all three consumers handle it as you described.

- **Event** (`src/events.ts`): a new `SubscriptionPaused` type with `resumeOn` and `reason`, added to the end of the `SubscriptionEvent` union.
- **State** (`src/subscription.ts`):
  - `SubscriptionStatus` now includes `"paused"`, and `Subscription` has a new `resumeOn: string | null` field, which is `null` when a subscription starts.
  - Pausing only works on an active subscription. A past-due, canceled or already-paused subscription is returned unchanged.
  - `payment_failed` now leaves a paused subscription alone, the same way it already left canceled ones. `payment_recovered` already did nothing unless the subscription was past due, so it needed no change.
  - Cancelling sets `resumeOn` back to `null`.
- **Audit** (`src/audit.ts`): the line reads `resumeOn=<date> reason=<quoted>`, quoting the reason with `JSON.stringify` just like the cancellation line.
- **Notifications** (`src/notifier.ts`): the customer gets one `subscription-paused` email with `{ resumeOn }`, and nobody else is notified.

**Tests:** I added 6 tests:
- the audit line, using your `sub_9` example exactly;
- the notification;
- four state tests: pausing an active subscription; past-due, canceled or already-paused subscriptions are unchanged; payment events don't change a paused subscription; cancelling a paused one works and clears the date.

I also added a check to the existing "started" test that `resumeOn` begins as `null`. `npm test` passes (19 of 19) and `npm run typecheck` finishes with no errors.

**Two things your spec doesn't cover, which I left as they are:**
- A `plan_changed` on a paused subscription still switches the plan. That's the same as it works today for every other status.
- `resumeOn` isn't checked against the `YYYY-MM-DD` format. Nothing else in the code validates event fields either.

Resuming is not included. I haven't committed anything.