I've added the `subscription_paused` event as you described, with tests. All 20 tests pass (13 old, 7 new) and the type check is clean. It's committed on `main` as `3f9b99d`, but not pushed because the repo has no remote.

**What changed**
- **Event** (`src/events.ts`): the new event carries `resumeOn` (a `YYYY-MM-DD` string) and `reason`.
- **State** (`src/subscription.ts`):
  - The new `paused` status applies only to an active subscription; pausing in any other status, including already paused, changes nothing.
  - The subscription now has a `resumeOn` field: the resume date while paused, `null` otherwise.
  - A paused subscription ignores failed payments. Recoveries already only applied to past-due subscriptions, so they needed no change.
  - Cancelling a paused subscription works as usual and clears `resumeOn`.
- **Audit log** (`src/audit.ts`): lines look like `… subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way as for cancellations.
- **Notifications** (`src/notifier.ts`): only the customer is notified, with a `subscription-paused` email carrying `resumeOn`.

**Decisions for you**
- **Plan changes while paused** still apply, since the spec doesn't mention them. If a paused subscription should keep its plan, that's a one-line guard.
- **Resume date format:** `resumeOn` is a plain string, and the code doesn't check that it really is `YYYY-MM-DD`. The other event fields aren't checked either, so I left it that way. A dedicated date type checked where events come in would make bad dates impossible.

**Log**
1. Read every file and ran the tests and type check first: 13/13 passing, no type errors.
2. Wrote the 7 tests before any code. All of them failed because the event wasn't handled yet, which was the expected reason.
3. Added the event type and let the compiler list the three places that had to handle it.
4. Added the audit and notification cases, and those tests passed.
5. Added the subscription changes, and all 20 tests passed.
6. My edit script had saved the files with Windows line endings, so I switched them back to the repo's Unix ones to keep the diff clean, then re-ran the tests and type check.
7. Made one commit, because the code doesn't compile until all three places handle the new event.

The skill mentions crapper, dryer and mutator tools, but none were available here, so I didn't run them. Instead I checked each new rule against the tests by hand: the payment guard while paused, the "only active can pause" rule, and clearing `resumeOn` on cancel each have a test that would fail if the rule were removed. Everything new is small and has no duplicated code.