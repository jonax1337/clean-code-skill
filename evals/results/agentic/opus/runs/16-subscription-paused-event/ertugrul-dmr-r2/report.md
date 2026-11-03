I added the `subscription_paused` event and its tests. All 19 tests pass and `npm run typecheck` is clean.

- **Event** (`src/events.ts`): a new `SubscriptionPaused` type with `resumeOn` (`YYYY-MM-DD`) and `reason`, added to the `SubscriptionEvent` union.
- **State** (`src/subscription.ts`):
  - There's a new `paused` status, and the subscription now has a `resumeOn` field that starts as `null`.
  - Pausing only does something when the subscription is active; in any other status, including already paused, it changes nothing.
  - A failed payment now leaves a paused subscription unchanged.
  - A recovered payment already only acted on past-due subscriptions, so it didn't need a change.
  - Cancelling now also sets `resumeOn` back to `null`.
- **Audit log** (`src/audit.ts`): a pause line reads `resumeOn=<date> reason="<reason>"`, with the reason quoted the same way as for cancellations.
- **Notifications** (`src/notifier.ts`): only the customer gets an email, using the `subscription-paused` template with `{ resumeOn }`.
- **Tests**:
  - The audit line from your example.
  - The pause notification.
  - Pausing an active subscription.
  - Pausing has no effect when the subscription is past due, cancelled or already paused.
  - Both payment events leave a paused subscription alone.
  - Cancelling a paused subscription clears the resume date.
  - The existing "started" test now also checks that `resumeOn` is `null`.

Nothing checks that `resumeOn` is a valid date; it's typed as a plain string, just like the timestamp field `occurredAt`. A plan change while paused still switches the plan, since you didn't mention it.

I haven't committed anything.