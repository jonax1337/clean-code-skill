I added the `subscription_paused` event. All 20 tests pass (7 of them new) and `npm run typecheck` shows no errors.

- **State** (`src/subscription.ts`): there's a new `paused` status, and the subscription has a new `resumeOn` field that is `null` whenever it isn't paused. Pausing only works on an active subscription; in any other status, including already paused, the event changes nothing. A failed payment now leaves a paused subscription alone. A recovered payment already did, because it only acts on past-due subscriptions. Cancelling a paused subscription works as usual and also clears `resumeOn`.
- **Event** (`src/events.ts`): the event carries `resumeOn` and `reason`.
- **Audit log** (`src/audit.ts`): the line shows `resumeOn=… reason="…"`, with the reason quoted the same way as the cancellation reason. Your example line is one of the tests.
- **Notifications** (`src/notifier.ts`): only the customer gets an email, the `subscription-paused` template with `{ resumeOn }`.
- **Tests**: the new ones cover pausing, pausing in each non-active status, payment events while paused, cancelling while paused, and the audit and notification output.

Two things I left as they are, since you didn't specify them:
- **Plan changes still apply while paused.** That seemed harmless since nothing is billed, but I can block them if you want.
- **The `resumeOn` format isn't checked.** It's typed as a plain string, and none of the existing fields are validated either. A date in the past or a badly formatted one would be accepted.