`subscription_paused` is in place across state, audit, and notifications, with tests. All 19 tests pass (13 existing, 6 new) and typecheck is clean. I haven't committed anything, since you didn't ask for a commit.

**Changes**

- **`src/events.ts`**: new `SubscriptionPaused` event with `resumeOn` and `reason`, added to the union.
- **`src/subscription.ts`**:
  - `paused` is a new status, and `resumeOn: string | null` is a new field, set to `null` on start.
  - A pause applies only to an active subscription. Any other status is returned unchanged.
  - Failed payments leave a paused subscription unchanged.
  - Cancelling clears `resumeOn`.
  - Payment recovery needs no change, because it already only acts on `past_due`.
- **`src/audit.ts`**: writes `resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way as the cancellation reason.
- **`src/notifier.ts`**: one customer email, `subscription-paused`, with `data: { resumeOn }`.
- **Tests**: one each for the audit line and the email. In `subscription.test.ts`, four new tests cover the pause, the active-only rule, payment events being ignored while paused, and cancel clearing `resumeOn`. The first test now also checks that `resumeOn` starts as `null`.

I wrote the tests first and ran them against the unchanged code. All seven failed for the expected reasons: the event was unhandled, or `resumeOn` was missing.

**Choices I made**

- `reason` is in the audit line but not in the email data, because the spec only asked for `resumeOn` there. Adding it would be one line in `notifier.ts`.
- `resumeOn` is stored as a plain string with no date validation, the same as `occurredAt`. The code has no entry-point parser to put a check in.
- `plan_changed` on a paused subscription still changes the plan. The spec didn't cover this.
- I followed the existing flat-field style (`resumeOn: string | null`) rather than a union type that would make illegal states impossible.

**Not done**

- I didn't run the `crapper`, `dryer`, or `mutator` tools from the ub-mode skill. None of them are in the repo or its dependencies. I checked the new tests by reading them against each rule instead.
- The skill asks for small commits and a push to `main`. Your harness rules only allow commits and pushes when you ask, so I left the seven modified files uncommitted. Tell me if you want them committed, and how you want them split.