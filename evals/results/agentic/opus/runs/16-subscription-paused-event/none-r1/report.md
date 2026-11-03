I added the `subscription_paused` event and its tests. All 19 tests pass and the typecheck is clean.

**What changed**
- **`src/events.ts`**: a new `SubscriptionPaused` event with `resumeOn` and `reason`, added to the `SubscriptionEvent` union.
- **`src/subscription.ts`**:
  - There's a new `paused` status, and the subscription now has a `resumeOn` field that is `null` unless it's paused.
  - Pausing only works on an active subscription; in any other status the event changes nothing, including when it's already paused.
  - `payment_failed` now leaves a paused subscription as it is. `payment_recovered` already did, because it only acts on `past_due`.
  - Cancelling sets `resumeOn` back to `null`.
- **`src/audit.ts`**: writes `resumeOn=<date> reason="<quoted>"`, quoting the reason the same way cancellations do.
- **`src/notifier.ts`**: sends only the customer a `subscription-paused` email with `{ resumeOn }`.

**Tests**
- **Audit:** the example line from your request comes out exactly as written.
- **Notifications:** the customer gets the one email and nobody else is notified.
- **State:**
  - Pausing an active subscription works and stores `resumeOn`.
  - Pausing does nothing when the subscription is past due, cancelled or already paused.
  - Payment events leave a paused subscription unchanged.
  - Cancelling a paused subscription clears `resumeOn`.

**Open question:** you didn't say whether a plan change should apply while a subscription is paused. Right now it does: the plan switches and it stays paused. Let me know if you'd rather block that.

I haven't committed anything.