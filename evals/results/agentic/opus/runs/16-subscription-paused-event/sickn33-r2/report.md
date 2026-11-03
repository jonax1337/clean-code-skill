The `subscription_paused` event is in. All 20 tests pass and the typecheck is clean.

**What changed**
- **`src/events.ts`**: a new `SubscriptionPaused` event with `resumeOn` and `reason`, added to the `SubscriptionEvent` union.
- **`src/subscription.ts`**:
  - Subscriptions have a new status, `paused`, and a new field `resumeOn`, which is `null` from the start.
  - A pause only does something when the subscription is active. In any other status, including already paused, the event changes nothing.
  - A failed payment no longer moves a paused subscription to `past_due`. A recovered payment already only acted on `past_due`, so it needed no change.
  - Cancelling now always sets `resumeOn` back to `null`.
- **`src/audit.ts`**: the log line reads `resumeOn=<date> reason="<quoted>"`, quoting the reason the same way as cancellations.
- **`src/notifier.ts`**: the customer gets a `subscription-paused` email with `{ resumeOn }`, and nobody else is notified.

**Tests:** 7 new ones (I wrote them first and watched them fail):
- the audit line, using your exact example
- the customer-only email
- `resumeOn` starting as `null`
- pausing an active subscription
- a pause being ignored when the subscription is past due, cancelled or already paused
- both payment events leaving a paused subscription alone
- cancelling a paused subscription, which also clears `resumeOn`

**Two things to be aware of**
- Your spec didn't cover plan changes, so a `plan_changed` event still changes the plan while a subscription is paused, as it does in every other status.
- `resumeOn` is typed as a plain string. Nothing checks that it really is `YYYY-MM-DD`, the same way the timestamps aren't checked today.

Resuming is not included, and nothing is committed.