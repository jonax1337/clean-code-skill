`subscription_paused` is in place across state, audit log, and notifications, with tests. All 21 tests pass (8 new) and `tsc --noEmit` is clean. I didn't commit anything.

**What changed**

- **`src/events.ts`**: new `SubscriptionPaused` event with `resumeOn` (`YYYY-MM-DD`) and `reason`.
- **`src/subscription.ts`**:
  - New `paused` status and a `resumeOn` field, which is `null` unless the subscription is paused.
  - Pause only moves an `active` subscription. Any other status is returned unchanged.
  - `payment_failed` now leaves a paused subscription alone, the same way it already ignores canceled ones.
  - Cancelling clears `resumeOn`.
- **`src/audit.ts`**: `2025-04-02T08:30:00Z sub_9 subscription_paused resumeOn=2025-05-01 reason="vacation"`, matching your example.
- **`src/notifier.ts`**: a customer-only `subscription-paused` email with `data: { resumeOn }`. The reason isn't in the email payload, since you only asked for the date.
- **Tests**: cover pausing an active subscription, the no-op cases (past due, canceled, already paused), payments during a pause, cancelling a paused subscription, plus the audit line and the notification.

**Decisions to check**

- A second pause on an already-paused subscription keeps the original `resumeOn`. I read "any other status changes nothing" literally.
- The notifier is stateless (it only sees the event), so a pause event sends the email even when the reducer ignores it, such as pausing a past-due subscription. This matches how `payment_failed` already behaves on canceled subscriptions. Tell me if the email should only go out for real pauses; that would need the notifier to see state.
- `resumeOn` is typed as a plain `string`, the same way `occurredAt` is. The `YYYY-MM-DD` format is documented, not enforced.

`npm install` also created an untracked `package-lock.json`, which I left alone.