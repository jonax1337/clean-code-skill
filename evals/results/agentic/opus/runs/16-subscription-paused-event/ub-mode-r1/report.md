I added the `subscription_paused` event and its tests. All 20 tests pass (13 old, 7 new) and the type check is clean. It's committed on `main` as `7b51b17`, but not pushed, because the repo has no remote set up.

**How it behaves**
- **Event:** `subscription_paused` carries `resumeOn` (`YYYY-MM-DD`) and a free-text `reason`, defined in `src/events.ts`.
- **State** (`src/subscription.ts`):
  - There's a new `paused` status, and the subscription now has a `resumeOn` field, which is `null` from the start.
  - Only an active subscription can be paused. Past-due, cancelled or already-paused ones are left unchanged.
  - A failed payment leaves a paused subscription as it is. A recovered payment already only acted on past-due subscriptions, so it needed no change.
  - Cancelling sets `resumeOn` back to `null`.
- **Audit log** (`src/audit.ts`): lines look like `… subscription_paused resumeOn=2025-05-01 reason="vacation"`, with the reason quoted the same way as cancellations.
- **Notifications** (`src/notifier.ts`): the customer gets a `subscription-paused` email with `{ resumeOn }`. Nobody else is notified.

Resuming is left out, as you asked.

**Decisions worth knowing**
- I kept `Subscription` as a flat object with `resumeOn: string | null` instead of a type that only allows a date while paused. That would have changed the shape of an exported type for every consumer. The "null unless paused" rule is enforced by the state logic and covered by tests, not by the type checker.
- `resumeOn` is a plain string, and nothing checks the date format. This repo never validates incoming data, so there was no existing place to put a check. If events come from outside, the `YYYY-MM-DD` check belongs wherever they are first read in.
- The skill calls for crapper, dryer and mutator tools, but none of them are in this repo or the skill folder, so I didn't run them. Instead I checked by hand that each new rule is tested: removing the pause guard on failed payments, the `resumeOn` reset on cancel, or the active-only check makes a test fail.

**Log**
1. Read all the source, tests and README. The baseline was 13/13 passing with a clean type check.
2. Wrote 7 tests first (1 audit, 1 notification, 5 state). They failed for the expected reasons: the event wasn't handled and `resumeOn` didn't exist.
3. Typed the test's `paused` fixture as the specific pause event so overriding `resumeOn` in a test would compile.
4. Added the event type and the handling in the three places that use events. Result: 20/20 passing and a clean type check.
5. My edit had switched `test/subscription.test.ts` from Windows to Unix line endings, which made every line show as changed. I switched it back so the diff only shows real changes, then re-ran the tests.
6. Committed with a message that explains why, what changed and how it was checked.