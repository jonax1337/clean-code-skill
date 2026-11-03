I've added the `subscription_paused` event and handled it in all three places that consume events, with tests for each.

**Changes**
- **`src/events.ts`**: a new `SubscriptionPaused` event with `resumeOn` (`YYYY-MM-DD`) and `reason`, added to the end of the event list.
- **`src/subscription.ts`**:
  - Subscriptions have a new `"paused"` status and a new `resumeOn: string | null` field, which starts as `null`.
  - Pausing only works on an active subscription. In any other status, including already paused, the event changes nothing.
  - `payment_failed` now leaves a paused subscription as it is. `payment_recovered` already did, because it only acts on `past_due`.
  - Cancelling a paused subscription works as before and now also sets `resumeOn` back to `null`.
- **`src/audit.ts`**: the log line is `resumeOn=<date> reason=<quoted>`, quoted the same way as the cancellation reason. For example: `2025-04-02T08:30:00Z sub_9 subscription_paused resumeOn=2025-05-01 reason="vacation"`.
- **`src/notifier.ts`**: only the customer is notified, with a `subscription-paused` email that carries `{ resumeOn }`.

**Tests:** I wrote 7 new tests before the code, and they failed against the old code. They cover:
- `resumeOn` being `null` when the subscription isn't paused
- pausing an active subscription
- pause having no effect when the subscription is past due, cancelled or already paused
- both payment events leaving a paused subscription alone
- cancelling a paused subscription
- the audit line, including a reason with quotes in it
- the notification

**Results:** `npm test` gives 20 tests, 20 passed, 0 failed. `tsc --noEmit` exits 0.

**Two things to know:**
- `Subscription` now has a required field, so any code outside this repo that builds `Subscription` objects by hand will need `resumeOn` added. Inside the repo only `startedSubscription` builds one.
- The `src` files use LF line endings, but `test/subscription.test.ts` uses CRLF, and I kept each file's existing style.

As you asked, I left resuming out: nothing reads `resumeOn` to bring a subscription back to active. I haven't committed anything.