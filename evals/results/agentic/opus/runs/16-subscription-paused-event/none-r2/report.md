I added the `subscription_paused` event and handled it in all three places that consume events. All 21 tests pass (the 13 that were already there plus 8 new ones), and `npm run typecheck` is clean.

**What changed**
- **`src/events.ts`**: new `SubscriptionPaused` event with `resumeOn` and `reason`, added to the `SubscriptionEvent` union.
- **`src/subscription.ts`**:
  - There's a new `paused` status, and the subscription has a new `resumeOn: string | null` field, set to `null` when it starts.
  - Pausing only works on an active subscription. If it's past due, already paused or canceled, the event changes nothing; pausing again doesn't move the resume date either.
  - `payment_failed` now leaves a paused subscription as it is. `payment_recovered` already only acted on past-due subscriptions, so it needed no change.
  - Cancelling a paused subscription works as before and also sets `resumeOn` back to `null`.
- **`src/audit.ts`**: logs `resumeOn=<date> reason="<reason>"`, quoting the reason the same way as the cancellation reason.
- **`src/notifier.ts`**: sends one email to the customer, template `subscription-paused`, with `data: { resumeOn }`.

**Tests added**
- **State**: a new subscription has no resume date; pausing an active one works; pausing does nothing when past due, canceled or already paused; payment events leave a paused subscription unchanged; cancelling a paused one clears the date.
- **Audit**: your example line, plus a reason containing quotes.
- **Notifications**: only the customer gets the email.

**Things to know**
- A plan change still goes through while a subscription is paused. You didn't say how that should work, so I left it unchanged.
- `resumeOn` is stored exactly as given. Nothing checks that it's a valid `YYYY-MM-DD` date or that it's in the future.
- Nothing is committed yet.