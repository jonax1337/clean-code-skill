The `subscription_paused` event is in, and all 19 tests and the typecheck pass. I wrote the tests in the same step as the code rather than watching them fail first. I haven't committed anything.

- **State** (`src/subscription.ts`):
  - There is a new `paused` status and a `resumeOn` field that is `null` unless the subscription is paused.
  - Pausing only changes an active subscription; in any other status the event changes nothing.
  - A failed payment now also leaves a paused subscription untouched (before, it would have flipped it to past due). A payment recovery already left it alone.
  - Cancelling a paused subscription works as before and clears `resumeOn`.
- **Audit log** (`src/audit.ts`): this gives lines like `… sub_9 subscription_paused resumeOn=2025-05-01 reason="vacation"`.
- **Notifications** (`src/notifier.ts`): the customer gets a `subscription-paused` email carrying `resumeOn`, and nobody else is notified.
- **Event type** (`src/events.ts`): `SubscriptionPaused` is a new event type, and I also exported it from `src/index.ts`.
- **Tests**: the new tests are in the audit, notifier and subscription test files. They cover the audit line, the notification, pausing an active subscription, pausing in other statuses, payment events while paused, and cancelling a paused subscription.

Resuming is left out, as you asked.

I didn't run the crapper, dryer or mutator tools from the skill, and I didn't commit or push.