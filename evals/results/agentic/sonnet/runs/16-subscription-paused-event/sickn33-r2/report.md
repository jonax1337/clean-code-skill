I added the `subscription_paused` event. Typecheck is clean and all 19 tests pass, including 6 new ones.

- **State** (`src/subscription.ts`): there is a new `paused` status and a `resumeOn: string | null` field.
  - An active subscription becomes `paused` and stores `resumeOn`. In any other status the pause changes nothing, so pausing an already paused subscription keeps the original date.
  - Payment events leave a paused subscription as it is. I changed `payment_failed` for this. `payment_recovered` already ignored anything that wasn't past due.
  - Cancelling a paused subscription works as usual and sets `resumeOn` back to `null`.
- **Audit log** (`src/audit.ts`): the line looks like `… sub_9 subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way as the cancellation reason.
- **Notifications** (`src/notifier.ts`): the customer gets a `subscription-paused` email with `resumeOn`, and nobody else is notified.
- **Tests**: new tests in the three existing test files cover the audit line, the email, pausing from an active subscription, being ignored in other statuses, payment events while paused, and cancelling a paused subscription.

Resuming is left out, as you asked. Until it exists, nothing moves a subscription out of `paused` except cancellation.

I didn't validate that `resumeOn` is a real `YYYY-MM-DD` date. The existing events don't validate their fields either, so I kept to that.