The `subscription_paused` event is in and committed on `main` as 165c73e. I did not push it. All 19 tests pass (the new ones included) and the typecheck is clean. I didn't run the crapper, dryer or mutator tools from the skill.

- **State:** an active subscription becomes `paused` and stores `resumeOn`. `resumeOn` is `null` in every other status. The event does nothing in any status other than active, so a second pause does not change the resume date.
- **Payments:** a failed payment now leaves a paused subscription alone. A recovery already only affected `past_due`, so it needed no change.
- **Cancelling:** cancelling a paused subscription works as usual and sets `resumeOn` back to `null`.
- **Audit log:** the line matches your example: `... subscription_paused resumeOn=2025-05-01 reason="vacation"`. The reason is quoted the same way as the cancellation reason.
- **Notifications:** only the customer is notified, with a `subscription-paused` email that carries `resumeOn`.
- **Tests:** new tests cover all of the above in `test/subscription.test.ts`, `test/audit.test.ts` and `test/notifier.test.ts`.

I did not add the `SubscriptionPaused` type to the exports in `src/index.ts`, because that file only exports the union and `Plan`. I added a README line saying resuming is not built yet, and I left resuming out as you asked.

I didn't write the tests before the code, so I never saw them fail first.