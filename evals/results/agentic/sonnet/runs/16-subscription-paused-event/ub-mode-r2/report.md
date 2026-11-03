I added the `subscription_paused` event; all 19 tests pass and the typecheck is clean. I haven't committed anything. I wrote the tests alongside the code and never ran them before the change, so I didn't see them fail first.

- **State:** an active subscription becomes `paused` and stores `resumeOn`. `resumeOn` is `null` in every other state. Pausing from any other status changes nothing, including a second pause on an already-paused subscription. Payment events leave a paused subscription as it is. For `payment_failed` I had to add an explicit check, because it would otherwise have turned a paused subscription into `past_due`. Cancelling a paused subscription works as usual and clears `resumeOn`.
- **Audit log:** the line reads `… sub_9 subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way as the cancellation reason.
- **Notifications:** the customer gets a `subscription-paused` email with `resumeOn`. Nobody else is notified.
- **Export:** I also exported the `SubscriptionPaused` type from `src/index.ts`.

Resuming is left out, as you asked. As things stand, nothing in the code moves a subscription out of `paused` except cancelling it.

I added tests for the new behaviour in `test/subscription.test.ts`, `test/audit.test.ts` and `test/notifier.test.ts`.

The skill's complexity, duplication and mutation-testing steps (the crapper, dryer and mutator tools) weren't run, since I didn't have those tools available here. The change adds only small branches.