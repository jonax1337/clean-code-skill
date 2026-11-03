The `subscription_paused` event is in and handled in all three places. Typecheck is clean and all 20 tests pass, including the new ones.

- **Event (`src/events.ts`):** the new `SubscriptionPaused` type carries `resumeOn` and `reason`, and it's added to the `SubscriptionEvent` union.
- **State (`src/subscription.ts`):**
  - There is a new `paused` status and a `resumeOn: string | null` field, which starts as `null`.
  - A pause only takes effect on an `active` subscription. In any other status, including an already-paused one, it returns the state unchanged.
  - `payment_failed` now leaves a paused subscription alone. `payment_recovered` already ignored anything that isn't `past_due`, so it needed no change.
  - Cancelling a paused subscription works as usual and sets `resumeOn` back to `null`.
- **Audit (`src/audit.ts`):** the line reads `… subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way as the cancellation reason.
- **Notifications (`src/notifier.ts`):** the customer gets a `subscription-paused` email with `resumeOn` in its data, and nobody else is notified.

I added tests in the audit, notifier and subscription test files. The subscription tests cover:
- the initial `null` for `resumeOn`;
- pausing an active subscription;
- a pause being ignored when the subscription is `past_due`, canceled or already paused;
- payment events leaving a paused subscription unchanged;
- cancelling a paused subscription and clearing `resumeOn`.

I left out resuming, as you asked.

The task didn't say whether the `resumeOn` format should be validated, so it isn't: the value is stored and echoed exactly as given.