The `subscription_paused` event now works in all three places: subscription state, audit log and notifications. I added tests for each. All 19 tests pass and the typecheck is clean. I did not build resuming.

- **Event** (`src/events.ts`): new `SubscriptionPaused` event with `resumeOn` and `reason`.
- **State** (`src/subscription.ts`):
  - There is a new `paused` status and a `resumeOn: string | null` field. It starts as `null`, and cancelling resets it to `null`.
  - Pausing only changes an active subscription. In any other status, including one that is already paused, the event changes nothing.
  - `payment_failed` now also leaves a paused subscription untouched. `payment_recovered` already did, because it only acts on `past_due`.
- **Audit log** (`src/audit.ts`): the line looks like `… subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way as the cancellation reason.
- **Notifications** (`src/notifier.ts`): the customer gets a `subscription-paused` email with `resumeOn` in its data. Nobody else is notified.

Because `Subscription` gained a field, any code outside this repo that builds a `Subscription` by hand will need to set `resumeOn`.