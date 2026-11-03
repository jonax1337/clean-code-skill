`subscription_paused` is in place across the event type, the reducer, the audit log and the notifier. Tests pass (19, up from 13), and the typecheck is clean. I haven't committed anything.

**What changed**

- **`src/events.ts`**: new `SubscriptionPaused` event carrying `resumeOn` and `reason`, added to the union.
- **`src/subscription.ts`**:
  - New `paused` status and a `resumeOn` field on `Subscription`, set to `null` on start and on cancel.
  - Pausing only applies when the subscription is `active`; in any other status the state is returned unchanged.
  - `payment_failed` is ignored while paused. `payment_recovered` already did nothing unless `past_due`, so it needed no change.
  - Cancelling a paused subscription works as before and clears `resumeOn`.
- **`src/audit.ts`**: produces `… subscription_paused resumeOn=2025-05-01 reason="vacation"`.
- **`src/notifier.ts`**: one `subscription-paused` email to the customer with `data: { resumeOn }`. Nobody else is notified.
- **Tests**: new cases for the pause transition, payment events being ignored while paused, pausing from other statuses being a no-op, cancel clearing `resumeOn`, the audit line, and the notification.

**Choices I made where the spec was silent**

- **Plan changes while paused still apply.** The spec didn't mention them, so I left them alone. Say if they should be blocked.
- **The `reason` is not in the email.** The spec only asked for `resumeOn` there. Adding it is a one-line change.
- **`resumeOn` is a plain string with no format check.** The `YYYY-MM-DD` shape is documented but not enforced at runtime. Validation could go in the event producer or in the reducer.

I also removed the `package-lock.json` that `npm install` created, since the repo doesn't track one.