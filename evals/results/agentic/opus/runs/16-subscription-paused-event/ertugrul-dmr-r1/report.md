I've added the `subscription_paused` event to state, the audit log and notifications. All 19 tests pass and `npm run typecheck` reports no errors. I haven't committed anything.

**What changed**
- **`src/events.ts`**: a new `SubscriptionPaused` event carrying `resumeOn` (`YYYY-MM-DD`) and `reason`, added to the `SubscriptionEvent` union.
- **`src/subscription.ts`**:
  - Added the `paused` status and a `resumeOn: string | null` field, which starts as `null`.
  - Pausing only does something when the subscription is `active`; in any other status the event changes nothing.
  - A failed payment now leaves a paused subscription as it is. A recovered payment already only affected `past_due` subscriptions, so it needed no change.
  - Cancelling now also sets `resumeOn` back to `null`.
- **`src/audit.ts`**: writes `resumeOn=<date> reason=<quoted>`, quoting the reason the same way as cancellations, so your example line comes out exactly as written.
- **`src/notifier.ts`**: sends one `subscription-paused` email to the customer with `{ resumeOn }`, and nothing to the billing team.

**Tests added**
- **Audit:** the pause line, including a reason that contains quotes.
- **Notifications:** only the customer gets the email, and it carries the resume date.
- **State:**
  - Pausing an active subscription stores the resume date, and a new subscription starts with `resumeOn` as `null`.
  - Pausing does nothing to a past-due, cancelled or already-paused subscription.
  - Failed and recovered payments leave a paused subscription unchanged.
  - Cancelling a paused subscription clears the resume date.

**Decision for you:** you didn't say what a plan change should do while a subscription is paused. Right now it still switches the plan, as it does in every other status. If paused subscriptions should keep their plan, that's a one-line guard.