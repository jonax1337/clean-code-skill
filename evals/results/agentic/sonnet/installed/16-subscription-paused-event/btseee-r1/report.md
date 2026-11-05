I added the `subscription_paused` event across state, audit log and notifications, with tests for each. All 19 tests pass and the typecheck is clean.

- **State:**
  - Pausing an active subscription sets its status to `paused` and stores `resumeOn`. In any other status, including an already-paused one, the event changes nothing.
  - `payment_failed` and `payment_recovered` leave a paused subscription as it is.
  - Cancelling a paused subscription works as usual and sets `resumeOn` back to `null`.
  - `resumeOn` is `null` on every other subscription.
- **Audit log:** pause entries look like `… subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way as the cancellation reason.
- **Notifications:** the customer gets a `subscription-paused` email with `resumeOn`. Nobody else is notified.

A `plan_changed` event still changes the plan on a paused subscription. You didn't say either way, so I left it alone.

I didn't add any resume handling, as you asked. I also exported the new `SubscriptionPaused` type from `src/index.ts`.