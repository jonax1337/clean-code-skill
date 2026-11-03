The `subscription_paused` event now works end to end. `npm test` passes (20 tests, 0 failures) and `npm run typecheck` reports no errors.

- **State:**
  - `src/subscription.ts` has a new `paused` status and a `resumeOn: string | null` field, which is `null` until a pause.
  - Only an `active` subscription is paused; in any other status the event changes nothing.
  - `payment_failed` now also leaves a paused subscription unchanged. `payment_recovered` already did, because it only acts on `past_due`.
  - Cancelling a paused subscription works as before and also sets `resumeOn` back to `null`.
- **Audit log:** `src/audit.ts` writes `resumeOn=… reason="…"`, with the reason quoted the same way as for cancellation. Your example line is one of the new tests.
- **Notifications:** `src/notifier.ts` sends the customer a `subscription-paused` email with `resumeOn` in its data, and nobody else.
- **Event type:** the event itself is defined in `src/events.ts`.
- **Tests:** I added tests in all three test files. They cover:
  - pausing an active subscription;
  - ignoring a pause from `past_due`, `canceled` or already-`paused`;
  - payment events on a paused subscription;
  - cancelling from `paused`;
  - the audit line;
  - the email.

Resuming is not implemented, as you asked. A paused subscription has no way back to `active` yet.

I didn't check that `resumeOn` is a valid `YYYY-MM-DD` date. The event just carries whatever string it is given, as `occurredAt` does today.